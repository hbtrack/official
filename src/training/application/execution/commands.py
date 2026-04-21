from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities import (
    ExecutionRecord,
    ExecutionType,
    SessionObjective,
    SessionObjectiveOrigin,
    TrainingSessionStatus,
)
from ...domain.rules import (
    InsufficientPrivilege,
    TrainingSessionNotFound,
    assert_can_modify_session,
)
from ...infrastructure.repository import (
    ExecutionRecordRepository,
    SessionObjectiveRepository,
    TrainingSessionRepository,
)
from .dto import CreateExecutionRecordInput, CreateSessionObjectiveInput


class CreateExecutionRecordUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._record_repo = record_repo

    def execute(self, inp: CreateExecutionRecordInput) -> ExecutionRecord:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        if session.status != TrainingSessionStatus.IN_PROGRESS:
            raise InsufficientPrivilege("ExecutionRecord requer sessão IN_PROGRESS")
        now = datetime.now(tz=timezone.utc)
        record = ExecutionRecord(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            block_id=inp.block_id,
            execution_type=ExecutionType(inp.execution_type),
            recorded_at=inp.recorded_at,
            planned_value=inp.planned_value,
            actual_value=inp.actual_value,
            planned_unit=inp.planned_unit,
            actual_unit=inp.actual_unit,
            adjustment_reason_type=inp.adjustment_reason_type,
            coach_rationale=inp.coach_rationale,
            notes=inp.notes,
            created_by_user_id=inp.actor_id,
            created_at=now,
            updated_at=now,
        )
        record.validate_invariants()
        return self._record_repo.save(record)


class CreateSessionObjectiveUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, obj_repo: SessionObjectiveRepository):
        self._session_repo = session_repo
        self._obj_repo = obj_repo

    def execute(self, inp: CreateSessionObjectiveInput) -> SessionObjective:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        now = datetime.now(tz=timezone.utc)
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            origin=SessionObjectiveOrigin(inp.origin),
            objective_type=inp.objective_type,
            description=inp.description,
            origin_notes=inp.origin_notes,
            priority=inp.priority,
            created_at=now,
            updated_at=now,
        )
        obj.validate_invariants()
        return self._obj_repo.save(obj)
