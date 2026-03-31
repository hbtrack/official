"""
TM-101, TM-102 — Janelas temporais de wellness.
Fonte: INVARIANTS_TRAINING.md (INV-TRAIN-002, INV-TRAIN-003).
"""
from datetime import datetime, timezone, timedelta

import pytest

from training.domain.rules import (
    WellnessWindowClosed,
    assert_wellness_pre_window,
    assert_wellness_post_window,
)


# ---------------------------------------------------------------------------
# INV-TRAIN-002: wellness_pre bloqueado >= session_at - 2h (TM-101)
# ---------------------------------------------------------------------------

class TestWellnessPreWindow:
    """INV-TRAIN-002: submissão bloqueada quando NOW_UTC >= session_at - 2h + 30s."""

    def test_far_future_session_passes(self):
        session_at = datetime.now(tz=timezone.utc) + timedelta(hours=10)
        assert_wellness_pre_window(session_at)

    def test_deadline_passed_raises(self):
        session_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        with pytest.raises(WellnessWindowClosed, match="INV-TRAIN-002"):
            assert_wellness_pre_window(session_at)

    def test_just_before_deadline_passes(self):
        session_at = datetime.now(tz=timezone.utc) + timedelta(hours=2, minutes=1)
        assert_wellness_pre_window(session_at)


# ---------------------------------------------------------------------------
# INV-TRAIN-003: wellness_post bloqueado >= created_at + 24h (TM-102)
# ---------------------------------------------------------------------------

class TestWellnessPostWindow:
    """INV-TRAIN-003: edição bloqueada quando NOW_UTC >= created_at + 24h + 30s."""

    def test_recent_creation_passes(self):
        created_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        assert_wellness_post_window(created_at)

    def test_old_creation_raises(self):
        created_at = datetime.now(tz=timezone.utc) - timedelta(hours=25)
        with pytest.raises(WellnessWindowClosed, match="INV-TRAIN-003"):
            assert_wellness_post_window(created_at)

    def test_just_within_window_passes(self):
        created_at = datetime.now(tz=timezone.utc) - timedelta(hours=23)
        assert_wellness_post_window(created_at)
