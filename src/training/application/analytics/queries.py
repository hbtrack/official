from __future__ import annotations

from ...domain.entities import ExecutionType
from ...domain.rules import TrainingSessionNotFound, assert_can_modify_session
from ...infrastructure.repository import ExecutionRecordRepository, TrainingSessionRepository
from .dto import GetLoadChartInput, GetLoadChartResult


class GetLoadChartUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        execution_record_repo: ExecutionRecordRepository,
    ):
        self._session_repo = session_repo
        self._execution_record_repo = execution_record_repo

    def execute(self, inp: GetLoadChartInput) -> GetLoadChartResult:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        records = self._execution_record_repo.list_by_session(inp.session_id)
        load_entries = [r for r in records if r.execution_type == ExecutionType.LOAD_RECALCULATION]
        return GetLoadChartResult(session=session, load_entries=load_entries)
