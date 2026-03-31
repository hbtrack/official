"""
TM-104 — Sessões somente leitura (histórico > 60 dias).
Fonte: INVARIANTS_TRAINING.md (INV-TRAIN-005).
"""
from datetime import datetime, timezone, timedelta

import pytest

from training.domain.rules import SessionNotMutable, assert_session_not_historical


class TestReadonlySessions:
    """INV-TRAIN-005: sessões com session_at > 60 dias são somente leitura."""

    def test_recent_session_passes(self):
        session_at = datetime.now(tz=timezone.utc) - timedelta(days=30)
        assert_session_not_historical(session_at)

    def test_session_at_60_days_passes(self):
        session_at = datetime.now(tz=timezone.utc) - timedelta(days=60)
        assert_session_not_historical(session_at)

    def test_session_older_than_60_days_raises(self):
        session_at = datetime.now(tz=timezone.utc) - timedelta(days=61)
        with pytest.raises(SessionNotMutable, match="INV-TRAIN-005"):
            assert_session_not_historical(session_at)

    def test_future_session_passes(self):
        session_at = datetime.now(tz=timezone.utc) + timedelta(days=7)
        assert_session_not_historical(session_at)
