"""
Router para presenças em sessões de treino (Attendance).

Regras aplicáveis:
- R22: Dados de treino são métricas operacionais.
- R40: Limite temporal de edição (10min autor; até 24h perfil superior; >24h somente leitura).
- R25/R26: Permissões por papel e escopo.
- RF5.2: Temporada interrompida bloqueia criação/edição.
- R37: Edição pós-encerramento apenas via ação administrativa auditada.
- R29/R33: Sem DELETE físico; histórico com rastro.

Constraints:
- UNIQUE (session_id, athlete_id): 1 presença por atleta por sessão.

Step 4 Implementado: Backend Attendance com Eager Loading (2026-01-16)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.core.db import AsyncSession, get_async_db
from app.core.auth import get_current_user
from app.core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    ConflictError
)
from app.core.context import ExecutionContext
from app.schemas.attendance import (
    Attendance,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceCorrection,
)
from sqlalchemy import text as sa_text
from app.services.attendance_service import AttendanceService
from app.services.training_pending_service import TrainingPendingService

router = APIRouter(tags=["attendance"])


@router.get(
    "/training_sessions/{training_session_id}/attendance",
    response_model=List[Attendance],
    summary="Lista presenças da sessão",
    responses={
        200: {"description": "Lista de presenças com eager loading (<50ms)"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def list_attendance_by_session(
    training_session_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
    athlete_id: Optional[UUID] = Query(default=None, description="Filtrar por atleta"),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filtrar por status ('present', 'absent')",
    ),
):
    """
    Retorna lista de registros de presença para uma sessão de treino.
    
    **Performance**: Usa eager loading (joinedload) para resolver N+1 queries (<50ms).
    **LGPD**: Filtra por team_memberships e registra acesso em data_access_logs.

    **Regras**: R22 (métricas operacionais), R25/R26 (permissões).

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Sessão não encontrada.
    """
    try:
        service = AttendanceService(db)
        
        # Extrair IP e User-Agent para audit log
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        
        # Obter role do usuário (simplificado - usar sistema RBAC real em produção)
        user_role = 'coordinator' if current_user.is_superadmin else 'coach'
        
        attendances = await service.get_session_attendance(
            session_id=training_session_id,
            user_id=current_user.user_id,
            user_role=user_role,
            person_id=current_user.person_id,
            ip_address=ip_address,
            user_agent=user_agent,
            athlete_id_filter=athlete_id,
            status_filter=status_filter
        )
        
        return attendances
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar presenças: {str(e)}"
        )


@router.post(
    "/training_sessions/{training_session_id}/attendance/batch",
    response_model=List[Attendance],
    status_code=status.HTTP_201_CREATED,
    summary="Registra presenças em batch",
    responses={
        201: {"description": "Presenças registradas com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
        409: {"description": "Conflito (duplicidade ou temporada bloqueada)"},
        422: {"description": "Erro de validação"},
    },
)
async def add_attendance_batch(
    training_session_id: UUID,
    payload: List[AttendanceCreate],
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Cria múltiplos registros de presença em batch (operação otimizada).
    Apenas 1 presença por atleta por sessão (UNIQUE session_id + athlete_id).

    **Regras**:
    - R22: Métricas operacionais.
    - RF5.2: Temporada interrompida bloqueia criação.
    - R25/R26: Permissões por papel e escopo.

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Sessão não encontrada.
    - 409 conflict_unique: Presença já registrada para este atleta nesta sessão.
    - 409 season_locked: Temporada interrompida/encerrada.
    - 422 validation_error: Payload inválido ou FK inválida.
    """
    try:
        service = AttendanceService(db)
        user_role = 'coordinator' if current_user.is_superadmin else 'coach'
        
        attendances = await service.record_batch(
            session_id=training_session_id,
            attendances=payload,
            user_id=current_user.user_id,
            user_role=user_role,
            person_id=current_user.person_id
        )
        
        await db.commit()
        return attendances
        
    except NotFoundError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar presenças: {str(e)}"
        )


