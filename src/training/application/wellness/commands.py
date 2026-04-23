from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ...domain.entities import (
    TrainingSessionStatus,
    WellnessPost,
    WellnessPre,
)
from ...domain.rules import (
    DuplicateWellnessEntry,
    InsufficientPrivilege,
    TrainingSessionNotFound,
    WellnessEntryNotFound,
    assert_can_submit_wellness,
    assert_can_view_athlete_record,
    assert_wellness_post_window,
    assert_wellness_pre_window,
)
from ...infrastructure.repository import (
    TrainingSessionRepository,
    WellnessPostRepository,
    WellnessPreRepository,
)
from .dto import (
    SubmitWellnessPostInput,
    SubmitWellnessPreInput,
    UpdateWellnessPostInput,
    UpdateWellnessPreInput,
)


class SubmitWellnessPreUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        wellness_repo: WellnessPreRepository,
    ):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: SubmitWellnessPreInput) -> WellnessPre:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_submit_wellness(inp.actor_role, inp.actor_id, inp.athlete_id)
        # INV-TRAIN-002: janela temporal
        assert_wellness_pre_window(session.session_at)
        # INV-TRAIN-009: unicidade
        existing = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if existing:
            raise DuplicateWellnessEntry("INV-TRAIN-009: já existe wellness_pre ativo para este atleta/sessão")
        now = datetime.now(tz=timezone.utc)
        wellness = WellnessPre(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            readiness=inp.readiness,
            sleep_quality=inp.sleep_quality,
            sleep_hours=inp.sleep_hours,
            mood=inp.mood,
            fatigue=inp.fatigue,
            muscle_soreness=inp.muscle_soreness,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)


class SubmitWellnessPostUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        wellness_repo: WellnessPostRepository,
    ):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: SubmitWellnessPostInput) -> WellnessPost:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_submit_wellness(inp.actor_role, inp.actor_id, inp.athlete_id)
        # Requer sessão IN_PROGRESS ou COMPLETED
        if session.status not in (TrainingSessionStatus.IN_PROGRESS, TrainingSessionStatus.COMPLETED):
            raise InsufficientPrivilege("WellnessPost requer sessão IN_PROGRESS ou COMPLETED")
        # INV-TRAIN-010: unicidade
        existing = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if existing:
            raise DuplicateWellnessEntry("INV-TRAIN-010: já existe wellness_post ativo para este atleta/sessão")
        now = datetime.now(tz=timezone.utc)
        wellness = WellnessPost(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            perceived_exertion=inp.perceived_exertion,
            enjoyment=inp.enjoyment,
            technical_learning=inp.technical_learning,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)


class UpdateWellnessPreUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPreRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: UpdateWellnessPreInput) -> WellnessPre:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        assert_wellness_pre_window(session.session_at)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_pre não encontrado para este atleta/sessão")
        for field_name in (
            "readiness",
            "sleep_quality",
            "sleep_hours",
            "mood",
            "fatigue",
            "muscle_soreness",
            "notes",
        ):
            value = getattr(inp, field_name)
            if value is not None:
                setattr(wellness, field_name, value)
        wellness.updated_at = datetime.now(tz=timezone.utc)
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)


class UpdateWellnessPostUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPostRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: UpdateWellnessPostInput) -> WellnessPost:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_post não encontrado para este atleta/sessão")
        assert_wellness_post_window(wellness.created_at)
        for field_name in ("perceived_exertion", "enjoyment", "technical_learning", "notes"):
            value = getattr(inp, field_name)
            if value is not None:
                setattr(wellness, field_name, value)
        wellness.updated_at = datetime.now(tz=timezone.utc)
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)
