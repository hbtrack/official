"""attendance sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/attendance
  POST /training-sessions/{id}/attendance
"""

import uuid

from ninja import Router
from .deps import CamelRouter
from ninja.errors import HttpError

from ..application.common.services import TrainingServices
from ..application.attendance.dto import (
    ListSessionAttendanceInput,
    RecordSessionAttendanceInput,
)
from ..schemas.attendance import (
    AttendanceListOut,
    AttendanceRecordOut,
    RecordSessionAttendanceIn,
)
from ..schemas.sessions import ProblemOut
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _attendance_to_out

router = CamelRouter()


@router.get(
    "/training-sessions/{id}/attendance",
    response={200: AttendanceListOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def list_session_attendance(request, id: uuid.UUID):
    svc = TrainingServices()
    records = svc.list_session_attendance_uc().execute(
        ListSessionAttendanceInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 200, AttendanceListOut(items=[_attendance_to_out(r) for r in records])


@router.post(
    "/training-sessions/{id}/attendance",
    response={201: AttendanceRecordOut, 401: ProblemOut, 400: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut},
)
@map_exceptions
def record_session_attendance(request, id: uuid.UUID, body: RecordSessionAttendanceIn):
    svc = TrainingServices()
    record = svc.record_session_attendance_uc().execute(
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
