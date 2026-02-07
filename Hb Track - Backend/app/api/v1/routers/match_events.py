"""
Router para Eventos de Partida (Match Events).

FASE 5 - Implementação completa.

Regras RAG aplicadas:
- RD1-RD91: Tipos de eventos estatísticos
- R23/R24: Correção com histórico
- RD4: Atleta deve estar no roster
- RF15: Eventos só editáveis se partida não finalizada
- R25/R26: Permissões por papel e escopo
- RDB13: Jogo finalizado é somente leitura
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.deps.auth import permission_dep
from app.core.auth import get_current_context, require_role
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.core.permissions import require_team_registration_in_season
from app.models.match import Match
from app.models.team import Team
from app.models.season import Season
from app.models.match_event import EventType
from app.schemas.match_events import (
    MatchEventCreate,
    MatchEventUpdate,
    MatchEventCorrection,
    MatchEventResponse,
    MatchEventList,
    AthleteMatchStats,
)
from app.schemas.error import ErrorResponse
from app.services.match_event_service import MatchEventService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["match-events"])
# Rotas novas com escopo de equipe/match
scoped_events_router = APIRouter(
    prefix="/teams/{team_id}/matches/{match_id}",
    tags=["match-events"],
)


async def _get_match_scoped(
    db: AsyncSession, ctx: ExecutionContext, team_id: UUID, match_id: UUID
) -> Match:
    query = (
        select(Match)
        .join(Team, Team.id == Match.team_id)
        .where(Match.id == match_id)
    )
    if not ctx.is_superadmin:
        query = query.where(Team.organization_id == ctx.organization_id)
    result = db.execute(query)
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="match_not_found")
    if str(match.team_id) != str(team_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="permission_denied_team_scope")
    return match


# DEPRECATED: usar /teams/{team_id}/matches/{match_id}/events...
@router.get(
    "/matches/{match_id}/events",
    status_code=status.HTTP_200_OK,
    summary="Listar eventos do jogo",
    operation_id="listMatchEvents",
    response_model=MatchEventList,
    responses={
        200: {"description": "Lista paginada de eventos do jogo"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Jogo não encontrado", "model": ErrorResponse},
    },
)
async def list_match_events(
    match_id: UUID,
    athlete_id: Optional[UUID] = Query(None, description="Filtrar por atleta"),
    event_type: Optional[EventType] = Query(None, description="Filtrar por tipo de evento"),
    period: Optional[int] = Query(None, ge=1, le=2, description="Filtrar por período"),
    page: int = Query(1, ge=1, description="Número da página (1-indexed)"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página (máximo 100)"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
) -> MatchEventList:
    """
    Lista eventos do jogo (gols, faltas, etc.) de forma paginada.

    **Regras aplicáveis:**
    - R25/R26: Permissões por papel e escopo
    - RD1-RD91: Eventos estatísticos do handball

    **Paginação:**
    - page: Número da página (1-indexed)
    - limit: Itens por página (1-100, padrão 50)

    **Envelope de resposta:** {items, page, size, total, pages}
    """
    service = MatchEventService(db, context)
    events, total = await service.get_all_for_match(
        match_id,
        athlete_id=athlete_id,
        event_type=event_type,
        period=period,
        page=page,
        size=limit,
    )

    pages = (total + limit - 1) // limit if total > 0 else 0

    return MatchEventList(
        items=events,
        total=total,
        page=page,
        size=limit,
        pages=pages,
    )


@router.post(
    "/matches/{match_id}/events",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar evento ao jogo",
    operation_id="addEventToMatch",
    response_model=MatchEventResponse,
    responses={
        201: {"description": "Evento criado"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Jogo, equipe ou atleta não encontrado", "model": ErrorResponse},
        409: {
            "description": "Conflito (jogo finalizado ou temporada bloqueada)",
            "model": ErrorResponse,
        },
        422: {
            "description": "Erro de validação ou regra de goleira (RD13/RD22)",
            "model": ErrorResponse,
        },
    },
)
async def add_event_to_match(
    match_id: UUID,
    payload: MatchEventCreate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["admin", "coach"])),
) -> MatchEventResponse:
    """
    Adiciona um novo evento ao jogo (gol, falta, etc.).

    **Regras aplicáveis:**
    - RDB13: Bloquear se jogo finalizado → 409 edit_finalized_game
    - RD4: Atleta deve estar no roster do time
    - RF15: Partida não pode estar finalizada
    - R25/R26: Permissões por papel e escopo

    **Campo event_type (EventType enum):**
    goal, goal_7m, own_goal, shot, shot_on_target, save, goal_conceded,
    assist, yellow_card, red_card, two_minutes, turnover, technical_foul, etc.
    """
    # Garantir que o match_id do path é usado
    payload.match_id = match_id
    
    service = MatchEventService(db, context)
    event = await service.create(payload)
    db.commit()
    db.refresh(event)

    return MatchEventResponse.model_validate(event)


@router.patch(
    "/match_events/{match_event_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar evento do jogo",
    operation_id="updateMatchEvent",
    response_model=MatchEventResponse,
    responses={
        200: {"description": "Evento atualizado"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Match event não encontrado", "model": ErrorResponse},
        409: {"description": "Jogo finalizado (RDB13)", "model": ErrorResponse},
        422: {"description": "Erro de validação", "model": ErrorResponse},
    },
)
async def update_match_event(
    match_event_id: UUID,
    payload: MatchEventUpdate,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["admin", "coach"])),
) -> MatchEventResponse:
    """
    Atualiza atributos de um evento do jogo.

    **Campos editáveis:** event_type, minute, period, x_position, y_position, notes
    **Campos NÃO editáveis:** match_id, athlete_id

    **Regras aplicáveis:**
    - RDB13/RF15: Bloquear se jogo finalizado → 409 edit_finalized_game
    - R25/R26: Permissões por papel e escopo

    Para correções com histórico, use POST /match_events/{id}/correct
    """
    service = MatchEventService(db, context)
    event = await service.update(match_event_id, payload)
    db.commit()
    db.refresh(event)

    return MatchEventResponse.model_validate(event)


@router.post(
    "/match_events/{match_event_id}/correct",
    status_code=status.HTTP_200_OK,
    summary="Corrigir evento com histórico",
    operation_id="correctMatchEvent",
    response_model=MatchEventResponse,
    responses={
        200: {"description": "Evento corrigido com histórico"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente", "model": ErrorResponse},
        404: {"description": "Match event não encontrado", "model": ErrorResponse},
        422: {"description": "Justificativa obrigatória", "model": ErrorResponse},
    },
)
async def correct_match_event(
    match_event_id: UUID,
    payload: MatchEventCorrection,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["admin", "coach"])),
) -> MatchEventResponse:
    """
    Corrige evento com histórico obrigatório.
    
    **Regras aplicáveis:**
    - R23/R24: Correção com justificativa e registro de valor anterior

    Salva os valores anteriores em previous_value (JSON) e
    registra a justificativa em correction_note.
    """
    service = MatchEventService(db, context)
    event = await service.correct(match_event_id, payload)
    db.commit()
    db.refresh(event)

    return MatchEventResponse.model_validate(event)


@router.delete(
    "/match_events/{match_event_id}",
    status_code=status.HTTP_200_OK,
    summary="Excluir evento",
    operation_id="deleteMatchEvent",
    response_model=MatchEventResponse,
    responses={
        200: {"description": "Evento excluído (soft delete)"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Partida finalizada", "model": ErrorResponse},
        404: {"description": "Match event não encontrado", "model": ErrorResponse},
    },
)
async def delete_match_event(
    match_event_id: UUID,
    reason: str = Query(..., min_length=5, description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["admin", "coach"])),
) -> MatchEventResponse:
    """
    Soft delete de evento.
    
    **Regras aplicáveis:**
    - RDB3: Soft delete com deleted_at e deleted_reason
    - RF15: Partida não pode estar finalizada
    """
    service = MatchEventService(db, context)
    event = await service.soft_delete(match_event_id, reason)
    db.commit()
    db.refresh(event)

    return MatchEventResponse.model_validate(event)


@router.get(
    "/matches/{match_id}/stats/athlete/{athlete_id}",
    status_code=status.HTTP_200_OK,
    summary="Estatísticas do atleta na partida",
    operation_id="getAthleteMatchStats",
    response_model=AthleteMatchStats,
    responses={
        200: {"description": "Estatísticas agregadas do atleta"},
        404: {"description": "Partida ou atleta não encontrado", "model": ErrorResponse},
    },
)
async def get_athlete_match_stats(
    match_id: UUID,
    athlete_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(get_current_context),
) -> AthleteMatchStats:
    """
    Retorna estatísticas agregadas de um atleta em uma partida.
    
    **Regras aplicáveis:**
    - RD1-RD91: Agregação de eventos estatísticos
    
    Retorna gols, assistências, cartões, defesas, etc.
    """
    service = MatchEventService(db, context)
    stats = await service.get_athlete_stats(match_id, athlete_id)

    return stats


@router.post(
    "/matches/{match_id}/events/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Criar eventos em lote",
    operation_id="bulkCreateMatchEvents",
    response_model=list[MatchEventResponse],
    responses={
        201: {"description": "Eventos criados"},
        403: {"description": "Partida finalizada", "model": ErrorResponse},
        422: {"description": "Dados inválidos", "model": ErrorResponse},
    },
)
async def bulk_create_match_events(
    match_id: UUID,
    events: list[MatchEventCreate],
    db: AsyncSession = Depends(get_async_db),
    context: ExecutionContext = Depends(require_role(["admin"])),
) -> list[MatchEventResponse]:
    """
    Cria múltiplos eventos em lote.
    Útil para importação de súmula.
    """
    # Garantir que todos usam o match_id do path
    for event in events:
        event.match_id = match_id

    service = MatchEventService(db, context)
    created = await service.bulk_create(events)
    db.commit()

    return [MatchEventResponse.model_validate(e) for e in created]


# =============================================================================
# Rotas canônicas com escopo de equipe (/teams/{team_id}/matches/{match_id}/events)
# =============================================================================

@scoped_events_router.get(
    "/events",
    status_code=status.HTTP_200_OK,
    summary="Listar eventos do jogo (escopo equipe)",
    response_model=MatchEventList,
)
async def scoped_list_match_events(
    team_id: UUID,
    match_id: UUID,
    athlete_id: Optional[UUID] = Query(None, description="Filtrar por atleta"),
    event_type: Optional[EventType] = Query(None, description="Filtrar por tipo de evento"),
    period: Optional[int] = Query(None, ge=1, le=2, description="Filtrar por período"),
    page: int = Query(1, ge=1, description="Número da página (1-indexed)"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página (máximo 100)"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> MatchEventList:
    match = await _get_match_scoped(db, ctx, team_id, match_id)
    service = MatchEventService(db, ctx)
    events, total = await service.get_all_for_match(
        match_id,
        athlete_id=athlete_id,
        event_type=event_type,
        period=period,
        page=page,
        size=limit,
    )
    pages = (total + limit - 1) // limit if total > 0 else 0
    return MatchEventList(items=events, total=total, page=page, size=limit, pages=pages)


async def _maybe_validate_registration(
    db: AsyncSession,
    ctx: ExecutionContext,
    team_id: UUID,
    match: Match,
    athlete_id: Optional[UUID],
) -> None:
    if athlete_id and match.season_id:
        season = db.scalar(select(Season).where(Season.id == match.season_id))
        if season:
            require_team_registration_in_season(
                team_id=team_id,
                athlete_id=athlete_id,
                season_start=season.start_date,
                season_end=season.end_date,
                db=db,
                ctx=ctx,
            )


@scoped_events_router.post(
    "/events",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar evento ao jogo (escopo equipe)",
    response_model=MatchEventResponse,
)
async def scoped_add_event_to_match(
    team_id: UUID,
    match_id: UUID,
    payload: MatchEventCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin", "coach"], require_team=True)),
) -> MatchEventResponse:
    match = await _get_match_scoped(db, ctx, team_id, match_id)
    payload.match_id = match_id
    await _maybe_validate_registration(db, ctx, team_id, match, payload.athlete_id)
    service = MatchEventService(db, ctx)
    event = await service.create(payload)
    db.commit()
    db.refresh(event)
    return MatchEventResponse.model_validate(event)


@scoped_events_router.patch(
    "/match_events/{match_event_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar evento (escopo equipe)",
    response_model=MatchEventResponse,
)
async def scoped_update_match_event(
    team_id: UUID,
    match_id: UUID,
    match_event_id: UUID,
    payload: MatchEventUpdate,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin", "coach"], require_team=True)),
) -> MatchEventResponse:
    match = await _get_match_scoped(db, ctx, team_id, match_id)
    service = MatchEventService(db, ctx)
    event = await service.update(match_event_id, payload)
    if str(event.match_id) != str(match.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="permission_denied_team_scope")
    db.commit()
    db.refresh(event)
    return MatchEventResponse.model_validate(event)


@scoped_events_router.post(
    "/match_events/{match_event_id}/correct",
    status_code=status.HTTP_200_OK,
    summary="Corrigir evento (escopo equipe)",
    response_model=MatchEventResponse,
)
async def scoped_correct_match_event(
    team_id: UUID,
    match_id: UUID,
    match_event_id: UUID,
    payload: MatchEventCorrection,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin", "coach"], require_team=True)),
) -> MatchEventResponse:
    match = await _get_match_scoped(db, ctx, team_id, match_id)
    service = MatchEventService(db, ctx)
    event = await service.correct(match_event_id, payload)
    if str(event.match_id) != str(match.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="permission_denied_team_scope")
    db.commit()
    db.refresh(event)
    return MatchEventResponse.model_validate(event)


@scoped_events_router.delete(
    "/match_events/{match_event_id}",
    status_code=status.HTTP_200_OK,
    summary="Excluir evento (escopo equipe)",
    response_model=MatchEventResponse,
)
async def scoped_delete_match_event(
    team_id: UUID,
    match_id: UUID,
    match_event_id: UUID,
    reason: str = Query(..., min_length=5, description="Motivo da exclusão"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin", "coach"], require_team=True)),
) -> MatchEventResponse:
    match = await _get_match_scoped(db, ctx, team_id, match_id)
    service = MatchEventService(db, ctx)
    event = await service.soft_delete(match_event_id, reason)
    if str(event.match_id) != str(match.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="permission_denied_team_scope")
    db.commit()
    db.refresh(event)
    return MatchEventResponse.model_validate(event)


@scoped_events_router.get(
    "/stats/athlete/{athlete_id}",
    status_code=status.HTTP_200_OK,
    summary="Estatísticas do atleta na partida (escopo equipe)",
    response_model=AthleteMatchStats,
)
async def scoped_get_athlete_match_stats(
    team_id: UUID,
    match_id: UUID,
    athlete_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> AthleteMatchStats:
    match = await _get_match_scoped(db, ctx, team_id, match_id)
    await _maybe_validate_registration(db, ctx, team_id, match, athlete_id)
    service = MatchEventService(db, ctx)
    stats = await service.get_athlete_stats(match_id, athlete_id)
    return stats


@scoped_events_router.post(
    "/events/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Criar eventos em lote (escopo equipe)",
    response_model=list[MatchEventResponse],
)
async def scoped_bulk_create_match_events(
    team_id: UUID,
    match_id: UUID,
    events: list[MatchEventCreate],
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep(roles=["admin"], require_team=True)),
) -> list[MatchEventResponse]:
    match = await _get_match_scoped(db, ctx, team_id, match_id)
    for event in events:
        event.match_id = match_id
        await _maybe_validate_registration(db, ctx, team_id, match, event.athlete_id)
    service = MatchEventService(db, ctx)
    created = await service.bulk_create(events)
    db.commit()
    return [MatchEventResponse.model_validate(e) for e in created]
