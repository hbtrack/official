from __future__ import annotations

from ...domain.entities.wellness import WellnessPost, WellnessPre
from ...domain.rules import (
    TrainingSessionNotFound,
    WellnessEntryNotFound,
    assert_can_view_athlete_record,
)
from ...infrastructure.repository.sessions import TrainingSessionRepository
from ...infrastructure.repository.wellness import WellnessPostRepository, WellnessPreRepository
from .dto import GetWellnessPostInput, GetWellnessPreInput


class GetWellnessPreUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPreRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: GetWellnessPreInput) -> WellnessPre:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_pre não encontrado para este atleta/sessão")
        return wellness


class GetWellnessPostUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPostRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: GetWellnessPostInput) -> WellnessPost:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_post não encontrado para este atleta/sessão")
        return wellness
