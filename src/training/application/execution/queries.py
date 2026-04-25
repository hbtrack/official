from __future__ import annotations

from ...domain.entities.execution import ExecutionRecord
from ...domain.entities.sessions import SessionObjective
from ...domain.rules import (
    ExecutionRecordNotFound,
    TrainingSessionNotFound,
    assert_can_read_session,
)
from ...infrastructure.repository.execution import ExecutionRecordRepository
from ...infrastructure.repository.sessions import SessionObjectiveRepository, TrainingSessionRepository
from .dto import GetExecutionRecordInput, ListExecutionRecordsInput, ListSessionObjectivesInput


class ListExecutionRecordsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._record_repo = record_repo

    def execute(self, inp: ListExecutionRecordsInput) -> list[ExecutionRecord]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        return self._record_repo.list_by_session(inp.session_id)


class GetExecutionRecordUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._record_repo = record_repo

    def execute(self, inp: GetExecutionRecordInput) -> ExecutionRecord:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_read_session(inp.actor_role, inp.actor_id, inp.session_athlete_ids)
        record = self._record_repo.get_by_id(inp.record_id)
        if not record or record.session_id != inp.session_id:
            raise ExecutionRecordNotFound(
                f"Registro de execução {inp.record_id} não encontrado para a sessão {inp.session_id}"
            )
        return record


class ListSessionObjectivesUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, obj_repo: SessionObjectiveRepository):
        self._session_repo = session_repo
        self._obj_repo = obj_repo

    def execute(self, inp: ListSessionObjectivesInput) -> list[SessionObjective]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        return self._obj_repo.list_by_session(inp.session_id)
