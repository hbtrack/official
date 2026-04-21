"""attendance sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/attendance
  POST /training-sessions/{id}/attendance
"""

import uuid

from ninja import Router
from ninja.errors import HttpError

from ..application.use_cases import (
    ListSessionAttendanceInput,
    ListSessionAttendanceUseCase,
    RecordSessionAttendanceInput,
    RecordSessionAttendanceUseCase,
)
from ..infrastructure.repository import (
    AttendanceRepository,
    TrainingSessionRepository,
)
from ..schemas import (
    AttendanceListOut,
    AttendanceRecordOut,
    ErrorOut,
    RecordSessionAttendanceIn,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _attendance_to_out

router = Router()


@router.get(
    "/training-sessions/{id}/attendance",
    response={200: AttendanceListOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def list_session_attendance(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    attendance_repo = AttendanceRepository()
    records = ListSessionAttendanceUseCase(session_repo, attendance_repo).execute(
        ListSessionAttendanceInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 200, AttendanceListOut(items=[_attendance_to_out(r) for r in records])


@router.post(
    "/training-sessions/{id}/attendance",
    response={201: AttendanceRecordOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def record_session_attendance(request, id: uuid.UUID, body: RecordSessionAttendanceIn):
    session_repo = TrainingSessionRepository()
    attendance_repo = AttendanceRepository()
    record = RecordSessionAttendanceUseCase(session_repo, attendance_repo).execute(
        RecordSessionAttendanceInput(
            session_id=id,
            athlete_id=body.athlete_id,
            status=body.status,
            source=body.source,
            correction_by_user_id=body.correction_by_user_id,
            correction_at=body.correction_at,
            justification_reason=body.justification_reason,
            observed_at=body.observed_at,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 201, _attendance_to_out(record)


def register(parent: Router) -> None:
    parent.add_router("", router)
