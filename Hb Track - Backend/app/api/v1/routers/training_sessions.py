"""
Router para sessões de treino (Training Sessions).

FASE 5 - Implementação completa.

Regras aplicáveis:
- R18: Treinos são eventos operacionais, editáveis dentro dos limites do sistema.
- R22: Dados de treino são métricas operacionais e não substituem estatísticas primárias de jogo.
- R40: Limite temporal de edição (10min autor; até 24h perfil superior; >24h somente leitura).
- R25/R26: Permissões por papel e escopo.
- RF5.2: Temporada interrompida bloqueia criação/edição.
- R29/R33: Sem DELETE físico; histórico com rastro.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.auth import get_current_context, require_role
from app.core.cache import invalidate_report_cache
from app.core.exceptions import ValidationError
from app.core.decorators import scoped_endpoint
from app.core.context import ExecutionContext
from app.core.db import get_async_db, get_db
from app.core.permissions import require_team_scope
from app.models.training_session import TrainingSession as TrainingSessionModel
from app.schemas.training_sessions import (
    TrainingSession,
    TrainingSessionCreate,
    ScopedTrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingSessionPaginatedResponse,
    SessionClosureResponse,
    TrainingSessionScheduleRequest,
    TrainingSessionFinalizeRequest,
)
from app.schemas.wellness import (
    WellnessStatusResponse,
    WellnessAthleteData,
    WellnessSessionStats,
    WellnessPreData,
    WellnessPostData,
)
from app.schemas.error import ErrorResponse
from app.services.training_session_service import TrainingSessionService

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["training-sessions"],
)
scoped_router = APIRouter(
    prefix="/teams/{team_id}/trainings",
    tags=["training-sessions"],
)


async def _require_team_scope_async(team_id: UUID, ctx: ExecutionContext, db: AsyncSession):
    """Versão async de require_team_scope para usar com AsyncSession"""
    from app.models.team import Team
    from app.schemas.error import ErrorCode
    
    if ctx.is_superadmin:
        team = await db.get(Team, str(team_id))
        return team

    team = await db.get(Team, str(team_id))
    if not team or getattr(team, "deleted_at", None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.RESOURCE_NOT_FOUND.value,
                "message": "Equipe não encontrada",
            },
        )

    if str(team.organization_id) != str(ctx.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": ErrorCode.ORGANIZATION_SCOPE_VIOLATION.value,
                "message": "Equipe fora do contexto da organização",
                "constraint": "R34",
                "team_id": str(team_id),
                "team_org_id": str(team.organization_id),
                "context_org_id": str(ctx.organization_id),
            },
        )

    return team


async def _ensure_team(db: AsyncSession, ctx: ExecutionContext, team_id: UUID):
    team = await _require_team_scope_async(team_id, ctx, db)
    if not team:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="team_not_found")
    return team


async def _get_training_scoped(
    db: AsyncSession,
    ctx: ExecutionContext,
    team_id: UUID,
    training_id: UUID,
    include_deleted: bool = False,
) -> TrainingSessionModel:
    """
    Garante que a sessao pertence ao time do path e, se aplicavel, a mesma org do contexto.
    
    Args:
        include_deleted: Se True, inclui registros soft-deleted (útil para restore)
    """
    await _ensure_team(db, ctx, team_id)

    stmt = select(TrainingSessionModel).where(
        TrainingSessionModel.id == training_id,
        TrainingSessionModel.team_id == team_id,
    )
    if not include_deleted:
        stmt = stmt.where(TrainingSessionModel.deleted_at.is_(None))
    if not ctx.is_superadmin:
        stmt = stmt.where(TrainingSessionModel.organization_id == ctx.organization_id)

    training = await db.scalar(stmt)
    if not training:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="training_session_not_found")
    return training


@router.get(
    "",
    response_model=TrainingSessionPaginatedResponse,
    summary="Lista sessões de treino",
    responses={
        200: {"description": "Lista paginada de sessões"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
@scoped_endpoint("can_view_training_schedule")
async def list_training_sessions(
    team_id: Optional[UUID] = Query(None, description="Filtrar por time"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=50, ge=1, le=100, description="Itens por página"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Lista paginada de sessões de treino.

    **Regras**: R25/R26 (permissões por papel)
    - Ref: RDB14 - Paginação padrão

    **Filtros disponíveis:**
    - team_id: Filtrar por time
    - season_id: Filtrar por temporada
    - start_date/end_date: Filtros de data
    """
    service = TrainingSessionService(db, ctx)
    sessions, total = await service.get_all(
        team_id=team_id,
        season_id=season_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=limit,
    )

    pages = (total + limit - 1) // limit if total > 0 else 0

    return TrainingSessionPaginatedResponse(
        items=sessions,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.post(
    "",
    response_model=TrainingSession,
    status_code=status.HTTP_201_CREATED,
    summary="Cria sessão de treino",
    responses={
        201: {"description": "Sessão criada com sucesso"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
        404: {"description": "Time não encontrado", "model": ErrorResponse},
    },
)
async def create_training_session(
    payload: TrainingSessionCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente", "coordenador", "treinador"])),
):
    """
    Cria uma nova sessão de treino (evento operacional).

    **Regras**:
    - R18: Treinos são eventos operacionais.
    - R22: Métricas operacionais, não substituem estatísticas de jogo.
    - R25/R26: Permissões por papel e escopo.
    - Step 2: Validação de permissão can_create_training
    """
    # Step 2: Validar permissão can_create_training
    context.requires("can_create_training")
    
    service = TrainingSessionService(db, context)
    session = await service.create(payload)
    await db.commit()
    invalidate_report_cache()
    await db.refresh(session)

    return TrainingSession.model_validate(session)


@router.get(
    "/{training_session_id}",
    response_model=TrainingSession,
    summary="Obtém sessão de treino por ID",
    responses={
        200: {"description": "Detalhes da sessão"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
    },
)
@scoped_endpoint("can_view_training_schedule")
async def get_training_session_by_id(
    training_session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Retorna detalhes de uma sessão de treino específica.

    **Regras**: R25/R26 (permissões por papel e escopo).
    """
    service = TrainingSessionService(db, ctx)
    session = await service.get_by_id(training_session_id)

    return TrainingSession.model_validate(session)


@router.patch(
    "/{training_session_id}",
    response_model=TrainingSession,
    summary="Atualiza sessão de treino",
    responses={
        200: {"description": "Sessão atualizada com sucesso"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Janela de edição expirada (R40)", "model": ErrorResponse},
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
    },
)
async def update_training_session(
    training_session_id: UUID,
    payload: TrainingSessionUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente", "coordenador", "treinador"])),
):
    """
    Atualiza campos editáveis de uma sessão de treino.

    **Regras de edição (R40)**:
    - ≤10 minutos: autor pode editar livremente.
    - >10 min e ≤24h: exige perfil superior (admin/coordinator).
    - >24h: exige admin_note obrigatório para justificar edição tardia.

    **Outras regras**:
    - R25/R26: Permissões por papel e escopo.
    """
    service = TrainingSessionService(db, context)
    session = await service.update(training_session_id, payload)
    await db.commit()
    invalidate_report_cache()
    await db.refresh(session)

    return TrainingSession.model_validate(session)


@router.delete(
    "/{training_session_id}",
    response_model=TrainingSession,
    summary="Exclui sessão de treino",
    responses={
        200: {"description": "Sessão excluída (soft delete)"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
    },
)
async def delete_training_session(
    training_session_id: UUID,
    reason: str = Query(..., min_length=5, description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente", "coordenador", "treinador"])),
):
    """
    Soft delete de sessão de treino.
    
    **Regras**:
    - R29/R33: Sem DELETE físico, histórico com rastro
    - RDB3: Soft delete com deleted_at e deleted_reason
    """
    service = TrainingSessionService(db, context)
    session = await service.soft_delete(training_session_id, reason)
    await db.commit()
    invalidate_report_cache()
    await db.refresh(session)

    return TrainingSession.model_validate(session)


@router.post(
    "/{training_session_id}/restore",
    response_model=TrainingSession,
    summary="Restaura sessão de treino",
    responses={
        200: {"description": "Sessão restaurada"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
        422: {"description": "Sessão não está excluída", "model": ErrorResponse},
    },
)
async def restore_training_session(
    training_session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["dirigente", "coordenador", "treinador"])),
):
    """
    Restaura sessão de treino excluída.
    
    **Regras**: RDB3 - Restore via nullify de deleted_at
    """
    service = TrainingSessionService(db, context)
    session = await service.restore(training_session_id)
    await db.commit()
    invalidate_report_cache()
    await db.refresh(session)

    return TrainingSession.model_validate(session)



# =============================================================================
# Rotas canonicas com escopo de equipe (/teams/{team_id}/trainings)
# =============================================================================

@scoped_router.get(
    "",
    response_model=TrainingSessionPaginatedResponse,
    summary="Listar sessoes de treino (escopo equipe)",
    responses={403: {"model": ErrorResponse}},
)
@scoped_endpoint("can_view_training_schedule", scope="team", require_org=True)
async def scoped_list_training_sessions(
    team_id: UUID,
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    page: int = Query(default=1, ge=1, description="Numero da pagina"),
    limit: int = Query(default=50, ge=1, le=100, description="Itens por pagina"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> TrainingSessionPaginatedResponse:
    await _ensure_team(db, ctx, team_id)

    stmt = select(TrainingSessionModel).where(
        TrainingSessionModel.team_id == team_id,
        TrainingSessionModel.deleted_at.is_(None),
    )
    if not ctx.is_superadmin:
        stmt = stmt.where(TrainingSessionModel.organization_id == ctx.organization_id)
    if season_id:
        stmt = stmt.where(TrainingSessionModel.season_id == season_id)
    if start_date:
        stmt = stmt.where(TrainingSessionModel.session_at >= start_date)
    if end_date:
        stmt = stmt.where(TrainingSessionModel.session_at <= end_date)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.order_by(TrainingSessionModel.session_at.desc()).offset((page - 1) * limit).limit(limit)
    items = list(await db.scalars(stmt))

    pages = (total + limit - 1) // limit if total else 0
    return TrainingSessionPaginatedResponse(
        items=[TrainingSession.model_validate(s) for s in items],
        total=total or 0,
        page=page,
        limit=limit,
    )


@scoped_router.post(
    "",
    response_model=TrainingSession,
    status_code=status.HTTP_201_CREATED,
    summary="Criar sessao de treino (escopo equipe)",
    responses={403: {"model": ErrorResponse}},
)
async def scoped_create_training_session(
    team_id: UUID,
    payload: ScopedTrainingSessionCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente", "coordenador", "treinador"], require_team=True)),
) -> TrainingSession:
    team = await _ensure_team(db, ctx, team_id)

    org_id = team.organization_id
    if not ctx.is_superadmin and payload.organization_id and str(payload.organization_id) != str(org_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="organization_scope_mismatch")
    if not ctx.membership_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="membership_required")

    session = TrainingSessionModel(
        organization_id=org_id,
        team_id=team_id,
        season_id=getattr(payload, "season_id", None),
        session_at=payload.session_at,
        session_type=getattr(payload, "session_type", "quadra"),  # Default: quadra
        created_by_user_id=ctx.user_id,  # Preenche com usuário autenticado
        main_objective=getattr(payload, "main_objective", None),
        planned_load=getattr(payload, "planned_load", None),
        group_climate=getattr(payload, "group_climate", None),
        # Campos de foco (percentuais 0-100)
        focus_attack_positional_pct=getattr(payload, "focus_attack_positional_pct", None),
        focus_defense_positional_pct=getattr(payload, "focus_defense_positional_pct", None),
        focus_transition_offense_pct=getattr(payload, "focus_transition_offense_pct", None),
        focus_transition_defense_pct=getattr(payload, "focus_transition_defense_pct", None),
        focus_attack_technical_pct=getattr(payload, "focus_attack_technical_pct", None),
        focus_defense_technical_pct=getattr(payload, "focus_defense_technical_pct", None),
        focus_physical_pct=getattr(payload, "focus_physical_pct", None),
    )
    db.add(session)
    await db.commit()
    invalidate_report_cache()
    await db.refresh(session)
    return TrainingSession.model_validate(session)


@scoped_router.get(
    "/{training_id}",
    response_model=TrainingSession,
    summary="Detalhar sessao de treino (escopo equipe)",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
@scoped_endpoint("can_view_training_schedule", scope="team", require_org=True)
async def scoped_get_training_session(
    team_id: UUID,
    training_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> TrainingSession:
    training = await _get_training_scoped(db, ctx, team_id, training_id)
    return TrainingSession.model_validate(training)


@scoped_router.patch(
    "/{training_id}",
    response_model=TrainingSession,
    summary="Atualizar sessao de treino (escopo equipe)",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def scoped_update_training_session(
    team_id: UUID,
    training_id: UUID,
    payload: TrainingSessionUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente", "coordenador", "treinador"], require_team=True)),
) -> TrainingSession:
    training = await _get_training_scoped(db, ctx, team_id, training_id)

    # Atualizar campos básicos
    if payload.session_at is not None:
        training.session_at = payload.session_at
    if payload.main_objective is not None:
        training.main_objective = payload.main_objective
    if payload.planned_load is not None:
        training.planned_load = payload.planned_load
    if payload.group_climate is not None:
        training.group_climate = payload.group_climate
    
    # Atualizar campos de foco (se fornecidos)
    if payload.focus_attack_positional_pct is not None:
        training.focus_attack_positional_pct = payload.focus_attack_positional_pct
    if payload.focus_defense_positional_pct is not None:
        training.focus_defense_positional_pct = payload.focus_defense_positional_pct
    if payload.focus_transition_offense_pct is not None:
        training.focus_transition_offense_pct = payload.focus_transition_offense_pct
    if payload.focus_transition_defense_pct is not None:
        training.focus_transition_defense_pct = payload.focus_transition_defense_pct
    if payload.focus_attack_technical_pct is not None:
        training.focus_attack_technical_pct = payload.focus_attack_technical_pct
    if payload.focus_defense_technical_pct is not None:
        training.focus_defense_technical_pct = payload.focus_defense_technical_pct
    if payload.focus_physical_pct is not None:
        training.focus_physical_pct = payload.focus_physical_pct

    await db.commit()
    invalidate_report_cache()
    await db.refresh(training)
    return TrainingSession.model_validate(training)


@scoped_router.delete(
    "/{training_id}",
    response_model=TrainingSession,
    summary="Excluir sessao de treino (escopo equipe)",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def scoped_delete_training_session(
    team_id: UUID,
    training_id: UUID,
    reason: str = Query(..., min_length=5, description="Motivo da exclusao"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente", "coordenador"], require_team=True)),
) -> TrainingSession:
    training = await _get_training_scoped(db, ctx, team_id, training_id)
    training.deleted_at = datetime.now(timezone.utc)
    training.deleted_reason = reason
    await db.commit()
    invalidate_report_cache()
    await db.refresh(training)
    return TrainingSession.model_validate(training)


@scoped_router.post(
    "/{training_id}/restore",
    response_model=TrainingSession,
    summary="Restaurar sessao de treino (escopo equipe)",
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def scoped_restore_training_session(
    team_id: UUID,
    training_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["dirigente", "coordenador"], require_team=True)),
) -> TrainingSession:
    # include_deleted=True para encontrar registros soft-deleted
    training = await _get_training_scoped(db, ctx, team_id, training_id, include_deleted=True)
    if training.deleted_at is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="training_session_not_deleted")
    training.deleted_at = None
    training.deleted_reason = None
    await db.commit()
    invalidate_report_cache()
    await db.refresh(training)
    return TrainingSession.model_validate(training)


# =============================================================================
# Novos endpoints (TRAINNIG.MD) - Fechamento e Desvios
# =============================================================================

@router.post(
    "/{training_session_id}/schedule",
    response_model=TrainingSession,
    summary="Agenda sessão completa (draft → scheduled)",
    description="Valida campos mínimos e agenda a sessão para execução automática",
    responses={
        200: {"description": "Sessão agendada com sucesso"},
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
        422: {"description": "Dados incompletos", "model": ErrorResponse},
    },
)
async def schedule_training_session(
    training_session_id: UUID,
    request_data: TrainingSessionScheduleRequest,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["dirigente", "coordenador", "treinador"])),
):
    """
    Agenda uma sessão completa (draft → scheduled).

    **Campos mínimos obrigatórios:**
    - session_at
    - duration_planned_minutes
    - location
    - session_type
    - main_objective
    """
    service = TrainingSessionService(db, context)

    try:
        session, errors = await service.schedule_session(
            training_session_id,
            request_data.starts_at,
            request_data.ends_at,
        )
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_code": "INCOMPLETE_SCHEDULE",
                    "message": "Sessão incompleta para agendamento",
                    "field_errors": errors,
                },
            )

        await db.commit()
        invalidate_report_cache()
        await db.refresh(session)

        return TrainingSession.model_validate(session)
    except ValidationError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "INVALID_STATUS",
                "message": str(e),
            },
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error scheduling training session {training_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling training session: {str(e)}"
        )

@router.post(
    "/{training_session_id}/finalize",
    response_model=SessionClosureResponse,
    summary="Finaliza revisão operacional e congela a sessão",
    description="Finaliza a revisão operacional (pending_review → readonly) com validações bloqueantes",
    responses={
        200: {
            "description": "Resposta de finalização (success=True se finalizou, False com validation se falhou)",
            "model": SessionClosureResponse
        },
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def finalize_training_session(
    training_session_id: UUID,
    request_data: TrainingSessionFinalizeRequest,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["dirigente", "coordenador", "treinador"])),
):
    """
    Finaliza revisão operacional (pending_review → readonly).

    **Validações Bloqueantes:**
    - Status deve ser 'pending_review'
    - execution_outcome e campos condicionais
    - Justificativa obrigatória se execução != on_time
    - Presenças completas (exceto cancelado)

    **Ações ao finalizar:**
    - Atualiza status para 'readonly'
    - Registra post_review_completed_at/by e closed_at/by
    - Ajusta ended_at com duração real (se informada)
    - Define planning_deviation_flag quando execução != on_time

    Requer permissão: dirigente, coordenador ou treinador
    """
    service = TrainingSessionService(db, context)

    try:
        result = await service.finalize_session(
            training_session_id,
            attendance_completed=request_data.attendance_completed,
            review_completed=request_data.review_completed,
        )
        
        if result.success:
            await db.commit()
            invalidate_report_cache()
            logger.info(
                f"Training session {training_session_id} review finalized by user {context.user_id}"
            )
        else:
            # Não faz rollback porque validação não altera dados
            logger.warning(
                f"Training session {training_session_id} validation failed: {result.validation.error_code}"
            )
        
        return result
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error finalizing training session {training_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finalizing training session: {str(e)}"
        )



@router.get(
    "/{training_session_id}/deviation",
    response_model=dict,
    summary="Análise de desvio (planejado vs executado)",
    description="Calcula desvio entre focos planejados (microciclo) e executados (sessão)",
    responses={
        200: {"description": "Análise de desvio"},
        404: {"description": "Sessão não encontrada ou sem microciclo", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
async def get_session_deviation(
    training_session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(permission_dep(["coach", "admin"])),
):
    """
    Calcula desvio entre planejado e executado.

    **Regras (TRAINNIG.MD):**
    - Desvio absoluto ≥ 20 pontos percentuais em QUALQUER foco OU
    - Desvio agregado ≥ 30% (soma dos absolutos)

    **Retorna:**
    - Desvios por foco (executado - planejado)
    - Desvio total agregado
    - Flag de significância
    - Mensagem explicativa
    - Sugestões (futuro - FASE 4)

    **Nota:** Retorna 404 se sessão não tem microciclo vinculado.

    Requer permissão: coach ou admin
    """
    service = TrainingSessionService(db, context)

    try:
        deviation = await service.calculate_deviation(training_session_id)

        if not deviation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session has no microcycle linked or not found"
            )

        logger.info(
            f"Retrieved deviation analysis for training session {training_session_id} "
            f"(significant: {deviation.get('is_significant_deviation')}) "
            f"by user {context.user_id}"
        )

        return deviation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating deviation for session {training_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training session not found: {str(e)}"
        )


@router.post(
    "/{training_session_id}/duplicate",
    response_model=TrainingSession,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicar sessão de treino",
    description="Cria uma cópia de uma sessão existente com status draft",
    responses={
        201: {"description": "Sessão duplicada criada"},
        400: {"description": "Sessão muito antiga (>60 dias) ou já deletada", "model": ErrorResponse},
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
@scoped_endpoint("can_create_training")
async def duplicate_training_session(
    training_session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Duplica uma sessão de treino existente.

    **Comportamento:**
    - Cria nova sessão com status 'draft'
    - Copia: title, description, session_type, location, duration_minutes, focus_* (7 focos)
    - Mantém: team_id, organization_id
    - NÃO copia: session_at (usuário define), attendance, wellness, exercises
    - Validação: bloqueia duplicação de sessões >60 dias (apenas leitura)

    **Regras:**
    - R40: Sessões >60 dias são readonly
    - R25/R26: Permissões por papel (can_create_training)

    Requer permissão: can_create_training
    """
    service = TrainingSessionService(db, ctx)

    try:
        # Buscar sessão original
        original = await db.get(TrainingSessionModel, str(training_session_id))
        if not original or original.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found or deleted"
            )

        # Validar >60 dias (readonly)
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        sixty_days_ago = now - timedelta(days=60)
        
        if original.session_at < sixty_days_ago:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "SESSION_READONLY",
                    "message": "Sessões com mais de 60 dias não podem ser duplicadas (readonly)",
                    "session_at": original.session_at.isoformat(),
                    "constraint": "R40"
                }
            )

        # Criar payload de duplicação
        duplicate_data = TrainingSessionCreate(
            team_id=original.team_id,
            title=f"{original.title} (Cópia)",
            description=original.description,
            session_type=original.session_type,
            session_at=now,  # Usuário ajustará depois
            location=original.location,
            duration_minutes=original.duration_minutes,
            focus_attack_pct=original.focus_attack_pct,
            focus_defense_pct=original.focus_defense_pct,
            focus_physical_pct=original.focus_physical_pct,
            focus_technical_pct=original.focus_technical_pct,
            focus_tactical_pct=original.focus_tactical_pct,
            focus_transition_pct=original.focus_transition_pct,
            focus_goalkeeper_pct=original.focus_goalkeeper_pct,
            status="draft",
            training_microcycle_id=original.training_microcycle_id,
        )

        # Criar duplicata
        duplicated = await service.create_session(duplicate_data)

        logger.info(
            f"Duplicated training session {training_session_id} -> {duplicated.id} "
            f"by user {ctx.user_id}"
        )

        return duplicated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating session {training_session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate session: {str(e)}"
        )


@router.get(
    "/{training_session_id}/wellness-status",
    response_model=WellnessStatusResponse,
    summary="Status de wellness da sessão",
    description="Retorna status de wellness de todos atletas da sessão para dashboard do treinador",
    responses={
        200: {"description": "Status de wellness da sessão"},
        404: {"description": "Sessão não encontrada", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
@scoped_endpoint("can_view_training_schedule")
async def get_wellness_status(
    training_session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Retorna status de wellness para todos os atletas de uma sessão.

    **Dados retornados por atleta:**
    - Status: complete (pre+post), partial (só pre), none, absent
    - Dados de wellness pré e pós (se preenchidos)
    - Taxa de resposta mensal e badge de comprometimento

    **Estatísticas agregadas:**
    - Total de atletas, responderam pré/pós
    - Médias de fadiga, stress, prontidão, RPE
    - Alertas se métricas fora do normal

    Requer permissão: can_view_training_schedule
    """
    from app.models.wellness_pre import WellnessPre
    from app.models.wellness_post import WellnessPost
    from app.models.athlete import Athlete
    from app.models.attendance import Attendance

    # Buscar sessão
    session = await db.get(TrainingSessionModel, str(training_session_id))
    if not session or session.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )

    # Buscar attendance (presença) dos atletas
    attendance_stmt = select(Attendance).where(
        Attendance.training_session_id == training_session_id,
        Attendance.deleted_at.is_(None)
    )
    attendance_result = await db.execute(attendance_stmt)
    attendances = {str(a.athlete_id): a for a in attendance_result.scalars().all()}

    # Buscar wellness pre
    wellness_pre_stmt = select(WellnessPre).where(
        WellnessPre.training_session_id == training_session_id,
        WellnessPre.deleted_at.is_(None)
    )
    wellness_pre_result = await db.execute(wellness_pre_stmt)
    wellness_pres = {str(wp.athlete_id): wp for wp in wellness_pre_result.scalars().all()}

    # Buscar wellness post
    wellness_post_stmt = select(WellnessPost).where(
        WellnessPost.training_session_id == training_session_id,
        WellnessPost.deleted_at.is_(None)
    )
    wellness_post_result = await db.execute(wellness_post_stmt)
    wellness_posts = {str(wp.athlete_id): wp for wp in wellness_post_result.scalars().all()}

    # Buscar atletas da equipe
    from app.models.team_registration import TeamRegistration
    athletes_stmt = select(Athlete).join(
        TeamRegistration,
        and_(
            TeamRegistration.athlete_id == Athlete.id,
            TeamRegistration.team_id == session.team_id,
            TeamRegistration.end_at.is_(None),  # Vínculo ativo
            TeamRegistration.deleted_at.is_(None)
        )
    ).where(
        Athlete.deleted_at.is_(None),
        Athlete.state == 'ativa'
    )
    athletes_result = await db.execute(athletes_stmt)
    athletes = athletes_result.scalars().all()

    # Construir lista de atletas com status
    athletes_data: list[WellnessAthleteData] = []
    fatigue_values = []
    stress_values = []
    readiness_values = []
    rpe_values = []
    load_values = []

    for athlete in athletes:
        athlete_id_str = str(athlete.id)
        attendance = attendances.get(athlete_id_str)
        wellness_pre = wellness_pres.get(athlete_id_str)
        wellness_post = wellness_posts.get(athlete_id_str)

        # Verificar se está ausente
        is_absent = attendance is not None and attendance.presence_status == 'absent'
        has_pre = wellness_pre is not None
        has_post = wellness_post is not None

        # Determinar status
        if is_absent:
            status_value = 'absent'
        elif has_pre and has_post:
            status_value = 'complete'
        elif has_pre:
            status_value = 'partial'
        else:
            status_value = 'none'

        # Dados de wellness pre
        wellness_pre_data = None
        if wellness_pre:
            wellness_pre_data = WellnessPreData(
                fatigue_level=wellness_pre.fatigue_pre,
                stress_level=wellness_pre.stress_level,
                readiness=wellness_pre.readiness_score,
                filled_at=wellness_pre.filled_at
            )
            fatigue_values.append(wellness_pre.fatigue_pre)
            stress_values.append(wellness_pre.stress_level)
            if wellness_pre.readiness_score:
                readiness_values.append(wellness_pre.readiness_score)

        # Dados de wellness post
        wellness_post_data = None
        if wellness_post:
            wellness_post_data = WellnessPostData(
                session_rpe=wellness_post.session_rpe,
                internal_load=float(wellness_post.internal_load) if wellness_post.internal_load else None,
                fatigue_after=wellness_post.fatigue_after,
                filled_at=wellness_post.filled_at
            )
            rpe_values.append(wellness_post.session_rpe)
            if wellness_post.internal_load:
                load_values.append(float(wellness_post.internal_load))

        athletes_data.append(WellnessAthleteData(
            athlete_id=athlete.id,
            athlete_name=athlete.athlete_name,
            athlete_nickname=athlete.athlete_nickname,
            position=None,  # TODO: buscar posição
            status=status_value,
            has_wellness_pre=has_pre,
            has_wellness_post=has_post,
            is_absent=is_absent,
            monthly_response_rate=0.0,  # TODO: calcular taxa mensal
            has_monthly_badge=False,
            reminders_sent_count=0,
            wellness_pre=wellness_pre_data,
            wellness_post=wellness_post_data
        ))

    # Calcular estatísticas
    total_present = len([a for a in athletes_data if not a.is_absent])
    responded_pre = len(wellness_pres)
    responded_post = len(wellness_posts)

    avg_fatigue = sum(fatigue_values) / len(fatigue_values) if fatigue_values else 0.0
    avg_stress = sum(stress_values) / len(stress_values) if stress_values else 0.0
    avg_readiness = sum(readiness_values) / len(readiness_values) if readiness_values else 0.0
    avg_rpe = sum(rpe_values) / len(rpe_values) if rpe_values else 0.0
    avg_load = sum(load_values) / len(load_values) if load_values else 0.0

    stats = WellnessSessionStats(
        total_athletes=total_present,
        responded_pre=responded_pre,
        responded_post=responded_post,
        response_rate_pre=(responded_pre / total_present * 100) if total_present > 0 else 0.0,
        response_rate_post=(responded_post / total_present * 100) if total_present > 0 else 0.0,
        avg_fatigue_pre=avg_fatigue,
        avg_stress_pre=avg_stress,
        avg_readiness_pre=avg_readiness,
        avg_rpe_post=avg_rpe,
        avg_internal_load_post=avg_load,
        has_high_fatigue_alert=avg_fatigue >= 7,
        has_high_stress_alert=avg_stress >= 7,
        has_low_readiness_alert=avg_readiness <= 4 and avg_readiness > 0,
        has_high_rpe_alert=avg_rpe >= 8
    )

    return WellnessStatusResponse(
        athletes=athletes_data,
        stats=stats
    )


@router.post(
    "/copy-week",
    response_model=list[TrainingSession],
    status_code=status.HTTP_201_CREATED,
    summary="Copiar semana de treinos",
    description="Cria cópias de todas as sessões de uma semana para outra data",
    responses={
        201: {"description": "Sessões da semana copiadas"},
        400: {"description": "Parâmetros inválidos ou validação de focos falhou", "model": ErrorResponse},
        404: {"description": "Sessões não encontradas", "model": ErrorResponse},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
    },
)
@scoped_endpoint("can_create_training")
async def copy_week_sessions(
    team_id: UUID = Query(..., description="ID do time"),
    source_week_start: datetime = Query(..., description="Data inicial da semana de origem"),
    target_week_start: datetime = Query(..., description="Data inicial da semana de destino"),
    validate_focus: bool = Query(True, description="Validar soma de focos = 100%"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Copia todas as sessões de uma semana para outra data.

    **Comportamento:**
    - Busca todas as sessões da semana de origem (7 dias)
    - Cria cópias ajustando session_at para semana de destino
    - Mantém offset de dias/horários (seg 10h -> seg 10h)
    - Validação opcional: soma de focos = 100% por sessão

    **Parâmetros:**
    - source_week_start: Data inicial da semana de origem (segunda-feira)
    - target_week_start: Data inicial da semana de destino (segunda-feira)
    - validate_focus: Se True, valida focos antes de criar

    **Validações:**
    - Soma de focus_* deve ser 100% (se validate_focus=True)
    - Sessões de origem devem existir
    - Não copia sessões >60 dias (readonly)

    **Regras:**
    - R40: Sessões >60 dias são readonly
    - R25/R26: Permissões por papel (can_create_training)

    Requer permissão: can_create_training
    """
    service = TrainingSessionService(db, ctx)

    try:
        from datetime import timedelta

        # Validar team_id no contexto
        await _ensure_team(db, ctx, team_id)

        # Buscar sessões da semana de origem
        week_end = source_week_start + timedelta(days=7)
        stmt = select(TrainingSessionModel).where(
            TrainingSessionModel.team_id == team_id,
            TrainingSessionModel.session_at >= source_week_start,
            TrainingSessionModel.session_at < week_end,
            TrainingSessionModel.deleted_at.is_(None),
        ).order_by(TrainingSessionModel.session_at)

        result = await db.execute(stmt)
        source_sessions = result.scalars().all()

        if not source_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No sessions found for week starting {source_week_start.date()}"
            )

        # Validar >60 dias (readonly)
        now = datetime.now(timezone.utc)
        sixty_days_ago = now - timedelta(days=60)
        readonly_sessions = [s for s in source_sessions if s.session_at < sixty_days_ago]
        
        if readonly_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "SESSION_READONLY",
                    "message": f"{len(readonly_sessions)} sessão(ões) com mais de 60 dias não podem ser copiadas (readonly)",
                    "constraint": "R40"
                }
            )

        # Criar cópias
        created_sessions = []
        offset = target_week_start - source_week_start

        for original in source_sessions:
            # Validar focos se solicitado
            if validate_focus:
                total_focus = sum([
                    original.focus_attack_pct or 0,
                    original.focus_defense_pct or 0,
                    original.focus_physical_pct or 0,
                    original.focus_technical_pct or 0,
                    original.focus_tactical_pct or 0,
                    original.focus_transition_pct or 0,
                    original.focus_goalkeeper_pct or 0,
                ])
                if total_focus != 100:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error_code": "INVALID_FOCUS_SUM",
                            "message": f"Sessão '{original.title}' tem soma de focos = {total_focus}% (esperado 100%)",
                            "session_id": str(original.id),
                            "total_focus": total_focus,
                        }
                    )

            # Ajustar data
            new_session_at = original.session_at + offset

            # Criar payload
            copy_data = TrainingSessionCreate(
                team_id=original.team_id,
                title=original.title,
                description=original.description,
                session_type=original.session_type,
                session_at=new_session_at,
                location=original.location,
                duration_minutes=original.duration_minutes,
                focus_attack_pct=original.focus_attack_pct,
                focus_defense_pct=original.focus_defense_pct,
                focus_physical_pct=original.focus_physical_pct,
                focus_technical_pct=original.focus_technical_pct,
                focus_tactical_pct=original.focus_tactical_pct,
                focus_transition_pct=original.focus_transition_pct,
                focus_goalkeeper_pct=original.focus_goalkeeper_pct,
                status="draft",
                training_microcycle_id=original.training_microcycle_id,
            )

            # Criar cópia
            copied = await service.create_session(copy_data)
            created_sessions.append(copied)

        logger.info(
            f"Copied week: {len(created_sessions)} sessions from {source_week_start.date()} "
            f"to {target_week_start.date()} for team {team_id} by user {ctx.user_id}"
        )

        return created_sessions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error copying week sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to copy week: {str(e)}"
        )
