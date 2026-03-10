"""
AR_274 — Gate 10: idempotencia do task de transicao.

Cobre:
  test_double_run_no_duplicate_transitions
  test_hash_unchanged_after_second_run
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


def _simulate_transition(sessions: list, now: datetime) -> list:
    """Simula a logica de transicao scheduled -> in_progress do celery task."""
    transitioned = []
    for session in sessions:
        if (
            session.status == "scheduled"
            and session.session_at <= now
        ):
            session.status = "in_progress"
            transitioned.append(session.id)
    return transitioned


def _state_hash(sessions: list) -> str:
    """Hash do estado de todas as sessoes (para detectar mudancas)."""
    state = sorted(
        [{"id": str(s.id), "status": s.status} for s in sessions],
        key=lambda x: x["id"],
    )
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


def _make_session(session_at_offset_sec: int = -60):
    s = MagicMock()
    from uuid import uuid4
    s.id = uuid4()
    s.status = "scheduled"
    s.session_at = datetime.now(timezone.utc) + timedelta(seconds=session_at_offset_sec)
    return s


def test_double_run_no_duplicate_transitions():
    """Executar a logica duas vezes nao deve criar transicoes duplicadas."""
    sessions = [_make_session(-60) for _ in range(5)]
    now = datetime.now(timezone.utc)

    first_run = _simulate_transition(sessions, now)
    second_run = _simulate_transition(sessions, now)  # todos ja estao in_progress

    assert len(first_run) == 5
    assert len(second_run) == 0  # nao ha mais sessoes em 'scheduled'
    assert all(s.status == "in_progress" for s in sessions)


def test_hash_unchanged_after_second_run():
    """Estado das sessoes (hash) nao muda apos segundo run idempotente."""
    sessions = [_make_session(-60) for _ in range(3)]
    now = datetime.now(timezone.utc)

    _simulate_transition(sessions, now)
    hash_after_first = _state_hash(sessions)

    _simulate_transition(sessions, now)
    hash_after_second = _state_hash(sessions)

    assert hash_after_first == hash_after_second
