"""
Router para Seasons (Temporadas).

FASE 5 — Implementação da lógica de negócio.

Regras aplicáveis:
- RF4: Criação de temporadas (Dirigentes, Coordenadores, Treinadores)
- RF5: Encerramento automático de temporada (não manual após início)
- RF5.1: Cancelamento antes do início (sem dados vinculados)
- RF5.2: Interrupção após início (força maior)
- R37: Edição após encerramento exige ação administrativa auditada
- RDB4: Soft delete obrigatório (deleted_at, deleted_reason)
- 6.1.1: Status derivado (planejada|ativa|interrompida|cancelada|encerrada)

Erros mapeados (Contrato de erros por regra):
- 401 unauthorized: credencial ausente/inválida
- 403 permission_denied (R25/R26): permissão insuficiente
- 404 not_found: recurso inexistente
- 409 season_locked (RF5.2/R37): temporada interrompida, operação bloqueada
- 409 season_has_linked_data (RF5.1): temporada tem dados vinculados
- 409 invalid_state_transition: transição de estado inválida
- 422 validation_error: payload inválido
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.auth import ExecutionContext
from app.core.db import get_async_db
from app.schemas.seasons import (
    SeasonCreate,
    SeasonPaginatedResponse,
    SeasonResponse,
    SeasonUpdate,
)
from app.services.season_service import SeasonService

router = APIRouter(tags=["seasons"])


class ReasonRequest(BaseModel):
    """Payload para operações que exigem motivo."""

    reason: str


def _get_service(db: AsyncSession) -> SeasonService:
    """Factory para SeasonService."""
    return SeasonService(db)


# -----------------------------------------------------------------------------
# GET /v1/seasons — Listar temporadas
# -----------------------------------------------------------------------------
@router.get(
    "",
    operation_id="listSeasons",
    status_code=status.HTTP_200_OK,
    summary="Listar temporadas",
    response_model=SeasonPaginatedResponse,
    responses={
        200: {"description": "Lista de temporadas"},
        401: {"description": "Credencial ausente ou inválida"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
    },
)
async def list_seasons(
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        enum=["planejada", "ativa", "interrompida", "cancelada", "encerrada"],
        description="Filtro por status derivado (6.1.1)",
    ),
):
    """
    Lista temporadas com paginação.

    **Regras:** R25/R26 (filtro por organização implícito via token)

    **Filtros disponíveis:**
    - status: derivado conforme 6.1.1 (planejada|ativa|interrompida|cancelada|encerrada)
    """
    service = _get_service(db)
    seasons, total = await service.list_seasons(
        organization_id=ctx.organization_id,
        page=page,
        limit=limit,
    )

    # Filtro por status (pós-query, pois é derivado)
    if status_filter:
        seasons = [s for s in seasons if s.status == status_filter]
        total = len(seasons)

    return SeasonPaginatedResponse(
        items=[SeasonResponse.model_validate(s) for s in seasons],
        page=page,
        limit=limit,
        total=total,
    )


# -----------------------------------------------------------------------------
# POST /v1/seasons — Criar temporada
# -----------------------------------------------------------------------------
@router.post(
    "",
    operation_id="createSeason",
    status_code=status.HTTP_201_CREATED,
    summary="Criar temporada",
    response_model=SeasonResponse,
    responses={
        201: {"description": "Temporada criada"},
        401: {"description": "Credencial ausente ou inválida"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        422: {"description": "Erro de validação"},
    },
)
async def create_season(
    body: SeasonCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Cria uma nova temporada.

    **Regras:**
    - RF4: Dirigentes, Coordenadores e Treinadores podem criar temporadas
    - R25/R26: Permissões por papel
    - RDB8: start_date < end_date (validado pelo DB)
    - 6.1.1: Status inicial será "planejada" (se start_date > hoje)
    """
    service = _get_service(db)
    try:
        season = await service.create(
            data=body,
            organization_id=ctx.organization_id,
            membership_id=getattr(ctx, "membership_id", None),
            created_by_user_id=getattr(ctx, "user_id", None),
        )
        await db.commit()
        await db.refresh(season)
        return SeasonResponse.model_validate(season)
    except ValueError as exc:
        code = str(exc)
        if code == "team_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "not_found", "message": "Equipe não encontrada para a temporada"},
            )
        if code == "team_out_of_org":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "permission_denied", "message": "Equipe não pertence à organização atual"},
            )
        raise


