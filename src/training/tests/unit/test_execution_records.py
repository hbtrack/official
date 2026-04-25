"""
TM-028, TM-029, TM-106, TM-107 — ExecutionRecord invariants.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-015, DR-TRAIN-017, DR-TRAIN-019).
"""
import uuid
from datetime import datetime, timezone

import pytest

from training.domain.entities.execution import ExecutionRecord
from training.domain.common.enums import ExecutionType


def _make_record(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        execution_type=ExecutionType.SESSION_EXECUTION,
        recorded_at=datetime.now(tz=timezone.utc),
        created_by_user_id=uuid.uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return ExecutionRecord(**defaults)


class TestExecutionRecordInvariants:
    """DR-TRAIN-019: LIVE_ADJUSTMENT e CONSTRAINT_OVERRIDE exigem coachRationale >= 5 chars."""

    def test_session_execution_no_rationale_needed(self):
        r = _make_record(execution_type=ExecutionType.SESSION_EXECUTION)
        r.validate_invariants()

    def test_live_adjustment_requires_rationale(self):
        r = _make_record(
            execution_type=ExecutionType.LIVE_ADJUSTMENT,
            coach_rationale=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-019"):
            r.validate_invariants()

    def test_live_adjustment_short_rationale_raises(self):
        r = _make_record(
            execution_type=ExecutionType.LIVE_ADJUSTMENT,
            coach_rationale="abc",
        )
        with pytest.raises(ValueError, match="DR-TRAIN-019"):
            r.validate_invariants()

    def test_live_adjustment_with_rationale_passes(self):
        r = _make_record(
            execution_type=ExecutionType.LIVE_ADJUSTMENT,
            coach_rationale="Atleta demonstrou fadiga excessiva",
        )
        r.validate_invariants()

    def test_constraint_override_requires_rationale(self):
        r = _make_record(
            execution_type=ExecutionType.CONSTRAINT_OVERRIDE,
            coach_rationale=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-019"):
            r.validate_invariants()

    def test_constraint_override_with_rationale_passes(self):
        r = _make_record(
            execution_type=ExecutionType.CONSTRAINT_OVERRIDE,
            coach_rationale="Override necessário para adaptação de carga",
        )
        r.validate_invariants()

    def test_block_execution_no_rationale_needed(self):
        r = _make_record(execution_type=ExecutionType.BLOCK_EXECUTION)
        r.validate_invariants()

    def test_planned_unit_too_long_raises(self):
        r = _make_record(planned_unit="a" * 33)
        with pytest.raises(ValueError):
            r.validate_invariants()

    def test_actual_unit_too_long_raises(self):
        r = _make_record(actual_unit="a" * 33)
        with pytest.raises(ValueError):
            r.validate_invariants()
