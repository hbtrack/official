from __future__ import annotations

from ...domain.entities.blocks import SessionBlock
from ...domain.rules import (
    SessionBlockNotFound,
    TrainingSessionNotFound,
    assert_can_read_session,
)
from ...infrastructure.repository.blocks import SessionBlockRepository
from ...infrastructure.repository.sessions import TrainingSessionRepository
from .dto import GetSessionBlockInput, ListSessionBlocksInput


class ListSessionBlocksUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: ListSessionBlocksInput) -> list[SessionBlock]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_read_session(inp.actor_role, inp.actor_id, inp.session_athlete_ids)
        return self._block_repo.list_by_session(inp.session_id)


class GetSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: GetSessionBlockInput) -> SessionBlock:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_read_session(inp.actor_role, inp.actor_id, inp.session_athlete_ids)
        block = self._block_repo.get_by_id(inp.block_id)
        if not block or block.session_id != inp.session_id:
            raise SessionBlockNotFound(f"Bloco {inp.block_id} não encontrado")
        return block
