"""
Router para Match Roster.

Rotas canônicas:
/teams/{team_id}/matches/{match_id}/roster[...]

Campos do banco (match_roster):
- id, match_id, team_id, athlete_id, jersey_number (>0), is_starting, is_goalkeeper, is_available, notes
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext
from app.core.db import get_db
from app.core.permissions import require_team_registration_in_season
from app.models.match import Match
from app.models.match_roster import MatchRoster as MatchRosterModel
from app.models.season import Season
from app.models.team import Team
from app.schemas.matches_subresources import (
    MatchRoster,
    MatchRosterCreate,
    MatchRosterUpdate,
)
from app.schemas.error import ErrorResponse

router = APIRouter(tags=["match-roster"])
scoped_router = APIRouter(prefix="/teams/{team_id}/matches/{match_id}", tags=["match-roster"])


def _get_match_scoped(db: Session, ctx: ExecutionContext, team_id: UUID, match_id: UUID) -> Match:
    """
    Busca match verificando escopo via season -> team -> organization.
    Match pertence a team via: match.season_id -> season.team_id.
    """
    query = (
        select(Match)
        .join(Season, Season.id == Match.season_id)
        .join(Team, Team.id == Season.team_id)
        .where(Match.id == match_id, Season.team_id == team_id)
    )
    if not ctx.is_superadmin:
        query = query.where(Team.organization_id == ctx.organization_id)
    query = query.where(Match.deleted_at.is_(None))
    match = db.execute(query).scalar_one_or_none()
    if not match:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="match_not_found")
    return match


def _maybe_validate_registration(
    db: Session,
    ctx: ExecutionContext,
    team_id: UUID,
    match: Match,
    athlete_id: UUID | None,
) -> None:
    """Valida inscrição do atleta na temporada do jogo."""
    if athlete_id and match.season_id:
        season = db.get(Season, str(match.season_id))
        if season:
            require_team_registration_in_season(
                team_id=team_id,
                athlete_id=athlete_id,
                season_start=season.start_date,
                season_end=season.end_date,
                db=db,
                ctx=ctx,
            )


# DEPRECATED: usar rotas canônicas em /teams/{team_id}/matches/{match_id}/roster
@router.get(
    "/matches/{match_id}/roster",
    status_code=status.HTTP_200_OK,
    summary="Listar roster do jogo",
    response_model=list[MatchRoster],
    responses={
        200: {"description": "Lista de atletas do jogo"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Jogo não encontrado", "model": ErrorResponse},
    },
)
def list_match_roster(
    match_id: UUID,
    db: Session = Depends(get_db),
) -> list[MatchRoster]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="deprecated_use_scoped_routes")


# DEPRECATED
@router.post(
    "/matches/{match_id}/roster",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar atleta ao roster",
    response_model=MatchRoster,
)
def add_athlete_to_match(
    match_id: UUID,
    payload: MatchRosterCreate,
    db: Session = Depends(get_db),
) -> MatchRoster:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="deprecated_use_scoped_routes")


# DEPRECATED
@router.patch(
    "/match_roster/{match_roster_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar entrada do roster",
    response_model=MatchRoster,
)
def update_match_roster(
    match_roster_id: UUID,
    payload: MatchRosterUpdate,
    db: Session = Depends(get_db),
) -> MatchRoster:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="deprecated_use_scoped_routes")


# =============================================================================
# Rotas canônicas com escopo de equipe (/teams/{team_id}/matches/{match_id}/roster)
# =============================================================================

@scoped_router.get(
    "/roster",
    status_code=status.HTTP_200_OK,
    summary="Listar roster do jogo (escopo equipe)",
    response_model=list[MatchRoster],
)
async def scoped_list_match_roster(
    team_id: UUID,
    match_id: UUID,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> list[MatchRoster]:
    match = _get_match_scoped(db, ctx, team_id, match_id)
    
    query = (
        select(MatchRosterModel)
        .where(
            MatchRosterModel.match_id == match_id,
            MatchRosterModel.team_id == team_id,
        )
    )
    roster_entries = db.execute(query).scalars().all()
    return [MatchRoster.model_validate(r) for r in roster_entries]


@scoped_router.post(
    "/roster",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar atleta ao roster (escopo equipe)",
    response_model=MatchRoster,
)
async def scoped_add_athlete_to_match(
    team_id: UUID,
    match_id: UUID,
    payload: MatchRosterCreate,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> MatchRoster:
    match = _get_match_scoped(db, ctx, team_id, match_id)
    
    # Validar inscrição na temporada
    _maybe_validate_registration(db, ctx, team_id, match, payload.athlete_id)
    
    # Verificar duplicata
    existing = db.execute(
        select(MatchRosterModel)
        .where(
            MatchRosterModel.match_id == match_id,
            MatchRosterModel.athlete_id == payload.athlete_id,
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="athlete_already_in_roster"
        )
    
    # RD18: máximo 16 atletas por jogo
    count = db.execute(
        select(MatchRosterModel)
        .where(MatchRosterModel.match_id == match_id)
    ).scalars().all()
    if len(count) >= 16:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="max_roster_size_exceeded"
        )
    
    # Criar entrada
    roster_entry = MatchRosterModel(
        match_id=match_id,
        team_id=team_id,
        athlete_id=payload.athlete_id,
        jersey_number=payload.jersey_number,
        is_goalkeeper=payload.is_goalkeeper,
        is_available=payload.is_available,
        is_starting=payload.is_starting,
        notes=payload.notes,
    )
    db.add(roster_entry)
    db.commit()
    db.refresh(roster_entry)
    return MatchRoster.model_validate(roster_entry)


@scoped_router.patch(
    "/roster/{roster_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar entrada do roster (escopo equipe)",
    response_model=MatchRoster,
)
async def scoped_update_match_roster(
    team_id: UUID,
    match_id: UUID,
    roster_id: UUID,
    payload: MatchRosterUpdate,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> MatchRoster:
    match = _get_match_scoped(db, ctx, team_id, match_id)
    
    # Buscar entrada
    roster_entry = db.execute(
        select(MatchRosterModel)
        .where(
            MatchRosterModel.id == roster_id,
            MatchRosterModel.match_id == match_id,
            MatchRosterModel.team_id == team_id,
        )
    ).scalar_one_or_none()
    if not roster_entry:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="roster_entry_not_found")
    
    # Atualizar campos
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(roster_entry, key, value)
    
    db.commit()
    db.refresh(roster_entry)
    return MatchRoster.model_validate(roster_entry)


@scoped_router.delete(
    "/roster/{athlete_id}",
    status_code=status.HTTP_200_OK,
    summary="Remover atleta do roster (escopo equipe)",
    response_model=dict,
)
async def scoped_delete_from_roster(
    team_id: UUID,
    match_id: UUID,
    athlete_id: UUID,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> dict:
    match = _get_match_scoped(db, ctx, team_id, match_id)
    
    # Buscar entrada pelo athlete_id
    roster_entry = db.execute(
        select(MatchRosterModel)
        .where(
            MatchRosterModel.match_id == match_id,
            MatchRosterModel.team_id == team_id,
            MatchRosterModel.athlete_id == athlete_id,
        )
    ).scalar_one_or_none()
    if not roster_entry:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="athlete_not_in_roster")
    
    # Hard delete (match_roster não tem soft delete)
    db.delete(roster_entry)
    db.commit()
    return {"detail": "athlete_removed_from_roster"}
