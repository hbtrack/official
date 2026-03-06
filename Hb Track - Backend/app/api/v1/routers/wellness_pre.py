"""
Router para wellness pré-treino (Wellness Pre).

Regras aplicáveis:
- R22: Dados de treino são métricas operacionais.
- R40: Limite temporal de edição (até session_at - 2 hours).
- R25/R26: Permissões por papel e escopo.
- RF5.2: Temporada interrompida bloqueia criação/edição.
- R29/R33: Sem DELETE físico; histórico com rastro.

Constraints:
- UNIQUE (session_id, athlete_id): 1 wellness pré por atleta por sessão.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.auth import get_current_user
from app.core.exceptions import NotFoundError, PermissionDeniedError, ConflictError, ValidationError
from app.schemas.wellness import (
    WellnessPre,
    WellnessPreCreate,
    WellnessPreUpdate,
)
from app.services.wellness_pre_service import WellnessPreService

router = APIRouter(tags=["wellness_pre"])


def _ctx_get(user, name: str, default=None):
    if isinstance(user, dict):
        return user.get(name, default)
    return getattr(user, name, default)


@router.get(
    "/training_sessions/{training_session_id}/wellness_pre",
    response_model=List[WellnessPre],
    summary="Lista wellness pré-treino da sessão",
    responses={
        200: {"description": "Lista de wellness pré-treino"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def list_wellness_pre_by_session(
    training_session_id: UUID,
    request: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    athlete_id: Optional[UUID] = Query(default=None, description="Filtrar por atleta"),
):
    """
    Retorna lista de registros de wellness pré-treino para uma sessão.

    **Regras**: R22 (métricas operacionais), R25/R26 (permissões).

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Sessão não encontrada.
    """
    try:
        service = WellnessPreService(db)
        
        # Determinar role do usuário
        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'
        
        # Extrair IP e user-agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        
        wellness_list = await service.get_session_wellness_pre(
            session_id=training_session_id,
            user_id=_ctx_get(current_user, "user_id"),
            user_role=user_role,
            athlete_filter=athlete_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return wellness_list
    
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/training_sessions/{training_session_id}/wellness_pre/status",
    response_model=Dict[str, Any],
    summary="Status de preenchimento do wellness pré",
    responses={
        200: {"description": "Status de preenchimento"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas treinadores)"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def get_wellness_pre_status(
    training_session_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retorna status de preenchimento do wellness pré-treino.
    
    **Resposta**:
    {
        "total_athletes": 20,
        "responded_pre": 15,
        "pending": [athlete_id1, athlete_id2, ...],
        "response_rate": 75.0
    }
    """
    try:
        service = WellnessPreService(db)
        
        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        user_role = 'coordinator' if is_superadmin else 'coach'
        
        status_data = await service.get_session_wellness_status(
            session_id=training_session_id,
            user_id=_ctx_get(current_user, "user_id"),
            user_role=user_role
        )
        
        return status_data
    
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/training_sessions/{training_session_id}/wellness_pre",
    response_model=WellnessPre,
    status_code=status.HTTP_201_CREATED,
    summary="Registra wellness pré-treino",
    responses={
        201: {"description": "Wellness pré-treino registrado com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
        409: {"description": "Conflito (duplicidade ou temporada bloqueada)"},
        422: {"description": "Erro de validação"},
    },
)
async def add_wellness_pre_to_session(
    training_session_id: UUID,
    payload: WellnessPreCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Cria registro de wellness pré-treino para um atleta (1 por atleta por sessão).

    **Regras**:
    - R22: Métricas operacionais.
    - RF5.2: Temporada interrompida bloqueia criação.
    - R25/R26: Permissões por papel e escopo.

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Sessão não encontrada.
    - 409 conflict_unique: Wellness pré já registrado para este atleta nesta sessão.
    - 409 season_locked: Temporada interrompida/encerrada.
    - 422 validation_error: Payload inválido ou FK inválida.
    """
    try:
        service = WellnessPreService(db)
        
        # Determinar role do usuário
        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'
        
        wellness = await service.submit_wellness_pre(
            session_id=training_session_id,
            athlete_id=payload.athlete_id,
            data=payload.dict(exclude={'athlete_id'}),
            user_id=_ctx_get(current_user, "user_id"),
            user_role=user_role
        )
        
        await db.commit()
        return wellness
    
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/wellness_pre/{wellness_pre_id}",
    response_model=WellnessPre,
    summary="Obtém wellness pré-treino por ID",
    responses={
        200: {"description": "Detalhes do wellness pré-treino"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Wellness pré-treino não encontrado"},
    },
)
async def get_wellness_pre_by_id(
    wellness_pre_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retorna detalhes de um registro de wellness pré-treino específico.

    **Regras**: R25/R26 (permissões por papel e escopo).

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Wellness pré-treino não encontrado.
    """
    try:
        service = WellnessPreService(db)

        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'

        wellness = await service.get_wellness_pre_by_id(
            wellness_id=wellness_pre_id,
            user_id=_ctx_get(current_user, "user_id"),
            user_role=user_role,
        )
        return wellness

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/wellness_pre/{wellness_pre_id}",
    response_model=WellnessPre,
    summary="Atualiza wellness pré-treino",
    responses={
        200: {"description": "Wellness pré-treino atualizado com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Wellness pré-treino não encontrado"},
        409: {"description": "Janela de edição expirada (R40) ou conflito (R41) ou temporada bloqueada (RF5.2)"},
        422: {"description": "Erro de validação"},
    },
)
async def update_wellness_pre(
    wellness_pre_id: UUID,
    payload: WellnessPreUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Atualiza campos de wellness pré-treino.
    Não é possível alterar session_id, athlete_id, organization_id ou created_by_membership_id.

    **Regras de edição (R40)**:
    - ≤10 minutos: autor pode editar livremente.
    - >10 min e ≤24h: exige perfil superior ou aprovação → 403 permission_denied.
    - >24h: somente leitura → 409 edit_window_expired.

    **Outras regras**:
    - R41: Conflito de edição simultânea → 409 edit_conflict.
    - RF5.2/R37: Temporada bloqueada → 409 season_locked.
    - R25/R26: Permissões por papel e escopo.

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente ou edição >10min sem perfil superior.
    - 404 not_found: Wellness pré-treino não encontrado.
    - 409 edit_window_expired: Janela de edição expirada (>24h).
    - 409 edit_conflict: Conflito de edição simultânea (R41).
    - 409 season_locked: Temporada interrompida/encerrada.
    - 422 validation_error: Payload inválido.
    """
    try:
        service = WellnessPreService(db)

        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'

        wellness = await service.update_wellness_pre_by_id(
            wellness_id=wellness_pre_id,
            data=payload.dict(exclude_none=True),
            user_id=_ctx_get(current_user, "user_id"),
            user_role=user_role,
        )
        await db.commit()
        return wellness

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/wellness_pre/{wellness_pre_id}/request-unlock",
    response_model=Dict[str, Any],
    summary="Solicita desbloqueio de wellness pré após deadline",
    responses={
        200: {"description": "Solicitação enviada com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Wellness pré-treino não encontrado"},
        422: {"description": "Erro de validação (razão obrigatória)"},
    },
)
async def request_wellness_unlock(
    wellness_pre_id: UUID,
    request: Request,
    reason: str = Query(..., min_length=10, max_length=500, description="Motivo da solicitação"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Atleta solicita desbloqueio de wellness pré após deadline.
    
    Cria uma notificação para o staff (treinador/coordenador) com a solicitação.
    O staff pode então decidir se desbloqueia o wellness para edição.
    
    **Regras**:
    - R40: Solicitação apenas após deadline (session_at - 2h)
    - Apenas o próprio atleta pode solicitar
    - Notificação enviada para staff da equipe
    
    **Payload**:
    - reason: Motivo da solicitação (10-500 caracteres)
    
    **Erros mapeados**:
    - 403 permission_denied: Não é o próprio atleta ou deadline não expirado
    - 404 not_found: Wellness pré-treino não encontrado
    - 422 validation_error: Razão inválida
    """
    try:
        from app.services.wellness_pre_service import WellnessPreService
        from app.services.notification_service import NotificationService
        from datetime import datetime, timedelta
        
        service = WellnessPreService(db)
        notification_service = NotificationService(db)
        
        # Buscar wellness pre
        from sqlalchemy import select
        from app.models.wellness_pre import WellnessPre as WellnessPreModel
        from app.models.training_session import TrainingSession
        
        result = await db.execute(
            select(WellnessPreModel, TrainingSession)
            .join(TrainingSession, WellnessPreModel.training_session_id == TrainingSession.id)
            .where(WellnessPreModel.id == wellness_pre_id)
        )
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wellness pré-treino não encontrado"
            )
        
        wellness, session = row
        
        # Verificar se é o próprio atleta
        athlete_id = current_user.get('athlete_id')
        if not athlete_id or wellness.athlete_id != UUID(athlete_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o próprio atleta pode solicitar desbloqueio"
            )
        
        # Verificar se deadline expirou
        deadline = session.session_at - timedelta(hours=2)
        if datetime.now() < deadline:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deadline ainda não expirou. Você pode editar até 2h antes da sessão."
            )
        
        # Buscar staff da equipe para notificar
        from app.models.team_membership import TeamMembership
        from app.models.user import User
        
        staff_result = await db.execute(
            select(User.id)
            .join(TeamMembership, TeamMembership.user_id == User.id)
            .where(TeamMembership.team_id == session.team_id)
            .where(TeamMembership.role.in_(['coordinator', 'coach']))
            .where(TeamMembership.is_active == True)
        )
        staff_ids = [row[0] for row in staff_result.fetchall()]
        
        # Criar notificação para cada membro do staff
        for staff_id in staff_ids:
            await notification_service.create(
                user_id=staff_id,
                type='wellness_unlock_request',
                title='Solicitação de Desbloqueio',
                message=f'Atleta solicita desbloqueio de wellness pré. Motivo: {reason[:100]}...',
                link=f'/admin/training/wellness-unlock/{wellness_pre_id}',
                metadata={
                    'wellness_pre_id': str(wellness_pre_id),
                    'athlete_id': str(wellness.athlete_id),
                    'session_id': str(session.id),
                    'session_title': session.title,
                    'reason': reason,
                    'requested_at': datetime.now().isoformat()
                }
            )
            
            # Broadcast via WebSocket se conectado
            await notification_service.broadcast_to_user(staff_id, {
                'type': 'wellness_unlock_request',
                'wellness_pre_id': str(wellness_pre_id),
                'session_title': session.title
            })
        
        await db.commit()
        
        return {
            'success': True,
            'message': 'Solicitação enviada para o staff. Você será notificado quando for aprovada.',
            'wellness_pre_id': str(wellness_pre_id),
            'notified_staff_count': len(staff_ids)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar solicitação: {str(e)}"
        )

