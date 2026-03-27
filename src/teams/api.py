"""
Router django-ninja — módulo teams.
8 endpoints correspondentes aos 8 operationIds do contrato.
Contrato: contracts/openapi/paths/teams.yaml
ADR-007 (JWT), ADR-008 (RBAC), ADR-031 (Django).
"""
from __future__ import annotations

from uuid import UUID

from ninja import Router
from ninja.errors import HttpError

from .application.use_cases import (
    AddAthleteToTeamInput,
    AddAthleteToTeamUseCase,
    AddStaffToTeamInput,
    AddStaffToTeamUseCase,
    CreateTeamInput,
    CreateTeamUseCase,
    GetTeamInput,
    GetTeamUseCase,
    ListTeamsInput,
    ListTeamsUseCase,
    PatchTeamInput,
    PatchTeamUseCase,
    RemoveAthleteFromTeamInput,
    RemoveAthleteFromTeamUseCase,
    RemoveStaffFromTeamInput,
    RemoveStaffFromTeamUseCase,
)
from .domain.rules import (
    InsufficientPrivilege,
    InvalidStatusTransition,
    RoleLabel,
    TeamNotFound,
)
from .infrastructure.repository import TeamsRepository
from .schemas import (
    CreateTeamIn,
    PatchTeamIn,
    TeamListOut,
    TeamOut,
)

router = Router(tags=["teams"])


def _get_actor_role(request) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")


def _get_actor_team_ids(request) -> list[UUID]:
    """
    Stub: retorna lista de team_ids do actor (coach/athlete).
    Substituir por integração real com identity_access.
    """
    return getattr(request, "_actor_team_ids", [])


def _team_to_out(team) -> TeamOut:
    return TeamOut(
        id=team.id,
        organization_id=team.organization_id,
        name=team.name,
        category_label=team.category_label,
        status_label=team.status_label.value,
        season_id=team.season_id,
        short_name=team.short_name,
        athlete_ids=team.athlete_ids,
        staff_user_ids=team.staff_user_ids,
        roster_notes=team.roster_notes,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )


