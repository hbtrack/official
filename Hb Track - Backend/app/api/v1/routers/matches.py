"""
Router para Partidas (Matches).

Regras RAG aplicadas:
- R19: Estrutura de partida
- RF14/RF15: Status e permissões de edição
- RDB13: Tabela matches
- 6.1.2: Fluxo de status
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import permission_dep
from app.core.auth import get_current_context, require_role
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.models.match import MatchStatus, MatchType
from app.schemas.matches import (
    MatchCreate,
    MatchUpdate,
    MatchStatusUpdate,
    MatchResponse,
    MatchList,
    MatchWithEvents,
)
from app.schemas.error import ErrorResponse
from app.services.match_service import MatchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matches", tags=["Matches"])
# Novas rotas canônicas com escopo de equipe
scoped_router = APIRouter(prefix="/teams/{team_id}/matches", tags=["Matches"])


def _ensure_match_in_team(match, team_id: UUID) -> None:
    if str(match.team_id) != str(team_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permission_denied_team_scope",
        )
# DEPRECATED: usar /teams/{team_id}/matches...
# DEPRECATED: usar /teams/{team_id}/matches...
# DEPRECATED: usar /teams/{team_id}/matches...
@router.get(
    "",
    response_model=MatchList,
    summary="Listar partidas",
    description="Lista partidas da organização com filtros e paginação.",
)
async def list_matches(
    team_id: Optional[UUID] = Query(None, description="Filtrar por time"),
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    match_status: Optional[MatchStatus] = Query(None, alias="status", description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
):
    """
    Lista partidas com filtros opcionais.
    Ref: RDB14 - Paginação padrão
    """
    service = MatchService(db, context)
    matches, total = await service.get_all(
        team_id=team_id,
        season_id=season_id,
        status=match_status,
        page=page,
        size=size,
    )

    pages = (total + size - 1) // size if total > 0 else 0

    return MatchList(
        items=matches,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


# DEPRECATED: usar /teams/{team_id}/matches...
# DEPRECATED: usar /teams/{team_id}/matches...
# DEPRECATED: usar /teams/{team_id}/matches...
@router.post(
    "",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar partida",
    description="Cria uma nova partida para um time.",
    responses={
        404: {"model": ErrorResponse, "description": "Time não encontrado"},
        403: {"model": ErrorResponse, "description": "Sem permissão"},
    },
)
async def create_match(
    data: MatchCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["treinador", "coordenador", "dirigente"])),
):
    """
    Cria nova partida.
    Ref: R19 - Partida inicia com status 'rascunho'
    """
    service = MatchService(db, context)
    match = await service.create(data)
    db.commit()
    db.refresh(match)

    # Adicionar campos calculados
    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished

    return response


# =============================================================================
# Rotas canônicas com escopo de equipe (/teams/{team_id}/matches)
# =============================================================================

@scoped_router.get(
    "",
    response_model=MatchList,
    summary="Listar partidas por equipe",
    description="Lista partidas de uma equipe com filtros e paginação.",
)
async def scoped_list_matches(
    team_id: UUID,
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    match_status: Optional[MatchStatus] = Query(None, alias="status", description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
):
    service = MatchService(db, ctx)
    matches, total = await service.get_all(
        team_id=team_id,
        season_id=season_id,
        status=match_status,
        page=page,
        size=size,
    )
    pages = (total + size - 1) // size if total > 0 else 0
    return MatchList(items=matches, total=total, page=page, size=size, pages=pages)


@scoped_router.post(
    "",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar partida (escopo equipe)",
    responses={
        404: {"model": ErrorResponse, "description": "Time não encontrado"},
        403: {"model": ErrorResponse, "description": "Sem permissão"},
    },
)
async def scoped_create_match(
    team_id: UUID,
    data: MatchCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin", "coach"], require_team=True)),
):
    data.team_id = team_id
    service = MatchService(db, ctx)
    match = await service.create(data)
    db.commit()
    db.refresh(match)
    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished
    return response


@scoped_router.get(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Obter partida (escopo equipe)",
    responses={404: {"model": ErrorResponse, "description": "Partida não encontrada"}},
)
async def scoped_get_match(
    team_id: UUID,
    match_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
):
    service = MatchService(db, ctx)
    match = await service.get_by_id(match_id)
    _ensure_match_in_team(match, team_id)
    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished
    return response


@scoped_router.get(
    "/{match_id}/with-events",
    response_model=MatchWithEvents,
    summary="Obter partida com eventos (escopo equipe)",
    responses={404: {"model": ErrorResponse, "description": "Partida não encontrada"}},
)
async def scoped_get_match_with_events(
    team_id: UUID,
    match_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
):
    service = MatchService(db, ctx)
    match = await service.get_by_id(match_id, with_events=True)
    _ensure_match_in_team(match, team_id)
    response = MatchWithEvents.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished
    response.total_events = len(match.events) if match.events else 0
    return response


@scoped_router.patch(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Atualizar partida (escopo equipe)",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        403: {"model": ErrorResponse, "description": "Partida finalizada"},
    },
)
async def scoped_update_match(
    team_id: UUID,
    match_id: UUID,
    data: MatchUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin", "coach"], require_team=True)),
):
    service = MatchService(db, ctx)
    match = await service.update(match_id, data)
    _ensure_match_in_team(match, team_id)
    db.commit()
    db.refresh(match)
    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished
    return response


@scoped_router.post(
    "/{match_id}/status",
    response_model=MatchResponse,
    summary="Alterar status da partida (escopo equipe)",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        403: {"model": ErrorResponse, "description": "Transição não permitida"},
        422: {"model": ErrorResponse, "description": "Dados inválidos"},
    },
)
async def scoped_update_match_status(
    team_id: UUID,
    match_id: UUID,
    data: MatchStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin", "coach"], require_team=True)),
):
    service = MatchService(db, ctx)
    match = await service.update_status(match_id, data)
    _ensure_match_in_team(match, team_id)
    db.commit()
    db.refresh(match)
    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished
    return response


@scoped_router.delete(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Excluir partida (escopo equipe)",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        403: {"model": ErrorResponse, "description": "Partida finalizada"},
    },
)
async def scoped_delete_match(
    team_id: UUID,
    match_id: UUID,
    reason: str = Query(..., min_length=5, description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin"], require_team=True)),
):
    service = MatchService(db, ctx)
    match = await service.soft_delete(match_id, reason)
    _ensure_match_in_team(match, team_id)
    db.commit()
    db.refresh(match)
    return MatchResponse.model_validate(match)


@scoped_router.post(
    "/{match_id}/restore",
    response_model=MatchResponse,
    summary="Restaurar partida (escopo equipe)",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        422: {"model": ErrorResponse, "description": "Partida não está excluída"},
    },
)
async def scoped_restore_match(
    team_id: UUID,
    match_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin"], require_team=True)),
):
    service = MatchService(db, ctx)
    match = await service.restore(match_id)
    _ensure_match_in_team(match, team_id)
    db.commit()
    db.refresh(match)
    return MatchResponse.model_validate(match)


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Obter partida",
    description="Retorna detalhes de uma partida específica.",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
    },
)
async def get_match(
    match_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
):
    """
    Busca partida por ID.
    """
    service = MatchService(db, context)
    match = await service.get_by_id(match_id)

    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished

    return response


@router.get(
    "/{match_id}/with-events",
    response_model=MatchWithEvents,
    summary="Obter partida com eventos",
    description="Retorna partida com todos os eventos/estatísticas.",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
    },
)
async def get_match_with_events(
    match_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
):
    """
    Busca partida com eventos inclusos.
    Ref: RD1-RD91 - Eventos estatísticos
    """
    service = MatchService(db, context)
    match = await service.get_by_id(match_id, with_events=True)

    response = MatchWithEvents.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished
    response.total_events = len(match.events) if match.events else 0

    return response


# DEPRECATED: usar /teams/{team_id}/matches...
@router.patch(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Atualizar partida",
    description="Atualiza dados de uma partida.",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        403: {"model": ErrorResponse, "description": "Partida finalizada"},
    },
)
async def update_match(
    match_id: UUID,
    data: MatchUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["treinador", "coordenador", "dirigente"])),
):
    """
    Atualiza partida.
    Ref: RF14 - Não pode editar se finalizada
    """
    service = MatchService(db, context)
    match = await service.update(match_id, data)
    db.commit()
    db.refresh(match)

    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished

    return response


@router.post(
    "/{match_id}/status",
    response_model=MatchResponse,
    summary="Alterar status da partida",
    description="Altera o status da partida conforme fluxo permitido.",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        403: {"model": ErrorResponse, "description": "Transição não permitida"},
        422: {"model": ErrorResponse, "description": "Dados inválidos"},
    },
)
async def update_match_status(
    match_id: UUID,
    data: MatchStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["treinador", "coordenador", "dirigente"])),
):
    """
    Atualiza status da partida.
    Ref: 6.1.2, RF14, RF15 - Fluxo de status
    
    Transições:
    - rascunho -> em_revisao: Treinador+
    - em_revisao -> finalizado: Admin+
    - em_revisao -> rascunho: Admin+ (com nota)
    - finalizado -> em_revisao: SuperAdmin APENAS (com nota)
    """
    service = MatchService(db, context)
    match = await service.update_status(match_id, data)
    db.commit()
    db.refresh(match)

    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished

    return response


# DEPRECATED: usar /teams/{team_id}/matches...
@router.delete(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Excluir partida",
    description="Soft delete de uma partida.",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        403: {"model": ErrorResponse, "description": "Partida finalizada"},
    },
)
async def delete_match(
    match_id: UUID,
    reason: str = Query(..., min_length=5, description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["coordenador", "dirigente"])),
):
    """
    Soft delete de partida.
    Ref: RDB3 - Soft delete
    """
    service = MatchService(db, context)
    match = await service.soft_delete(match_id, reason)
    db.commit()
    db.refresh(match)

    return MatchResponse.model_validate(match)


@router.post(
    "/{match_id}/restore",
    response_model=MatchResponse,
    summary="Restaurar partida",
    description="Restaura uma partida excluída.",
    responses={
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        422: {"model": ErrorResponse, "description": "Partida não está excluída"},
    },
)
async def restore_match(
    match_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["coordenador", "dirigente"])),
):
    """
    Restaura partida deletada.
    Ref: RDB3 - Restore
    """
    service = MatchService(db, context)
    match = await service.restore(match_id)
    db.commit()
    db.refresh(match)

    response = MatchResponse.model_validate(match)
    response.is_finalized = match.status == MatchStatus.finished
    response.can_edit = match.status != MatchStatus.finished

    return response
