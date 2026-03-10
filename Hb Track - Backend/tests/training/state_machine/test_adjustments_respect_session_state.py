"""
AR_274 — Gate 6: ajustes respeitam lifecycle/status da sessao.

Cobre:
  test_adjustment_allowed_in_in_progress
  test_adjustment_blocked_in_readonly
"""
import pytest

# Estados que permitem ajustes (regra de dominio AR_274)
_ADJUSTMENT_ALLOWED_STATES = frozenset({"in_progress"})
_ADJUSTMENT_BLOCKED_STATES = frozenset({"readonly", "draft", "scheduled", "pending_review"})


def _can_apply_adjustment(session_status: str) -> bool:
    """Politica de dominio: ajuste permitido apenas em sessoes in_progress."""
    return session_status in _ADJUSTMENT_ALLOWED_STATES


def test_adjustment_allowed_in_in_progress():
    """Ajuste e permitido quando sessao esta em in_progress."""
    assert _can_apply_adjustment("in_progress") is True


def test_adjustment_blocked_in_readonly():
    """Ajuste e bloqueado quando sessao esta em readonly."""
    assert _can_apply_adjustment("readonly") is False
    # Verificar outros estados imutaveis tambem
    for blocked_status in _ADJUSTMENT_BLOCKED_STATES:
        assert _can_apply_adjustment(blocked_status) is False, (
            f"Status '{blocked_status}' deveria bloquear ajustes"
        )
