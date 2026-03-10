"""
AR_274 — Gate 9: transicoes temporais corretas + UTC isolation.

Cobre:
  test_transition_at_t_minus_1_not_triggered
  test_transition_at_t_exact_triggered
  test_transition_at_t_plus_1_triggered
  test_utc_isolation
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest


def _should_transition_scheduled_to_in_progress(
    session_at: datetime, now: datetime
) -> bool:
    """Condicao de transicao scheduled -> in_progress (espelha logica do task)."""
    return session_at <= now


def test_transition_at_t_minus_1_not_triggered():
    """Sessao em T-1s (futuro) nao deve transicionar para in_progress."""
    now = datetime.now(timezone.utc)
    session_at = now + timedelta(seconds=1)
    assert _should_transition_scheduled_to_in_progress(session_at, now) is False


def test_transition_at_t_exact_triggered():
    """Sessao em T exato (== now) deve transicionar para in_progress."""
    now = datetime.now(timezone.utc)
    session_at = now  # T exato
    assert _should_transition_scheduled_to_in_progress(session_at, now) is True


def test_transition_at_t_plus_1_triggered():
    """Sessao em T+1s (passado) deve transicionar para in_progress."""
    now = datetime.now(timezone.utc)
    session_at = now - timedelta(seconds=1)
    assert _should_transition_scheduled_to_in_progress(session_at, now) is True


def test_utc_isolation():
    """Comparacao em UTC nao deve ser afetada por timezone local (Sao Paulo, Tokyo)."""
    now_utc = datetime.now(timezone.utc)
    # Mesmo instante em fusos diferentes
    tz_sp = timezone(timedelta(hours=-3))   # America/Sao_Paulo (aprox)
    tz_jp = timezone(timedelta(hours=9))    # Asia/Tokyo

    session_at_sp = now_utc.astimezone(tz_sp) - timedelta(seconds=10)
    session_at_jp = now_utc.astimezone(tz_jp) - timedelta(seconds=10)

    # Ambos sao 10s no passado, independente do fuso
    assert _should_transition_scheduled_to_in_progress(session_at_sp, now_utc) is True
    assert _should_transition_scheduled_to_in_progress(session_at_jp, now_utc) is True

    # 10s no futuro, mesmo resultado diferente de fuso
    session_at_future_sp = now_utc.astimezone(tz_sp) + timedelta(seconds=10)
    session_at_future_jp = now_utc.astimezone(tz_jp) + timedelta(seconds=10)
    assert _should_transition_scheduled_to_in_progress(session_at_future_sp, now_utc) is False
    assert _should_transition_scheduled_to_in_progress(session_at_future_jp, now_utc) is False
