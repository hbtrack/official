"""execution sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/execution-records
  POST /training-sessions/{id}/execution-records
  GET  /training-sessions/{id}/execution-records/{record_id}
  GET  /training-sessions/{id}/objectives
  POST /training-sessions/{id}/objectives
"""

import uuid

from ninja import Router

from ..application.use_cases import (
    CreateExecutionRecordInput,
    CreateExecutionRecordUseCase,
    CreateSessionObjectiveInput,
    CreateSessionObjectiveUseCase,
    GetExecutionRecordInput,
    GetExecutionRecordUseCase,
    ListExecutionRecordsInput,
    ListExecutionRecordsUseCase,
    ListSessionObjectivesInput,
    ListSessionObjectivesUseCase,
)
from ..infrastructure.repository import (
    ExecutionRecordRepository,
    SessionObjectiveRepository,
    TrainingSessionRepository,
)
from ..schemas import (
    CreateExecutionRecordIn,
    CreateSessionObjectiveIn,
    ErrorOut,
    ExecutionRecordListOut,
    ExecutionRecordOut,
    SessionObjectiveListOut,
    SessionObjectiveOut,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _execution_record_to_out, _session_objective_to_out

router = Router()


# ---------------------------------------------------------------------------
# Execution Records
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions/{id}/execution-records",
    response={200: ExecutionRecordListOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def list_execution_records(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    record_repo = ExecutionRecordRepository()
    records = ListExecutionRecordsUseCase(session_repo, record_repo).execute(
        ListExecutionRecordsInput(session_id=id)
    )
    return 200, ExecutionRecordListOut(data=[_execution_record_to_out(r) for r in records])


@router.post(
    "/training-sessions/{id}/execution-records",
    response={201: ExecutionRecordOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
@map_exceptions
def create_execution_record(request, id: uuid.UUID, body: CreateExecutionRecordIn):
    session_repo = TrainingSessionRepository()
    record_repo = ExecutionRecordRepository()
    record = CreateExecutionRecordUseCase(session_repo, record_repo).execute(
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
    "/training-sessions/{id}/execution-records/{record_id}",
    response={200: ExecutionRecordOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def get_execution_record(request, id: uuid.UUID, record_id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    record_repo = ExecutionRecordRepository()
    record = GetExecutionRecordUseCase(session_repo, record_repo).execute(
        GetExecutionRecordInput(
            session_id=id,
            record_id=record_id,
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
    response={200: SessionObjectiveListOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def list_session_objectives(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    obj_repo = SessionObjectiveRepository()
    objs = ListSessionObjectivesUseCase(session_repo, obj_repo).execute(
        ListSessionObjectivesInput(session_id=id)
    )
    return 200, SessionObjectiveListOut(data=[_session_objective_to_out(o) for o in objs])


@router.post(
    "/training-sessions/{id}/objectives",
    response={201: SessionObjectiveOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
@map_exceptions
def create_session_objective(request, id: uuid.UUID, body: CreateSessionObjectiveIn):
    session_repo = TrainingSessionRepository()
    obj_repo = SessionObjectiveRepository()
    obj = CreateSessionObjectiveUseCase(session_repo, obj_repo).execute(
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
