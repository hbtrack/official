from __future__ import annotations
import uuid
from http import HTTPStatus
from typing import Optional
from datetime import datetime

from ninja import Router
from ninja.errors import HttpError

from matches.application.use_cases import (
    CreateMatch, CreateMatchInput,
    ListMatches, ListMatchesInput,
    GetMatch, PatchMatch, PatchMatchInput,
    AddPlayerToLineup, RemovePlayerFromLineup,
)
from matches.domain.rules import (
    RoleLabel, MatchNotFound, InsufficientPrivilege, MatchStateError,
)
from matches.infrastructure.repository import MatchRepository
from matches.schemas import (
    CreateMatchIn, ErrorOut, MatchListOut, MatchOut, PatchMatchIn,
)

router = Router(tags=["matches"])
_repo = MatchRepository()


def _role(request) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")


def _actor_id(request) -> uuid.UUID:
    """Extrai actor_id do JWT validado."""
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return uuid.UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")


@router.get(
    "",
    response={200: MatchListOut, 401: ErrorOut, 403: ErrorOut, 500: ErrorOut},
    operation_id="listMatches",
    summary="Lista partidas",
)
def list_matches(
    request,
    competitionId: Optional[uuid.UUID] = None,
    statusLabel: Optional[str] = None,
    homeTeamId: Optional[uuid.UUID] = None,
    awayTeamId: Optional[uuid.UUID] = None,
    page: int = 1,
    pageSize: int = 20,
):
    try:
        uc = ListMatches(_repo)
        data, total = uc.execute(ListMatchesInput(
            competition_id=competitionId,
            status_label=statusLabel,
            home_team_id=homeTeamId,
            away_team_id=awayTeamId,
            page=page,
            page_size=pageSize,
        ))
        return 200, MatchListOut(
            data=[MatchOut.from_domain(m) for m in data],
            page=page, pageSize=pageSize, total=total,
        )
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.post(
    "",
    response={201: MatchOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="createMatch",
    summary="Cria partida",
)
def create_match(request, payload: CreateMatchIn):
    try:
        uc = CreateMatch(_repo)
        match = uc.execute(CreateMatchInput(
            actor_role=_role(request),
            competition_id=payload.competitionId,
            home_team_id=payload.homeTeamId,
            away_team_id=payload.awayTeamId,
            scheduled_at=payload.scheduledAt,
            venue_label=payload.venueLabel,
            referee_names=payload.refereeNames,
        ))
        return 201, MatchOut.from_domain(match)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except ValueError as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.get(
    "/{match_id}",
    response={200: MatchOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 500: ErrorOut},
    operation_id="getMatch",
    summary="Obtém partida por ID",
)
def get_match(request, match_id: uuid.UUID):
    try:
        uc = GetMatch(_repo)
        match = uc.execute(match_id)
        return 200, MatchOut.from_domain(match)
    except MatchNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.patch(
    "/{match_id}",
    response={200: MatchOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="patchMatch",
    summary="Atualiza parcialmente a partida",
)
def patch_match(request, match_id: uuid.UUID, payload: PatchMatchIn):
    try:
        uc = PatchMatch(_repo)
        match = uc.execute(match_id, PatchMatchInput(
            actor_role=_role(request),
            venue_label=payload.venueLabel,
            status_label=payload.statusLabel,
            scheduled_at=payload.scheduledAt,
            started_at=payload.startedAt,
            ended_at=payload.endedAt,
            home_score=payload.homeScore,
            away_score=payload.awayScore,
            referee_names=payload.refereeNames,
            official_incident_ids=payload.officialIncidentIds,
        ))
        return 200, MatchOut.from_domain(match)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except MatchNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except (ValueError, MatchStateError) as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.put(
    "/{match_id}/lineup/{user_id}",
    response={200: MatchOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="addPlayerToLineup",
    summary="Adiciona atleta ao lineup",
)
def add_player_to_lineup(request, match_id: uuid.UUID, user_id: uuid.UUID):
    try:
        uc = AddPlayerToLineup(_repo)
        match = uc.execute(_role(request), match_id, user_id)
        return 200, MatchOut.from_domain(match)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except MatchNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except MatchStateError as exc:
        raise HttpError(HTTPStatus.CONFLICT, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.delete(
    "/{match_id}/lineup/{user_id}",
    response={200: MatchOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="removePlayerFromLineup",
    summary="Remove atleta do lineup",
)
def remove_player_from_lineup(request, match_id: uuid.UUID, user_id: uuid.UUID):
    try:
        uc = RemovePlayerFromLineup(_repo)
        match = uc.execute(_role(request), match_id, user_id)
        return 200, MatchOut.from_domain(match)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except MatchNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except MatchStateError as exc:
        raise HttpError(HTTPStatus.CONFLICT, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
