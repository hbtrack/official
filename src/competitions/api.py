"""
Router HTTP — módulo competitions (Django Ninja).
Fonte: contracts/openapi/paths/competitions.yaml
RBAC: PERMISSIONS_COMPETITIONS.md
ADR-007 (JWT RS256), ADR-008 (RBAC 5 roles), ADR-031 (Django Ninja)
"""
from __future__ import annotations

import uuid
from http import HTTPStatus
from typing import Optional

from ninja import Router
from ninja.errors import HttpError

from competitions.application.use_cases import (
    CreateCompetition,
    CreateCompetitionInput,
    GetCompetition,
    ListCompetitions,
    ListCompetitionsInput,
    PatchCompetition,
    PatchCompetitionInput,
    RegisterTeamInCompetition,
    UnregisterTeamFromCompetition,
)
from competitions.domain.rules import (
    CompetitionNotFound,
    InsufficientPrivilege,
    InvalidStatusTransition,
    RoleLabel,
    TeamAlreadyRegistered,
    TeamNotRegistered,
)
from competitions.infrastructure.repository import CompetitionRepository
from competitions.schemas import (
    CompetitionListOut,
    CompetitionOut,
    CreateCompetitionIn,
    ErrorOut,
    PatchCompetitionIn,
)

router = Router(tags=["competitions"])
_repo = CompetitionRepository()


def _role(request) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")


# ---------------------------------------------------------------------------
# GET /competitions
# ---------------------------------------------------------------------------

@router.get(
    "",
    response={200: CompetitionListOut, 401: ErrorOut, 403: ErrorOut, 500: ErrorOut},
    operation_id="listCompetitions",
    summary="Lista competições",
)
def list_competitions(
    request,
    seasonId: Optional[uuid.UUID] = None,
    organizationId: Optional[uuid.UUID] = None,
    statusLabel: Optional[str] = None,
    page: int = 1,
    pageSize: int = 20,
):
    try:
        uc = ListCompetitions(_repo)
        result = uc.execute(ListCompetitionsInput(
            actor_role=_role(request),
            season_id=seasonId,
            organization_id=organizationId,
            status_label=statusLabel,
            page=page,
            page_size=pageSize,
        ))
        return 200, CompetitionListOut(
            data=[CompetitionOut.from_domain(c) for c in result.data],
            page=result.page,
            pageSize=result.page_size,
            total=result.total,
        )
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# ---------------------------------------------------------------------------
# POST /competitions
# ---------------------------------------------------------------------------

@router.post(
    "",
    response={201: CompetitionOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="createCompetition",
    summary="Cria competição",
)
def create_competition(request, payload: CreateCompetitionIn):
    try:
        uc = CreateCompetition(_repo)
        comp = uc.execute(CreateCompetitionInput(
            actor_role=_role(request),
            season_id=payload.seasonId,
            organization_id=payload.organizationId,
            name=payload.name,
            start_date=payload.startDate,
            end_date=payload.endDate,
            format_label=payload.formatLabel,
            stage_labels=list(payload.stageLabels),
            registration_team_ids=list(payload.registrationTeamIds),
        ))
        return 201, CompetitionOut.from_domain(comp)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except ValueError as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# ---------------------------------------------------------------------------
# GET /competitions/{competitionId}
# ---------------------------------------------------------------------------

@router.get(
    "/{competition_id}",
    response={200: CompetitionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 500: ErrorOut},
    operation_id="getCompetition",
    summary="Obter competição por ID",
)
def get_competition(request, competition_id: uuid.UUID):
    try:
        uc = GetCompetition(_repo)
        comp = uc.execute(_role(request), competition_id)
        return 200, CompetitionOut.from_domain(comp)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except CompetitionNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# ---------------------------------------------------------------------------
# PATCH /competitions/{competitionId}
# ---------------------------------------------------------------------------

@router.patch(
    "/{competition_id}",
    response={200: CompetitionOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut,
              409: ErrorOut, 500: ErrorOut},
    operation_id="patchCompetition",
    summary="Atualizar competição",
)
def patch_competition(request, competition_id: uuid.UUID, payload: PatchCompetitionIn):
    try:
        uc = PatchCompetition(_repo)
        comp = uc.execute(PatchCompetitionInput(
            actor_role=_role(request),
            competition_id=competition_id,
            name=payload.name,
            start_date=payload.startDate,
            end_date=payload.endDate,
            format_label=payload.formatLabel,
            status_label=payload.statusLabel,
            stage_labels=payload.stageLabels,
            standings_summary=payload.standingsSummary,
        ))
        return 200, CompetitionOut.from_domain(comp)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except (ValueError, InvalidStatusTransition) as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except CompetitionNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# ---------------------------------------------------------------------------
# POST /competitions/{competitionId}/teams/{teamId}
# ---------------------------------------------------------------------------

@router.post(
    "/{competition_id}/teams/{team_id}",
    response={204: None, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut,
              409: ErrorOut, 500: ErrorOut},
    operation_id="registerTeamInCompetition",
    summary="Inscrever equipe na competição",
)
def register_team(request, competition_id: uuid.UUID, team_id: uuid.UUID):
    try:
        uc = RegisterTeamInCompetition(_repo)
        uc.execute(_role(request), competition_id, team_id)
        return 204, None
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except TeamAlreadyRegistered as exc:
        raise HttpError(HTTPStatus.CONFLICT, str(exc))
    except CompetitionNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# ---------------------------------------------------------------------------
# DELETE /competitions/{competitionId}/teams/{teamId}
# ---------------------------------------------------------------------------

@router.delete(
    "/{competition_id}/teams/{team_id}",
    response={204: None, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="unregisterTeamFromCompetition",
    summary="Remover equipe da competição",
)
def unregister_team(request, competition_id: uuid.UUID, team_id: uuid.UUID):
    try:
        uc = UnregisterTeamFromCompetition(_repo)
        uc.execute(_role(request), competition_id, team_id)
        return 204, None
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except (TeamNotRegistered, CompetitionNotFound) as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
