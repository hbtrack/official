from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities.execution import ExecutionRecord
from ...domain.entities.sessions import SessionObjective
from ...domain.common.enums import ExecutionType, SessionObjectiveOrigin
from ...domain.policies.session_access import SessionGuard
from ...infrastructure.repository.execution import ExecutionRecordRepository
from ...infrastructure.repository.sessions import SessionObjectiveRepository, TrainingSessionRepository
from .dto import CreateExecutionRecordInput, CreateSessionObjectiveInput


class CreateExecutionRecordUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._record_repo = record_repo
        self._guard = SessionGuard(session_repo)

    def execute(self, inp: CreateExecutionRecordInput) -> ExecutionRecord:
        self._guard.load_for_in_progress(inp.session_id, inp.actor_role)
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
        self._guard = SessionGuard(session_repo)

    def execute(self, inp: CreateSessionObjectiveInput) -> SessionObjective:
        self._guard.load_with_write_access(inp.session_id, inp.actor_role)
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
