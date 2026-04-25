"""execution sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/execution-records
  POST /training-sessions/{id}/execution-records
  GET  /training-sessions/{id}/execution-records/{recordId}
  GET  /training-sessions/{id}/objectives
  POST /training-sessions/{id}/objectives
"""

import uuid

from ninja import Router
from .deps import CamelRouter

from ..application.common.services import TrainingServices
from ..application.execution.dto import (
    CreateExecutionRecordInput,
    CreateSessionObjectiveInput,
    GetExecutionRecordInput,
    ListExecutionRecordsInput,
    ListSessionObjectivesInput,
)
from ..schemas.execution import (
    CreateExecutionRecordIn,
    CreateSessionObjectiveIn,
    ExecutionRecordListOut,
    ExecutionRecordOut,
    SessionObjectiveListOut,
    SessionObjectiveOut,
)
from ..schemas.sessions import ProblemOut
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _execution_record_to_out, _session_objective_to_out

router = CamelRouter()


# ---------------------------------------------------------------------------
# Execution Records
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions/{id}/execution-records",
    response={200: ExecutionRecordListOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def list_execution_records(request, id: uuid.UUID):
    svc = TrainingServices()
    records = svc.list_execution_records_uc().execute(
        ListExecutionRecordsInput(session_id=id)
    )
    return 200, ExecutionRecordListOut(data=[_execution_record_to_out(r) for r in records])


@router.post(
    "/training-sessions/{id}/execution-records",
    response={201: ExecutionRecordOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 422: ProblemOut},
)
@map_exceptions
def create_execution_record(request, id: uuid.UUID, body: CreateExecutionRecordIn):
    svc = TrainingServices()
    record = svc.create_execution_record_uc().execute(
        CreateExecutionRecordInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            execution_type=body.execution_type,
            recorded_at=body.recorded_at,
            block_id=body.block_id,
            planned_value=body.planned_value,
            actual_value=body.actual_value,
            planned_unit=body.planned_unit,
            actual_unit=body.actual_unit,
            adjustment_reason_type=body.adjustment_reason_type,
            coach_rationale=body.coach_rationale,
            notes=body.notes,
        )
    )
    return 201, _execution_record_to_out(record)


@router.get(
    "/training-sessions/{id}/execution-records/{recordId}",
    response={200: ExecutionRecordOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def get_execution_record(request, id: uuid.UUID, recordId: uuid.UUID):
    svc = TrainingServices()
    record = svc.get_execution_record_uc().execute(
        GetExecutionRecordInput(
            session_id=id,
            record_id=recordId,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 200, _execution_record_to_out(record)


# ---------------------------------------------------------------------------
# Session Objectives
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions/{id}/objectives",
    response={200: SessionObjectiveListOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def list_session_objectives(request, id: uuid.UUID):
    svc = TrainingServices()
    objs = svc.list_session_objectives_uc().execute(
        ListSessionObjectivesInput(session_id=id)
    )
    return 200, SessionObjectiveListOut(data=[_session_objective_to_out(o) for o in objs])


@router.post(
    "/training-sessions/{id}/objectives",
    response={201: SessionObjectiveOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 422: ProblemOut},
)
@map_exceptions
def create_session_objective(request, id: uuid.UUID, body: CreateSessionObjectiveIn):
    svc = TrainingServices()
    obj = svc.create_session_objective_uc().execute(
        CreateSessionObjectiveInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            origin=body.origin,
            objective_type=body.objective_type,
            description=body.description,
            origin_notes=body.origin_notes,
            priority=body.priority,
        )
    )
    return 201, _session_objective_to_out(obj)


def register(parent: Router) -> None:
    parent.add_router("", router)