# -----------------------------------------------------------------------------
# GET /v1/seasons/{season_id} — Obter temporada
# -----------------------------------------------------------------------------
@router.get(
    "/{season_id}",
    operation_id="getSeason",
    status_code=status.HTTP_200_OK,
    summary="Obter temporada",
    response_model=SeasonResponse,
    responses={
        200: {"description": "Detalhes da temporada"},
        401: {"description": "Credencial ausente ou inválida"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        404: {"description": "Temporada não encontrada"},
    },
)
async def get_season(
    season_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Retorna detalhes de uma temporada específica.

    **Regras:** R25/R26 (permissões por papel)

    **Response inclui:**
    - status derivado conforme 6.1.1
    - deleted_at/deleted_reason se soft-deleted (RDB4)
    """
    service = _get_service(db)
    season = await service.get_by_id(season_id)

    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Temporada não encontrada"},
        )

    # Verificar organização (R25/R26)
    if str(season.organization_id) != str(ctx.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "permission_denied", "message": "Sem acesso a esta temporada"},
        )

    return SeasonResponse.model_validate(season)


# -----------------------------------------------------------------------------
# PATCH /v1/seasons/{season_id} — Atualizar temporada
# -----------------------------------------------------------------------------
@router.patch(
    "/{season_id}",
    operation_id="updateSeason",
    status_code=status.HTTP_200_OK,
    summary="Atualizar temporada",
    response_model=SeasonResponse,
    responses={
        200: {"description": "Temporada atualizada"},
        401: {"description": "Credencial ausente ou inválida"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        404: {"description": "Temporada não encontrada"},
        409: {"description": "season_locked - Temporada interrompida (RF5.2/R37)"},
        422: {"description": "Erro de validação"},
    },
)
async def update_season(
    season_id: UUID,
    body: SeasonUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Atualiza parcialmente uma temporada.

    **Regras:**
    - RF5: Não permite encerramento manual após início
    - RF5.2: NÃO editar se interrompida
    - R37: Após encerramento, edição só via ação administrativa auditada
    - RDB4: Soft delete via deleted_at/deleted_reason (não DELETE físico)
    - 6.1.1: Status é derivado, não editável diretamente
    """
    service = _get_service(db)
    season = await service.get_by_id(season_id)

    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Temporada não encontrada"},
        )

    # Verificar organização (R25/R26)
    if str(season.organization_id) != str(ctx.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "permission_denied", "message": "Sem acesso a esta temporada"},
        )

    try:
        season = await service.update(season, body)
        await db.commit()
        await db.refresh(season)
        return SeasonResponse.model_validate(season)
    except ValueError as e:
        if str(e) == "season_locked":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "season_locked",
                    "message": "Temporada interrompida não pode ser editada (RF5.2/R37)",
                },
            )
        raise


