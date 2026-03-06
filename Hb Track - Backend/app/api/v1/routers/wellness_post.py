"""
Router para wellness pós-treino (Wellness Post).

Regras aplicáveis:
- R22: Dados de treino são métricas operacionais.
- R40: Limite temporal de edição (até created_at + 24 hours).
- R25/R26: Permissões por papel e escopo.
- RF5.2: Temporada interrompida bloqueia criação/edição.
- R29/R33: Sem DELETE físico; histórico com rastro.

Constraints:
- UNIQUE (session_id, athlete_id): 1 wellness pós por atleta por sessão.

Regra técnica:
- internal_load = minutes_effective × session_rpe (calculado por trigger no banco).
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.auth import get_current_user
from app.core.exceptions import NotFoundError, PermissionDeniedError, ConflictError, ValidationError
from app.schemas.wellness import (
    WellnessPost,
    WellnessPostCreate,
    WellnessPostUpdate,
)
from app.services.wellness_post_service import WellnessPostService

router = APIRouter(tags=["wellness_post"])


def _ctx_get(user, name: str, default=None):
    if isinstance(user, dict):
        return user.get(name, default)
    return getattr(user, name, default)


@router.get(
    "/training_sessions/{training_session_id}/wellness_post",
    response_model=List[WellnessPost],
    summary="Lista wellness pós-treino da sessão",
    responses={
        200: {"description": "Lista de wellness pós-treino"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def list_wellness_post_by_session(
    training_session_id: UUID,
    request: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    athlete_id: Optional[UUID] = Query(default=None, description="Filtrar por atleta"),
):
    """
    Retorna lista de registros de wellness pós-treino para uma sessão.

    **Regras**: R22 (métricas operacionais), R25/R26 (permissões).

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Sessão não encontrada.
    """
    try:
        service = WellnessPostService(db)
        
        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'
        
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        
        wellness_list = await service.get_session_wellness_post(
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
    "/training_sessions/{training_session_id}/wellness_post/status",
    response_model=Dict[str, Any],
    summary="Status de preenchimento do wellness pós",
    responses={
        200: {"description": "Status de preenchimento"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente (apenas treinadores)"},
        404: {"description": "Sessão não encontrada"},
    },
)
async def get_wellness_post_status(
    training_session_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retorna status de preenchimento do wellness pós-treino.
    """
    try:
        service = WellnessPostService(db)
        
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
    "/training_sessions/{training_session_id}/wellness_post",
    response_model=WellnessPost,
    status_code=status.HTTP_201_CREATED,
    summary="Registra wellness pós-treino",
    responses={
        201: {"description": "Wellness pós-treino registrado com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Sessão não encontrada"},
        409: {"description": "Conflito (duplicidade ou temporada bloqueada)"},
        422: {"description": "Erro de validação"},
    },
)
async def add_wellness_post_to_session(
    training_session_id: UUID,
    payload: WellnessPostCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Cria registro de wellness pós-treino para um atleta.
    O campo `internal_load` é calculado automaticamente: `minutes_effective × session_rpe`.

    **Regras**:
    - R22: Métricas operacionais.
    - RF5.2: Temporada interrompida bloqueia criação.
    - R25/R26: Permissões por papel e escopo.

    **Regra técnica**: O trigger `tr_calculate_internal_load` calcula
    `internal_load = minutes_effective * session_rpe` automaticamente no INSERT/UPDATE.

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Sessão não encontrada.
    - 409 conflict_unique: Wellness pós já registrado para este atleta nesta sessão.
    - 409 season_locked: Temporada interrompida/encerrada.
    - 422 validation_error: Payload inválido ou FK inválida.
    """
    try:
        service = WellnessPostService(db)
        
        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'
        
        wellness = await service.submit_wellness_post(
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
    "/wellness_post/{wellness_post_id}",
    response_model=WellnessPost,
    summary="Obtém wellness pós-treino por ID",
    responses={
        200: {"description": "Detalhes do wellness pós-treino"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Wellness pós-treino não encontrado"},
    },
)
async def get_wellness_post_by_id(
    wellness_post_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retorna detalhes de um registro de wellness pós-treino específico.

    **Regras**: R25/R26 (permissões por papel e escopo).

    **Erros mapeados**:
    - 403 permission_denied: Permissão insuficiente.
    - 404 not_found: Wellness pós-treino não encontrado.
    """
    try:
        service = WellnessPostService(db)

        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'

        wellness = await service.get_wellness_post_by_id(
            wellness_id=wellness_post_id,
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
    "/wellness_post/{wellness_post_id}",
    response_model=WellnessPost,
    summary="Atualiza wellness pós-treino",
    responses={
        200: {"description": "Wellness pós-treino atualizado com sucesso"},
        401: {"description": "Token inválido ou ausente"},
        403: {"description": "Permissão insuficiente"},
        404: {"description": "Wellness pós-treino não encontrado"},
        409: {"description": "Janela de edição expirada (R40) ou conflito (R41) ou temporada bloqueada (RF5.2)"},
        422: {"description": "Erro de validação"},
    },
)
async def update_wellness_post(
    wellness_post_id: UUID,
    payload: WellnessPostUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Atualiza campos de wellness pós-treino.
    O campo `internal_load` é recalculado automaticamente quando `minutes_effective` ou `session_rpe` são alterados.
    Não é possível alterar session_id, athlete_id, organization_id ou created_by_membership_id.

    **Regra técnica**: O trigger `tr_calculate_internal_load` recalcula
    `internal_load = minutes_effective * session_rpe` automaticamente no UPDATE.

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
    - 404 not_found: Wellness pós-treino não encontrado.
    - 409 edit_window_expired: Janela de edição expirada (>24h).
    - 409 edit_conflict: Conflito de edição simultânea (R41).
    - 409 season_locked: Temporada interrompida/encerrada.
    - 422 validation_error: Payload inválido.
    """
    try:
        service = WellnessPostService(db)

        is_superadmin = bool(_ctx_get(current_user, "is_superadmin", False))
        role_code = _ctx_get(current_user, "role_code")
        user_role = 'coordinator' if is_superadmin else 'coach'
        if role_code == "atleta":
            user_role = 'athlete'

        wellness = await service.update_wellness_post_by_id(
            wellness_id=wellness_post_id,
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
