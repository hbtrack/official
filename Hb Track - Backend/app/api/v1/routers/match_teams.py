"""
Router para Match Teams.

Rotas canônicas:
/teams/{team_id}/matches/{match_id}/teams[...]

Campos do banco (match_teams):
- id, match_id, team_id, is_home (NOT NULL), is_our_team (NOT NULL)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import permission_dep
from app.core.context import ExecutionContext
from app.core.db import get_db
from app.models.match import Match
from app.models.match_teams import MatchTeams as MatchTeamsModel
from app.models.season import Season
from app.models.team import Team
from app.schemas.matches_subresources import (
    MatchTeam,
    MatchTeamCreate,
    MatchTeamUpdate,
)
from app.schemas.error import ErrorResponse

router = APIRouter(tags=["match-teams"])
scoped_router = APIRouter(prefix="/teams/{team_id}/matches/{match_id}", tags=["match-teams"])


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


# DEPRECATED: usar rotas canônicas em /teams/{team_id}/matches/{match_id}/teams
@router.get(
    "/matches/{match_id}/teams",
    status_code=status.HTTP_200_OK,
    summary="Listar equipes do jogo",
    response_model=list[MatchTeam],
    responses={
        200: {"description": "Lista de equipes do jogo"},
        401: {"description": "Token inválido ou ausente", "model": ErrorResponse},
        403: {"description": "Permissão insuficiente (R25/R26)", "model": ErrorResponse},
        404: {"description": "Jogo não encontrado", "model": ErrorResponse},
    },
)
def list_match_teams(
    match_id: UUID,
    db: Session = Depends(get_db),
) -> list[MatchTeam]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="deprecated_use_scoped_routes")


# DEPRECATED
@router.post(
    "/matches/{match_id}/teams",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar equipe ao jogo",
    response_model=MatchTeam,
)
def add_team_to_match(
    match_id: UUID,
    payload: MatchTeamCreate,
    db: Session = Depends(get_db),
) -> MatchTeam:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="deprecated_use_scoped_routes")


# DEPRECATED
@router.patch(
    "/match_teams/{match_team_id}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar equipe do jogo",
    response_model=MatchTeam,
)
def update_match_team(
    match_team_id: UUID,
    payload: MatchTeamUpdate,
    db: Session = Depends(get_db),
) -> MatchTeam:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="deprecated_use_scoped_routes")


# =============================================================================
# Rotas canônicas com escopo de equipe (/teams/{team_id}/matches/{match_id}/teams)
# =============================================================================

@scoped_router.get(
    "/teams",
    status_code=status.HTTP_200_OK,
    summary="Listar equipes do jogo (escopo equipe)",
    response_model=list[MatchTeam],
)
async def scoped_list_match_teams(
    team_id: UUID,
    match_id: UUID,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> list[MatchTeam]:
    match = _get_match_scoped(db, ctx, team_id, match_id)
    
    query = (
        select(MatchTeamsModel)
        .where(MatchTeamsModel.match_id == match_id)
    )
    team_entries = db.execute(query).scalars().all()
    return [MatchTeam.model_validate(t) for t in team_entries]


@scoped_router.post(
    "/teams",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar equipe ao jogo (escopo equipe)",
    response_model=MatchTeam,
)
async def scoped_add_team_to_match(
    team_id: UUID,
    match_id: UUID,
    payload: MatchTeamCreate,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> MatchTeam:
    match = _get_match_scoped(db, ctx, team_id, match_id)
    
    # Verificar duplicata (match_id + team_id)
    existing = db.execute(
        select(MatchTeamsModel)
        .where(
            MatchTeamsModel.match_id == match_id,
            MatchTeamsModel.team_id == payload.team_id,
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="team_already_in_match"
        )
    
    # Criar entrada
    team_entry = MatchTeamsModel(
        match_id=match_id,
        team_id=payload.team_id,
        is_home=payload.is_home,
        is_our_team=payload.is_our_team,
    )
    db.add(team_entry)
    db.commit()
    db.refresh(team_entry)
    return MatchTeam.model_validate(team_entry)


@scoped_router.patch(
    "/teams/{side}",
    status_code=status.HTTP_200_OK,
    summary="Atualizar equipe do jogo por lado (escopo equipe)",
    response_model=MatchTeam,
)
async def scoped_update_match_team(
    team_id: UUID,
    match_id: UUID,
    side: str,
    payload: MatchTeamUpdate,
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(permission_dep(require_team=True)),
) -> MatchTeam:
    match = _get_match_scoped(db, ctx, team_id, match_id)
    
    # side deve ser 'home' ou 'away'
    if side not in ('home', 'away'):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="side_must_be_home_or_away"
        )
    
    is_home = (side == 'home')
    
    # Buscar entrada por is_home
    team_entry = db.execute(
        select(MatchTeamsModel)
        .where(
            MatchTeamsModel.match_id == match_id,
            MatchTeamsModel.is_home == is_home,
        )
    ).scalar_one_or_none()
    
    if not team_entry:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="match_team_not_found")
    
    # Atualizar campos
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team_entry, key, value)
    
    db.commit()
    db.refresh(team_entry)
    return MatchTeam.model_validate(team_entry)
