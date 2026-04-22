"""
Teste de round-trip dos 12 campos de execução de TrainingSession (A1d).

Verifica que os campos adicionados na migration 0007 são gravados por
repository.save() e recuperados por repository.get_by_id() sem perda
silenciosa de dados (V1 fix).

Cobre:
  - started_at, ended_at, closed_at, closed_by_user_id
  - deviation_justification, planning_deviation_flag
  - duration_actual_minutes, execution_outcome
  - delay_minutes, cancellation_reason
  - actual_load_recorded, post_review_completed_at
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from training.domain.entities import TrainingSession, TrainingSessionStatus
from training.infrastructure.repository import TrainingSessionRepository


pytestmark = pytest.mark.django_db


def _base_session(**overrides) -> TrainingSession:
    """Cria uma TrainingSession mínima válida."""
    defaults = dict(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        team_id=uuid.uuid4(),
        season_id=uuid.uuid4(),
        microcycle_id=None,
        session_at=datetime(2026, 4, 21, 10, 0, tzinfo=timezone.utc),
        duration_planned_minutes=90,
        session_type="TECHNICAL",
        status=TrainingSessionStatus.DRAFT,
        created_by_user_id=uuid.uuid4(),
        created_at=datetime(2026, 4, 21, 9, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 21, 9, 0, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    return TrainingSession(**defaults)


class TestExecutionFieldsRoundTrip:
    """Garante que os 12 campos de execução sobrevivem ao ciclo save → get_by_id."""

    def test_started_at_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        ts = datetime(2026, 4, 21, 14, 30, tzinfo=timezone.utc)
        session = _base_session(started_at=ts)
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.started_at == ts

    def test_ended_at_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        ts = datetime(2026, 4, 21, 16, 0, tzinfo=timezone.utc)
        session = _base_session(ended_at=ts)
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.ended_at == ts

    def test_closed_at_and_closed_by_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        user_id = uuid.uuid4()
        ts = datetime(2026, 4, 21, 17, 0, tzinfo=timezone.utc)
        session = _base_session(closed_at=ts, closed_by_user_id=user_id)
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.closed_at == ts
        assert loaded.closed_by_user_id == user_id

    def test_deviation_fields_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        session = _base_session(
            deviation_justification="Chuva impediu treino externo",
            planning_deviation_flag=True,
        )
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.deviation_justification == "Chuva impediu treino externo"
        assert loaded.planning_deviation_flag is True

    def test_duration_actual_minutes_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        session = _base_session(duration_actual_minutes=75)
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.duration_actual_minutes == 75

    def test_execution_outcome_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        session = _base_session(execution_outcome="COMPLETED_PARTIALLY")
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.execution_outcome == "COMPLETED_PARTIALLY"

    def test_delay_minutes_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        session = _base_session(delay_minutes=15)
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.delay_minutes == 15

    def test_cancellation_reason_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        session = _base_session(cancellation_reason="Lesão de atleta titular")
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.cancellation_reason == "Lesão de atleta titular"

    def test_actual_load_recorded_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        session = _base_session(actual_load_recorded=7)
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.actual_load_recorded == 7

    def test_post_review_completed_at_round_trip(self) -> None:
        repo = TrainingSessionRepository()
        ts = datetime(2026, 4, 22, 9, 0, tzinfo=timezone.utc)
        session = _base_session(post_review_completed_at=ts)
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.post_review_completed_at == ts

    def test_all_twelve_fields_round_trip(self) -> None:
        """Grava todos os 12 campos simultaneamente e valida cada um."""
        repo = TrainingSessionRepository()
        user_id = uuid.uuid4()
        t1 = datetime(2026, 4, 21, 14, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 4, 21, 16, 0, tzinfo=timezone.utc)
        t3 = datetime(2026, 4, 21, 17, 0, tzinfo=timezone.utc)
        t4 = datetime(2026, 4, 22, 9, 0, tzinfo=timezone.utc)

        session = _base_session(
            started_at=t1,
            ended_at=t2,
            closed_at=t3,
            closed_by_user_id=user_id,
            deviation_justification="Desvio por condições climáticas",
            planning_deviation_flag=True,
            duration_actual_minutes=110,
            execution_outcome="COMPLETED_FULLY",
            delay_minutes=5,
            cancellation_reason=None,  # não cancelada
            actual_load_recorded=8,
            post_review_completed_at=t4,
        )
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None

        assert loaded.started_at == t1
        assert loaded.ended_at == t2
        assert loaded.closed_at == t3
        assert loaded.closed_by_user_id == user_id
        assert loaded.deviation_justification == "Desvio por condições climáticas"
        assert loaded.planning_deviation_flag is True
        assert loaded.duration_actual_minutes == 110
        assert loaded.execution_outcome == "COMPLETED_FULLY"
        assert loaded.delay_minutes == 5
        assert loaded.cancellation_reason is None
        assert loaded.actual_load_recorded == 8
        assert loaded.post_review_completed_at == t4

    def test_null_execution_fields_preserved(self) -> None:
        """Sessão sem campos de execução: todos os 12 campos devem ser None."""
        repo = TrainingSessionRepository()
        session = _base_session()  # nenhum campo de execução definido
        repo.save(session)
        loaded = repo.get_by_id(session.id)
        assert loaded is not None

        assert loaded.started_at is None
        assert loaded.ended_at is None
        assert loaded.closed_at is None
        assert loaded.closed_by_user_id is None
        assert loaded.deviation_justification is None
        assert loaded.planning_deviation_flag is None
        assert loaded.duration_actual_minutes is None
        assert loaded.execution_outcome is None
        assert loaded.delay_minutes is None
        assert loaded.cancellation_reason is None
        assert loaded.actual_load_recorded is None
        assert loaded.post_review_completed_at is None