# -----------------------------------------------------------------------------
# POST /v1/seasons/{season_id}/interrupt — Interromper temporada
# -----------------------------------------------------------------------------
@router.post(
    "/{season_id}/interrupt",
    operation_id="interruptSeason",
    status_code=status.HTTP_200_OK,
    summary="Interromper temporada",
    response_model=SeasonResponse,
    responses={
        200: {"description": "Temporada interrompida"},
        401: {"description": "Credencial ausente ou inválida"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        404: {"description": "Temporada não encontrada"},
        409: {"description": "invalid_state_transition - Temporada não está ativa"},
        422: {"description": "Erro de validação"},
    },
)
async def interrupt_season(
    season_id: UUID,
    body: ReasonRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Interrompe uma temporada ativa por força maior.

    **Regras:**
    - RF5.2: Interrupção após início (força maior)
    - R37: Bloqueia criação/edição de novos eventos após interrupção
    - 6.1.1: Status muda para "interrompida"

    **Pré-condições:**
    - Temporada deve estar em status "ativa"

    **Payload obrigatório:** { "reason": "..." }
    """
    service = _get_service(db)
    season = await service.get_by_id(season_id)

    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Temporada não encontrada"},
        )

    # Verificar organização (R25/R26)
    if str(season.organization_id) != str(ctx.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "permission_denied", "message": "Sem acesso a esta temporada"},
        )

    try:
        season = await service.interrupt(season, body.reason)
        await db.commit()
        await db.refresh(season)
        return SeasonResponse.model_validate(season)
    except ValueError as e:
        if str(e) == "invalid_state_transition":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "invalid_state_transition",
                    "message": f"Temporada não pode ser interrompida (status atual: {season.status})",
                },
            )
        raise


# -----------------------------------------------------------------------------
# POST /v1/seasons/{season_id}/cancel — Cancelar temporada
# -----------------------------------------------------------------------------
@router.post(
    "/{season_id}/cancel",
    operation_id="cancelSeason",
    status_code=status.HTTP_200_OK,
    summary="Cancelar temporada",
    response_model=SeasonResponse,
    responses={
        200: {"description": "Temporada cancelada"},
        401: {"description": "Credencial ausente ou inválida"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        404: {"description": "Temporada não encontrada"},
        409: {"description": "Conflito - temporada não pode ser cancelada"},
        422: {"description": "Erro de validação"},
    },
)
async def cancel_season(
    season_id: UUID,
    body: ReasonRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["dirigente", "coordenador", "treinador"], require_org=True)
    ),
):
    """
    Cancela uma temporada antes do início.

    **Regras:**
    - RF5.1: Cancelamento permitido apenas se a temporada não possuir dados vinculados
    - 6.1.1: Status muda para "cancelada"

    **Pré-condições:**
    - Temporada deve estar em status "planejada" (antes de start_date)
    - Não pode haver dados vinculados (equipes, jogos, treinos, etc.)

    **Payload obrigatório:** { "reason": "..." }
    """
    service = _get_service(db)
    season = await service.get_by_id(season_id)

    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Temporada não encontrada"},
        )

    # Verificar organização (R25/R26)
    if str(season.organization_id) != str(ctx.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "permission_denied", "message": "Sem acesso a esta temporada"},
        )

    try:
        season = await service.cancel(season, body.reason)
        await db.commit()
        await db.refresh(season)
        return SeasonResponse.model_validate(season)
    except ValueError as e:
        error_code = str(e)
        if error_code == "invalid_state_transition":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "invalid_state_transition",
                    "message": f"Temporada não pode ser cancelada (status atual: {season.status})",
                },
            )
        if error_code == "season_has_linked_data":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "season_has_linked_data",
                    "message": "Temporada possui dados vinculados e não pode ser cancelada (RF5.1)",
                },
            )
        raise


# -----------------------------------------------------------------------------
# DELETE /v1/seasons/{season_id} — Excluir temporada (soft delete)
# -----------------------------------------------------------------------------
@router.delete(
    "/{season_id}",
    operation_id="deleteSeason",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir temporada (soft delete)",
    responses={
        204: {"description": "Temporada excluída"},
        401: {"description": "Credencial ausente ou inválida"},
        403: {"description": "Permissão insuficiente (R25/R26)"},
        404: {"description": "Temporada não encontrada"},
    },
)
async def delete_season(
    season_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(
        permission_dep(roles=["coordenador", "dirigente"], require_org=True)
    ),
):
    """
    Cancela uma temporada planejada (RF5.1).

    **Regras:**
    - RF5.1: Apenas temporada planejada e sem dados vinculados
    - R25/R26: Permissões por papel
    """
    service = _get_service(db)
    season = await service.get_by_id(season_id)

    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Temporada não encontrada"},
        )

    # Verificar organização (R25/R26)
    if str(season.organization_id) != str(ctx.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "permission_denied", "message": "Sem acesso a esta temporada"},
        )

    try:
        await service.cancel(season, reason="Cancelamento administrativo")
        await db.commit()
        return None
    except ValueError as e:
        if str(e) == "invalid_state_transition":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "invalid_state_transition", "message": "Temporada nao pode ser cancelada"},
            )
        if str(e) == "season_has_linked_data":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "season_has_linked_data", "message": "Temporada possui dados vinculados"},
            )
        raise

