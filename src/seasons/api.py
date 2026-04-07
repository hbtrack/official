from __future__ import annotations

# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases  # noqa: F401
from .generated.infrastructure import repository as _gen_repository  # noqa: F401


"""
Router django-ninja — módulo seasons.
6 endpoints correspondentes aos 6 operationIds do contrato.
Contrato: contracts/openapi/paths/seasons.yaml
ADR-007 (JWT), ADR-008 (RBAC), ADR-031 (Django).
"""

from http import HTTPStatus
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError

from .application.use_cases import (
    AddTeamToSeasonInput,
    AddTeamToSeasonUseCase,
    CreateSeasonInput,
    CreateSeasonUseCase,
    GetSeasonInput,
    GetSeasonUseCase,
    ListSeasonsInput,
    ListSeasonsUseCase,
    PatchSeasonInput,
    PatchSeasonUseCase,
    RemoveTeamFromSeasonInput,
    RemoveTeamFromSeasonUseCase,
)
from .domain.rules import (
    DuplicateTeamAssociation,
    InsufficientPrivilege,
    InvalidDateRange,
    InvalidStatusTransition,
    RoleLabel,
    SeasonNotFound,
)
from .infrastructure.repository import SeasonsRepository
from .schemas import (
    CreateSeasonIn,
    PatchSeasonIn,
    SeasonListOut,
    SeasonOut,
)

router = Router(tags=["seasons"])

def _get_actor_role(request) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")

def _season_to_out(season) -> SeasonOut:
    return SeasonOut(
        id=season.id,
        name=season.name,
        start_date=season.start_date,
        end_date=season.end_date,
        status_label=season.status_label.value,
        phase_labels=season.phase_labels,
        team_ids=season.team_ids,
        competition_ids=season.competition_ids,
        organization_id=season.organization_id,
        sport_cycle_label=season.sport_cycle_label,
        created_at=season.created_at,
        updated_at=season.updated_at,
    )

# ---------------------------------------------------------------------------
# GET /seasons — listSeasons (FT-018)
# ---------------------------------------------------------------------------
@router.get("", response={200: SeasonListOut}, operation_id="listSeasons")
def list_seasons(
    request,
    status_label: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    actor_role = _get_actor_role(request)
    repo = SeasonsRepository()
    uc = ListSeasonsUseCase(repo)
    result = uc.execute(ListSeasonsInput(
        actor_role=actor_role,
        status_label=status_label,
        page=page,
        page_size=page_size,
    ))
    return {
        "data": [_season_to_out(s) for s in result.data],
        "page": result.page,
        "page_size": result.page_size,
        "total": result.total,
    }

# ---------------------------------------------------------------------------
# POST /seasons — createSeason (FT-019)
# ---------------------------------------------------------------------------
@router.post("", response={201: SeasonOut}, operation_id="createSeason")
def create_season(request, payload: CreateSeasonIn):
    actor_role = _get_actor_role(request)
    repo = SeasonsRepository()
    uc = CreateSeasonUseCase(repo)
    try:
        season = uc.execute(CreateSeasonInput(
            actor_role=actor_role,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            organization_id=payload.organization_id,
            sport_cycle_label=payload.sport_cycle_label,
            phase_labels=list(payload.phase_labels),
        ))
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except InvalidDateRange as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except ValueError as exc:
        raise HttpError(HTTPStatus.UNPROCESSABLE_ENTITY, str(exc))
    return HTTPStatus.CREATED, _season_to_out(season)

# ---------------------------------------------------------------------------
# GET /seasons/{seasonId} — getSeason (FT-020)
# ---------------------------------------------------------------------------
@router.get("/{season_id}", response={200: SeasonOut}, operation_id="getSeason")
def get_season(request, season_id: UUID):
    actor_role = _get_actor_role(request)
    repo = SeasonsRepository()
    uc = GetSeasonUseCase(repo)
    try:
        season = uc.execute(GetSeasonInput(actor_role=actor_role, season_id=season_id))
    except SeasonNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    return _season_to_out(season)

# ---------------------------------------------------------------------------
# PATCH /seasons/{seasonId} — patchSeason (FT-021)
# ---------------------------------------------------------------------------
@router.patch("/{season_id}", response={200: SeasonOut}, operation_id="patchSeason")
def patch_season(request, season_id: UUID, payload: PatchSeasonIn):
    actor_role = _get_actor_role(request)
    repo = SeasonsRepository()
    uc = PatchSeasonUseCase(repo)
    try:
        season = uc.execute(PatchSeasonInput(
            actor_role=actor_role,
            season_id=season_id,
            name=payload.name,
            sport_cycle_label=payload.sport_cycle_label,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status_label=payload.status_label,
            phase_labels=payload.phase_labels,
        ))
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except (InvalidDateRange, InvalidStatusTransition) as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except SeasonNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    return _season_to_out(season)

# ---------------------------------------------------------------------------
# POST /seasons/{seasonId}/teams/{teamId} — addTeamToSeason (FT-022)
# ---------------------------------------------------------------------------
@router.post(
    "/{season_id}/teams/{team_id}",
    response={204: None},
    operation_id="addTeamToSeason",
)
def add_team_to_season(request, season_id: UUID, team_id: UUID):
    actor_role = _get_actor_role(request)
    repo = SeasonsRepository()
    uc = AddTeamToSeasonUseCase(repo)
    try:
        uc.execute(AddTeamToSeasonInput(
            actor_role=actor_role,
            season_id=season_id,
            team_id=team_id,
        ))
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except DuplicateTeamAssociation as exc:
        raise HttpError(HTTPStatus.CONFLICT, str(exc))
    except SeasonNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    return HTTPStatus.NO_CONTENT, None

# ---------------------------------------------------------------------------
# DELETE /seasons/{seasonId}/teams/{teamId} — removeTeamFromSeason (FT-023)
# ---------------------------------------------------------------------------
@router.delete(
    "/{season_id}/teams/{team_id}",
    response={204: None},
    operation_id="removeTeamFromSeason",
)
def remove_team_from_season(request, season_id: UUID, team_id: UUID):
    actor_role = _get_actor_role(request)
    repo = SeasonsRepository()
    uc = RemoveTeamFromSeasonUseCase(repo)
    try:
        uc.execute(RemoveTeamFromSeasonInput(
            actor_role=actor_role,
            season_id=season_id,
            team_id=team_id,
        ))
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except SeasonNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    return HTTPStatus.NO_CONTENT, None
