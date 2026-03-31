"""
TM-031 — Live adjustments during session execution.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-018, DR-TRAIN-019).
"""
import uuid
from datetime import datetime, timezone

import pytest

from training.domain.entities import ExecutionRecord, ExecutionType


def _make_record(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        execution_type=ExecutionType.LIVE_ADJUSTMENT,
        recorded_at=datetime.now(tz=timezone.utc),
        created_by_user_id=uuid.uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return ExecutionRecord(**defaults)


class TestLiveAdjustments:
    """DR-TRAIN-018/019: live adjustments exigem coachRationale."""

    def test_live_adjustment_with_rationale_passes(self):
        r = _make_record(coach_rationale="Atleta apresentou sinais de fadiga")
        r.validate_invariants()

    def test_live_adjustment_without_rationale_raises(self):
        r = _make_record(coach_rationale=None)
        with pytest.raises(ValueError, match="DR-TRAIN-019"):
            r.validate_invariants()

    def test_alternate_exercise_no_rationale_needed(self):
        r = _make_record(
            execution_type=ExecutionType.ALTERNATE_EXERCISE,
            coach_rationale=None,
        )
        r.validate_invariants()

    def test_load_recalculation_no_rationale_needed(self):
        r = _make_record(
            execution_type=ExecutionType.LOAD_RECALCULATION,
            coach_rationale=None,
        )
        r.validate_invariants()