@router.post(
    "/training_sessions/{training_session_id}/attendance",
    response_model=Attendance,
    status_code=status.HTTP_201_CREATED,
    summary="Registra presença individual",
    responses={
        201: {"description": "Presença registrada com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
        409: {"description": "Conflito (duplicidade ou temporada bloqueada)"},
        422: {"description": "Erro de validação"},
    },
)
async def add_attendance_to_session(
    training_session_id: UUID,
    payload: AttendanceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Cria registro de presença individual para um atleta em uma sessão de treino.

    **Nota**: Para múltiplos atletas, use o endpoint /batch para melhor performance.
    """
    try:
        service = AttendanceService(db)
        user_role = 'coordinator' if current_user.is_superadmin else 'coach'
        
        attendances = await service.record_batch(
            session_id=training_session_id,
            attendances=[payload],
            user_id=current_user.user_id,
            user_role=user_role,
            person_id=current_user.person_id
        )
        
        await db.commit()
        return attendances[0]
        
    except NotFoundError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar presença: {str(e)}"
        )


@router.patch(
    "/attendance/{attendance_id}",
    response_model=Attendance,
    summary="Atualiza registro de presença",
    responses={
        200: {"description": "Presença atualizada com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Presença não encontrada"},
        409: {"description": "Conflito de estado (R40: janela expirada, RF5.2: temporada)"},
        422: {"description": "Erro de validação"},
    },
)
async def update_attendance(
    attendance_id: UUID,
    payload: AttendanceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Atualiza status, minutes_effective, comment ou participation_type de um registro de presença.

    **Regras**:
    - R40: Janela de edição (10min/24h).
    - RF5.2/R37: Temporada bloqueada.
    - R25/R26: Permissões por papel e escopo.

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Presença não encontrada.
    - 409 edit_window_expired: Janela de edição expirada (R40).
    - 409 season_locked: Temporada interrompida/encerrada.
    - 422 validation_error: Payload inválido.
    """
    try:
        service = AttendanceService(db)
        user_role = 'coordinator' if current_user.is_superadmin else 'coach'
        
        attendance = await service.update_participation(
            attendance_id=attendance_id,
            data=payload,
            user_id=current_user.user_id,
            user_role=user_role,
            person_id=current_user.person_id
        )
        
        await db.commit()
        return attendance
        
    except NotFoundError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar presença: {str(e)}"
        )


@router.get(
    "/training_sessions/{training_session_id}/attendance/statistics",
    response_model=Dict[str, Any],
    summary="Estatísticas de presença da sessão",
    responses={
        200: {"description": "Estatísticas agregadas"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def get_session_attendance_statistics(
    training_session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Retorna estatísticas agregadas de presença de uma sessão.
    
    Retorna:
        - total_athletes: Total de atletas registrados
        - present_count: Quantidade de presentes
        - absent_count: Quantidade de ausentes
        - attendance_rate: Taxa de presença (0-100%)
    """
    try:
        service = AttendanceService(db)
        
        statistics = await service.get_session_statistics(
            session_id=training_session_id,
            user_id=current_user.user_id,
            person_id=current_user.person_id
        )
        
        return statistics
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular estatísticas: {str(e)}"
        )

@router.post(
    "/attendance/{attendance_id}/correct",
    response_model=Attendance,
    summary="Corrige presença administrativamente (RBAC)",
    responses={
        200: {"description": "Presença corrigida com auditoria"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas Coordenador/Admin)"},
        404: {"description": "Presença não encontrada"},
        422: {"description": "Validação: sessão não fechada ou comment inválido"},
    },
)
async def correct_attendance_administrative(
    attendance_id: UUID,
    payload: AttendanceCorrection,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Aplica correção administrativa a um registro de presença.

    **Regras RBAC (Step 11 - Refatoração Training):**
    - Apenas Coordenadores e Administradores podem corrigir
    - Requer permissão `attendance:correction_write`
    - Permitido apenas em sessões fechadas (R37: ação administrativa auditada)

    **Auditoria automática:**
    - source = 'correction'
    - correction_by_user_id = ID do usuário que corrigiu
    - correction_at = timestamp da correção
    - comment = motivo da correção (obrigatório, mín 10 caracteres)

    **Diferença vs PATCH /attendance/{id}:**
    - PATCH: edição normal dentro da janela temporal (R40)
    - POST /correct: correção administrativa após fechamento (R37)

    **Erros mapeados**:
    - 403 permission_denied: Sem permissão (apenas Coordenador/Admin).
    - 404 not_found: Presença não encontrada.
    - 422 validation_error: Sessão não fechada ou comment < 10 caracteres.
    """
    try:
        service = AttendanceService(db)
        
        # Determinar role do usuário (simplificado - usar sistema RBAC real)
        # TODO: Integrar com sistema de permissões real via permissions_map.py
        user_role = 'coordinator' if current_user.is_superadmin else 'coach'
        
        attendance = await service.correct_attendance(
            attendance_id=attendance_id,
            data=payload,
            user_id=current_user.user_id,
            user_role=user_role,
            person_id=current_user.person_id
        )
        
        await db.commit()
        return attendance
        
    except NotFoundError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao corrigir presença: {str(e)}"
        )


# =============================================================================
# AR_185 — Novos endpoints: preconfirm, close_session, pending-items
# INV-TRAIN-063, INV-TRAIN-065, DEC-INV-065
# =============================================================================

@router.post(
    "/attendance/sessions/{session_id}/preconfirm",
    summary="Atleta registra pré-confirmação de presença (INV-TRAIN-063)",
    responses={
        200: {"description": "Pré-confirmação registrada"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas atleta)"},
        404: {"description": "Sessão ou atleta não encontrado"},
        422: {"description": "Sessão já iniciada — pré-confirmação não permitida"},
    },
)
async def preconfirm_attendance(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Registra pré-confirmação de presença pelo atleta autenticado.

    INV-TRAIN-063: preconfirm NÃO gera is_official=True.
    Permitido apenas antes do início da sessão (status in [scheduled, draft]).
    """
    try:
        # Resolver athlete_id a partir do person_id do usuário autenticado
        athlete_row = await db.execute(
            sa_text("SELECT id FROM athletes WHERE person_id = :pid AND deleted_at IS NULL LIMIT 1"),
            {"pid": str(current_user.person_id)},
        )
        athlete = athlete_row.fetchone()
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Atleta não encontrado para o usuário autenticado",
            )
        athlete_id = athlete[0]

        service = AttendanceService(db)
        await service.set_preconfirm(
            session_id=session_id,
            athlete_id=athlete_id,
            user_id=current_user.user_id,
        )
        await db.commit()
        return {"presence_status": "preconfirm", "session_id": str(session_id)}

    except HTTPException:
        await db.rollback()
        raise
    except NotFoundError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar pré-confirmação: {str(e)}",
        )


@router.post(
    "/attendance/sessions/{session_id}/close",
    summary="Treinador fecha sessão e consolida presenças (DEC-INV-065)",
    responses={
        200: {"description": "Sessão fechada com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas treinador/admin)"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def close_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Consolida presenças ao fechar sessão.

    DEC-INV-065: encerramento NUNCA é bloqueado por pending items.
    Converte registros preconfirm→absent (treinador define presença oficial).
    Permissão: treinador/admin.
    """
    try:
        service = AttendanceService(db)
        pending_count = await service.close_session_attendance(
            session_id=session_id,
            closed_by_user_id=current_user.user_id,
        )
        await db.commit()
        return {"closed": True, "pending_count": pending_count}

    except NotFoundError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fechar sessão: {str(e)}",
        )


@router.get(
    "/attendance/sessions/{session_id}/pending-items",
    summary="Lista pending items da sessão (INV-TRAIN-066)",
    responses={
        200: {"description": "Lista de pending items"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas treinador/admin)"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def list_session_pending_items(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: ExecutionContext = Depends(get_current_user),
):
    """
    Lista todos os pending items de divergência da sessão.

    INV-TRAIN-066: treinador vê todos; atleta vê apenas os próprios (RBAC no service).
    Permissão: treinador/admin.
    """
    try:
        service = TrainingPendingService(db, current_user)
        items = await service.list_pending_items(session_id=session_id)
        return items

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar pending items: {str(e)}",
        )