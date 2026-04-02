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

# Source graph authority: docs/hbtrack/modulos/medical/graph/endpoints.yaml
router = Router(tags=["medical"])
_repo = MedicalRecordRepository()


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
    "/records",
    response={200: MedicalRecordListOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut, 500: ErrorOut},
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
    response={201: MedicalRecordOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 409: ErrorOut, 422: ErrorOut, 500: ErrorOut},
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
    response={200: MedicalRecordOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 500: ErrorOut},
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
    response={200: MedicalRecordOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 422: ErrorOut, 500: ErrorOut},
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
    response={204: None, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 500: ErrorOut},
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
