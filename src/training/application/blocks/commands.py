from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities import SessionBlock, SessionBlockIntensity, SessionBlockPhase
from ...domain.rules import (
    SessionBlockNotFound,
    TrainingSessionNotFound,
    assert_can_modify_session,
    assert_elastic_sum_rule,
    assert_session_mutable,
)
from ...infrastructure.repository import SessionBlockRepository, TrainingSessionRepository
from .dto import (
    AddSessionBlockInput,
    DeleteSessionBlockInput,
    ReorderSessionBlocksInput,
    UpdateSessionBlockInput,
)


class AddSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: AddSessionBlockInput) -> SessionBlock:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        # INV-TRAIN-083
        current_total = self._block_repo.total_duration_for_session(inp.session_id)
        assert_elastic_sum_rule(session.duration_planned_minutes, current_total, inp.duration_minutes)
        block = SessionBlock(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            phase=SessionBlockPhase(inp.phase),
            order_index=inp.order_index,
            duration_minutes=inp.duration_minutes,
            block_objective=inp.block_objective,
            intensity=SessionBlockIntensity(inp.intensity),
            is_optional=inp.is_optional,
            exercise_id=inp.exercise_id,
            exercise_version_id=inp.exercise_version_id,
            notes=inp.notes,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        block.validate_invariants()
        return self._block_repo.save(block)


class UpdateSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: UpdateSessionBlockInput) -> SessionBlock:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        block = self._block_repo.get_by_id(inp.block_id)
        if not block:
            raise SessionBlockNotFound(f"Bloco {inp.block_id} não encontrado")
        if inp.duration_minutes is not None:
            current_total = self._block_repo.total_duration_for_session(inp.session_id, exclude_id=inp.block_id)
            assert_elastic_sum_rule(session.duration_planned_minutes, current_total, inp.duration_minutes)
            block.duration_minutes = inp.duration_minutes
        if inp.block_objective is not None:
            block.block_objective = inp.block_objective
        if inp.intensity is not None:
            block.intensity = SessionBlockIntensity(inp.intensity)
        if inp.phase is not None:
            block.phase = SessionBlockPhase(inp.phase)
        if inp.is_optional is not None:
            block.is_optional = inp.is_optional
        if inp.notes is not None:
            block.notes = inp.notes
        if inp.exercise_id is not None:
            block.exercise_id = inp.exercise_id
        if inp.exercise_version_id is not None:
            block.exercise_version_id = inp.exercise_version_id
        block.updated_at = datetime.now(tz=timezone.utc)
        block.validate_invariants()
        return self._block_repo.save(block)


class DeleteSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: DeleteSessionBlockInput) -> None:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        block = self._block_repo.get_by_id(inp.block_id)
        if not block:
            raise SessionBlockNotFound(f"Bloco {inp.block_id} não encontrado")
        self._block_repo.delete(inp.block_id)


class ReorderSessionBlocksUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: ReorderSessionBlocksInput) -> list[SessionBlock]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        existing = self._block_repo.list_by_session(inp.session_id)
        existing_ids = {b.id for b in existing}
        if set(inp.block_ids) != existing_ids:
            raise ValueError(
                "blockIds deve conter exatamente todos os IDs dos blocos da sessão"
            )
        block_map = {b.id: b for b in existing}
        result = []
        now = datetime.now(tz=timezone.utc)
        for order_index, block_id in enumerate(inp.block_ids):
            block = block_map[block_id]
            block.order_index = order_index
            block.updated_at = now
            result.append(self._block_repo.save(block))
        return result
