from __future__ import annotations
import uuid
from http import HTTPStatus
from typing import List, Optional
from datetime import date

from ninja import Router
from ninja.errors import HttpError

from medical.application.use_cases import (
    CreateMedicalRecord, CreateMedicalRecordInput,
    ListMedicalRecords, ListMedicalRecordsInput,
    GetMedicalRecord, UpdateMedicalRecord, UpdateMedicalRecordInput,
    DeleteMedicalRecord,
)
from medical.domain.rules import (
    RoleLabel, MedicalRecordNotFound, InsufficientPrivilege,
)
from medical.infrastructure.repository import MedicalRecordRepository
from medical.schemas import (
    CreateMedicalRecordIn, ErrorOut, MedicalRecordListOut,
    MedicalRecordOut, UpdateMedicalRecordIn,
)

router = Router(tags=["medical"])
_repo = MedicalRecordRepository()


def _role(request) -> RoleLabel:
    val = getattr(request, "auth", None)
    if val is None:
        return RoleLabel.MEMBER
    if isinstance(val, dict):
        return RoleLabel(val.get("role", "member"))
    return RoleLabel(getattr(val, "role", "member"))


def _actor_id(request) -> uuid.UUID:
    val = getattr(request, "auth", None)
    if val is None:
        return uuid.uuid4()
    if isinstance(val, dict):
        return uuid.UUID(val.get("sub", str(uuid.uuid4())))
    return uuid.UUID(str(getattr(val, "sub", uuid.uuid4())))


@router.get(
    "/records",
    response={200: MedicalRecordListOut, 403: ErrorOut, 422: ErrorOut, 500: ErrorOut},
    operation_id="listMedicalRecords",
    summary="Lista registros médicos",
)
def list_medical_records(
    request,
    athleteUserId: Optional[uuid.UUID] = None,
    teamId: Optional[uuid.UUID] = None,
    recordDateFrom: Optional[date] = None,
    recordDateTo: Optional[date] = None,
    authorizationStatus: Optional[str] = None,
    pageToken: Optional[str] = None,
    pageSize: int = 20,
):
    try:
        uc = ListMedicalRecords(_repo)
        result = uc.execute(ListMedicalRecordsInput(
            actor_role=_role(request),
            actor_user_id=_actor_id(request),
            athlete_user_id=athleteUserId,
            team_id=teamId,
            record_date_from=recordDateFrom,
            record_date_to=recordDateTo,
            authorization_status=authorizationStatus,
            page_token=pageToken,
            page_size=pageSize,
        ))
        return 200, MedicalRecordListOut(
            data=[MedicalRecordOut.from_domain(r) for r in result.data],
            nextPageToken=result.next_page_token,
        )
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.post(
    "/records",
    response={201: MedicalRecordOut, 400: ErrorOut, 403: ErrorOut, 409: ErrorOut, 422: ErrorOut, 500: ErrorOut},
    operation_id="createMedicalRecord",
    summary="Cria registro médico",
)
def create_medical_record(request, payload: CreateMedicalRecordIn):
    try:
        uc = CreateMedicalRecord(_repo)
        record = uc.execute(CreateMedicalRecordInput(
            actor_role=_role(request),
            actor_user_id=_actor_id(request),
            athlete_user_id=payload.athleteUserId,
            team_id=payload.teamId,
            record_date=payload.recordDate,
            record_label=payload.recordLabel,
            assessment_summary=payload.assessmentSummary,
            restriction_summary=payload.restrictionSummary,
            return_to_training_authorized=payload.returnToTrainingAuthorized,
            return_to_play_authorized=payload.returnToPlayAuthorized,
            clinical_notes=payload.clinicalNotes,
        ))
        return 201, MedicalRecordOut.from_domain(record)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except ValueError as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.get(
    "/records/{record_id}",
    response={200: MedicalRecordOut, 403: ErrorOut, 404: ErrorOut, 500: ErrorOut},
    operation_id="getMedicalRecord",
    summary="Obtém registro médico por ID",
)
def get_medical_record(request, record_id: uuid.UUID):
    try:
        uc = GetMedicalRecord(_repo)
        record = uc.execute(_role(request), _actor_id(request), record_id)
        return 200, MedicalRecordOut.from_domain(record)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except MedicalRecordNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.patch(
    "/records/{record_id}",
    response={200: MedicalRecordOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 422: ErrorOut, 500: ErrorOut},
    operation_id="updateMedicalRecord",
    summary="Atualiza registro médico",
)
def update_medical_record(request, record_id: uuid.UUID, payload: UpdateMedicalRecordIn):
    try:
        uc = UpdateMedicalRecord(_repo)
        record = uc.execute(record_id, UpdateMedicalRecordInput(
            actor_role=_role(request),
            actor_user_id=_actor_id(request),
            record_date=payload.recordDate,
            record_label=payload.recordLabel,
            assessment_summary=payload.assessmentSummary,
            restriction_summary=payload.restrictionSummary,
            return_to_training_authorized=payload.returnToTrainingAuthorized,
            return_to_play_authorized=payload.returnToPlayAuthorized,
            clinical_notes=payload.clinicalNotes,
        ))
        return 200, MedicalRecordOut.from_domain(record)
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except MedicalRecordNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except ValueError as exc:
        raise HttpError(HTTPStatus.BAD_REQUEST, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


@router.delete(
    "/records/{record_id}",
    response={204: None, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 500: ErrorOut},
    operation_id="deleteMedicalRecord",
    summary="Soft-delete de registro médico (somente admin)",
)
def delete_medical_record(request, record_id: uuid.UUID):
    try:
        uc = DeleteMedicalRecord(_repo)
        uc.execute(_role(request), record_id)
        return 204, None
    except InsufficientPrivilege as exc:
        raise HttpError(HTTPStatus.FORBIDDEN, str(exc))
    except MedicalRecordNotFound as exc:
        raise HttpError(HTTPStatus.NOT_FOUND, str(exc))
    except Exception as exc:
        raise HttpError(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
