from __future__ import annotations
import uuid
from datetime import date
from decimal import Decimal
from http import HTTPStatus
from typing import Optional

from ninja import Router
from ninja.errors import HttpError

from wellness.application.use_cases import (
    CreateWellnessEntry, CreateWellnessEntryInput,
    GetWellnessEntry, ListWellnessEntries, ListWellnessEntriesInput,
    ListAthleteWellnessEntries, ListAthleteWellnessEntriesInput,
    GetAthleteWellnessSummary,
)
from wellness.domain.rules import (
    RoleLabel, WellnessEntryNotFound, InsufficientPrivilege,
)
from wellness.infrastructure.repository import WellnessEntryRepository
from wellness.schemas import (
    CreateWellnessEntryIn, ErrorOut, WellnessEntryListOut,
    WellnessEntryOut, WellnessSummaryOut,
)

router = Router(tags=["wellness"])
_repo = WellnessEntryRepository()


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


# POST /wellness/entries
@router.post(
    "/entries",
    response={201: WellnessEntryOut, 400: ErrorOut, 403: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="createWellnessEntry",
    summary="Registra entrada de wellness diário",
)
def create_wellness_entry(request, payload: CreateWellnessEntryIn):
    try:
        uc = CreateWellnessEntry(_repo)
        entry = uc.execute(CreateWellnessEntryInput(
            actor_role=_role(request),
            actor_user_id=_actor_id(request),
            athlete_user_id=payload.athleteUserId,
            training_session_id=payload.trainingSessionId,
            questionnaire_date=payload.questionnaireDate,
            questionnaire_label=payload.questionnaireLabel,
            readiness_score=payload.readinessScore,
            fatigue_score=payload.fatigueScore,
            pain_score=payload.painScore,
            recovery_score=payload.recoveryScore,
            sleep_hours=payload.sleepHours,
            notes=payload.notes,
        ))
        return 201, WellnessEntryOut.from_domain(entry)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except ValueError as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# GET /wellness/entries
@router.get(
    "/entries",
    response={200: WellnessEntryListOut, 403: ErrorOut, 500: ErrorOut},
    operation_id="listWellnessEntries",
    summary="Lista entradas de wellness",
)
def list_wellness_entries(
    request,
    athleteUserId: Optional[uuid.UUID] = None,
    questionnaireDate: Optional[date] = None,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
    questionnaireLabel: Optional[str] = None,
    page: int = 1,
    pageSize: int = 20,
):
    try:
        uc = ListWellnessEntries(_repo)
        result = uc.execute(ListWellnessEntriesInput(
            actor_role=_role(request),
            actor_user_id=_actor_id(request),
            athlete_user_id=athleteUserId,
            questionnaire_date=questionnaireDate,
            date_from=dateFrom,
            date_to=dateTo,
            questionnaire_label=questionnaireLabel,
            page=page,
            page_size=pageSize,
        ))
        return 200, WellnessEntryListOut(
            data=[WellnessEntryOut.from_domain(e) for e in result.data],
            page=result.page,
            pageSize=result.page_size,
            total=result.total,
        )
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# GET /wellness/entries/{entryId}
@router.get(
    "/entries/{entry_id}",
    response={200: WellnessEntryOut, 403: ErrorOut, 404: ErrorOut, 500: ErrorOut},
    operation_id="getWellnessEntry",
    summary="Obtém entrada de wellness por ID",
)
def get_wellness_entry(request, entry_id: uuid.UUID):
    try:
        uc = GetWellnessEntry(_repo)
        entry = uc.execute(_role(request), _actor_id(request), entry_id)
        return 200, WellnessEntryOut.from_domain(entry)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except WellnessEntryNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# GET /wellness/athletes/{athleteUserId}/entries
@router.get(
    "/athletes/{athlete_user_id}/entries",
    response={200: WellnessEntryListOut, 403: ErrorOut, 404: ErrorOut, 500: ErrorOut},
    operation_id="listAthleteWellnessEntries",
    summary="Lista entradas de wellness de um atleta",
)
def list_athlete_wellness_entries(
    request,
    athlete_user_id: uuid.UUID,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
    questionnaireLabel: Optional[str] = None,
    page: int = 1,
    pageSize: int = 20,
):
    try:
        uc = ListAthleteWellnessEntries(_repo)
        result = uc.execute(ListAthleteWellnessEntriesInput(
            actor_role=_role(request),
            actor_user_id=_actor_id(request),
            target_athlete_id=athlete_user_id,
            date_from=dateFrom,
            date_to=dateTo,
            questionnaire_label=questionnaireLabel,
            page=page,
            page_size=pageSize,
        ))
        return 200, WellnessEntryListOut(
            data=[WellnessEntryOut.from_domain(e) for e in result.data],
            page=result.page,
            pageSize=result.page_size,
            total=result.total,
        )
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


# GET /wellness/athletes/{athleteUserId}/summary
@router.get(
    "/athletes/{athlete_user_id}/summary",
    response={200: WellnessSummaryOut, 403: ErrorOut, 404: ErrorOut, 500: ErrorOut},
    operation_id="getAthleteWellnessSummary",
    summary="Obtém resumo de wellness do atleta",
)
def get_athlete_wellness_summary(
    request,
    athlete_user_id: uuid.UUID,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
):
    try:
        uc = GetAthleteWellnessSummary(_repo)
        summary = uc.execute(
            _role(request), _actor_id(request),
            athlete_user_id, dateFrom, dateTo,
        )
        return 200, WellnessSummaryOut.from_domain(summary)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
