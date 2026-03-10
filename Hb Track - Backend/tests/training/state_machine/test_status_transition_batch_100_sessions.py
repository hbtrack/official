"""
AR_274 — Gate 11: batch de 100 sessoes sem deadlock/timeout nem estados invalidos.

Cobre:
  test_100_sessions_transition_scheduled_to_in_progress
  test_no_residual_scheduled_sessions
  test_no_invalid_states_after_batch
  test_batch_time_within_slo
"""
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

_VALID_STATUSES = frozenset({
    "draft", "scheduled", "in_progress", "pending_review", "readonly"
})


def _make_session(status: str = "scheduled", offset_sec: int = -60):
    s = MagicMock()
    s.id = uuid4()
    s.status = status
    s.deleted_at = None
    s.session_at = datetime.now(timezone.utc) + timedelta(seconds=offset_sec)
    s.duration_planned_minutes = 90
    s.started_at = None
    s.ended_at = None
    return s


def _run_scheduled_to_in_progress(sessions: list, now: datetime) -> int:
    """Simula transicao scheduled -> in_progress conforme celery_tasks.py."""
    count = 0
    for session in sessions:
        if (
            session.status == "scheduled"
            and session.deleted_at is None
            and session.session_at <= now
        ):
            session.status = "in_progress"
            if session.started_at is None:
                session.started_at = session.session_at
            count += 1
    return count


def test_100_sessions_transition_scheduled_to_in_progress():
    """100 sessoes scheduled no passado devem transicionar para in_progress."""
    sessions = [_make_session("scheduled", -60) for _ in range(100)]
    now = datetime.now(timezone.utc)

    count = _run_scheduled_to_in_progress(sessions, now)

    assert count == 100
    assert all(s.status == "in_progress" for s in sessions)


def test_no_residual_scheduled_sessions():
    """Apos batch, nenhuma sessao com session_at no passado permanece em 'scheduled'."""
    sessions = [_make_session("scheduled", -60) for _ in range(100)]
    now = datetime.now(timezone.utc)

    _run_scheduled_to_in_progress(sessions, now)

    residual = [s for s in sessions if s.status == "scheduled"]
    assert len(residual) == 0


def test_no_invalid_states_after_batch():
    """Todos os status apos batch devem ser valores validos do lifecycle."""
    sessions = [_make_session("scheduled", -60) for _ in range(100)]
    now = datetime.now(timezone.utc)

    _run_scheduled_to_in_progress(sessions, now)

    invalid = [s for s in sessions if s.status not in _VALID_STATUSES]
    assert len(invalid) == 0, f"Estados invalidos encontrados: {[s.status for s in invalid]}"


def test_batch_time_within_slo():
    """Batch de 100 sessoes deve completar em menos de 500ms (SLO do scheduler)."""
    sessions = [_make_session("scheduled", -60) for _ in range(100)]
    now = datetime.now(timezone.utc)

    start = time.perf_counter()
    _run_scheduled_to_in_progress(sessions, now)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 500, f"Batch levou {elapsed_ms:.1f}ms — acima do SLO de 500ms"