# ---------------------------------------------------------------------------
# GET /teams — listTeams (FT-024)
# ---------------------------------------------------------------------------
@router.get("", response={200: TeamListOut}, operation_id="listTeams")
def list_teams(
    request,
    organization_id: UUID | None = None,
    season_id: UUID | None = None,
    category_label: str | None = None,
    status_label: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    actor_team_ids = _get_actor_team_ids(request)
    try:
        result = ListTeamsUseCase(repo).execute(
            ListTeamsInput(
                actor_role=actor_role,
                actor_team_ids=actor_team_ids,
                organization_id=organization_id,
                season_id=season_id,
                category_label=category_label,
                status_label=status_label,
                page=page,
                page_size=page_size,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, TeamListOut(
        data=[_team_to_out(t) for t in result.data],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


# ---------------------------------------------------------------------------
# POST /teams — createTeam (FT-025)
# ---------------------------------------------------------------------------
@router.post("", response={201: TeamOut}, operation_id="createTeam")
def create_team(request, payload: CreateTeamIn):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    try:
        team = CreateTeamUseCase(repo).execute(
            CreateTeamInput(
                actor_role=actor_role,
                organization_id=payload.organization_id,
                name=payload.name,
                category_label=payload.category_label,
                season_id=payload.season_id,
                short_name=payload.short_name,
                athlete_ids=payload.athlete_ids,
                staff_user_ids=payload.staff_user_ids,
                roster_notes=payload.roster_notes,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(422, str(exc))
    return 201, _team_to_out(team)


# ---------------------------------------------------------------------------
# GET /teams/{teamId} — getTeam (FT-026)
# ---------------------------------------------------------------------------
@router.get("/{team_id}", response={200: TeamOut}, operation_id="getTeam")
def get_team(request, team_id: UUID):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    actor_team_ids = _get_actor_team_ids(request)
    try:
        team = GetTeamUseCase(repo).execute(
            GetTeamInput(
                actor_role=actor_role,
                actor_team_ids=actor_team_ids,
                team_id=team_id,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except TeamNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, _team_to_out(team)


# ---------------------------------------------------------------------------
# PATCH /teams/{teamId} — patchTeam (FT-027)
# ---------------------------------------------------------------------------
@router.patch("/{team_id}", response={200: TeamOut}, operation_id="patchTeam")
def patch_team(request, team_id: UUID, payload: PatchTeamIn):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    actor_team_ids = _get_actor_team_ids(request)
    try:
        team = PatchTeamUseCase(repo).execute(
            PatchTeamInput(
                actor_role=actor_role,
                actor_team_ids=actor_team_ids,
                team_id=team_id,
                name=payload.name,
                category_label=payload.category_label,
                season_id=payload.season_id,
                short_name=payload.short_name,
                roster_notes=payload.roster_notes,
                status_label=payload.status_label,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except TeamNotFound as exc:
        raise HttpError(404, str(exc))
    except InvalidStatusTransition as exc:
        raise HttpError(422, str(exc))
    return 200, _team_to_out(team)


# ---------------------------------------------------------------------------
# POST /teams/{teamId}/athletes/{athleteUserId} — addAthleteToTeam (FT-028)
# Idempotente; retorna 200 com Team body (não 204).
# ---------------------------------------------------------------------------
@router.post("/{team_id}/athletes/{athlete_user_id}", response={200: TeamOut}, operation_id="addAthleteToTeam")
def add_athlete_to_team(request, team_id: UUID, athlete_user_id: UUID):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    actor_team_ids = _get_actor_team_ids(request)
    try:
        team = AddAthleteToTeamUseCase(repo).execute(
            AddAthleteToTeamInput(
                actor_role=actor_role,
                actor_team_ids=actor_team_ids,
                team_id=team_id,
                athlete_user_id=athlete_user_id,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except TeamNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, _team_to_out(team)


# ---------------------------------------------------------------------------
# DELETE /teams/{teamId}/athletes/{athleteUserId} — removeAthleteFromTeam (FT-029)
# Idempotente; retorna 200 com Team body (não 204).
# ---------------------------------------------------------------------------
@router.delete("/{team_id}/athletes/{athlete_user_id}", response={200: TeamOut}, operation_id="removeAthleteFromTeam")
def remove_athlete_from_team(request, team_id: UUID, athlete_user_id: UUID):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    actor_team_ids = _get_actor_team_ids(request)
    try:
        team = RemoveAthleteFromTeamUseCase(repo).execute(
            RemoveAthleteFromTeamInput(
                actor_role=actor_role,
                actor_team_ids=actor_team_ids,
                team_id=team_id,
                athlete_user_id=athlete_user_id,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except TeamNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, _team_to_out(team)


# ---------------------------------------------------------------------------
# POST /teams/{teamId}/staff/{staffUserId} — addStaffToTeam (FT-030)
# Idempotente; retorna 200 com Team body (não 204).
# ---------------------------------------------------------------------------
@router.post("/{team_id}/staff/{staff_user_id}", response={200: TeamOut}, operation_id="addStaffToTeam")
def add_staff_to_team(request, team_id: UUID, staff_user_id: UUID):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    try:
        team = AddStaffToTeamUseCase(repo).execute(
            AddStaffToTeamInput(
                actor_role=actor_role,
                team_id=team_id,
                staff_user_id=staff_user_id,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except TeamNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, _team_to_out(team)


# ---------------------------------------------------------------------------
# DELETE /teams/{teamId}/staff/{staffUserId} — removeStaffFromTeam (FT-031)
# Idempotente; retorna 200 com Team body (não 204).
# ---------------------------------------------------------------------------
@router.delete("/{team_id}/staff/{staff_user_id}", response={200: TeamOut}, operation_id="removeStaffFromTeam")
def remove_staff_from_team(request, team_id: UUID, staff_user_id: UUID):
    repo = TeamsRepository()
    actor_role = _get_actor_role(request)
    try:
        team = RemoveStaffFromTeamUseCase(repo).execute(
            RemoveStaffFromTeamInput(
                actor_role=actor_role,
                team_id=team_id,
                staff_user_id=staff_user_id,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except TeamNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, _team_to_out(team)
