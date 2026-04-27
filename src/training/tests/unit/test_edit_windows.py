"""
TM-103 — Edit windows por role e tempo.
Fonte: INVARIANTS_TRAINING.md (INV-TRAIN-004).
target-state: regras de janela de edição não implementadas em rules.py ainda.
"""
import inspect

import pytest

from training.domain.rules import (
    SessionNotMutable,
    assert_session_mutable,
    assert_session_not_historical,
)
from training.domain.common.enums import TrainingSessionStatus
from training.domain.policies.session_access import SessionAccessPolicy


class TestEditWindows:
    """INV-TRAIN-004: janela de edição por role/tempo."""

    def test_mutable_states_allow_edit(self):
        for state in (
            TrainingSessionStatus.DRAFT,
            TrainingSessionStatus.SCHEDULED,
            TrainingSessionStatus.PUBLISHED,
        ):
            assert_session_mutable(state)

    def test_immutable_states_deny_edit(self):
        for state in (
            TrainingSessionStatus.IN_PROGRESS,
            TrainingSessionStatus.COMPLETED,
            TrainingSessionStatus.CANCELLED,
            TrainingSessionStatus.ARCHIVED,
        ):
            with pytest.raises(SessionNotMutable):
                assert_session_mutable(state)

    def test_status_mutability_rule_has_no_role_or_timestamp_inputs(self):
        assert list(inspect.signature(assert_session_mutable).parameters) == ["status"]

    def test_policy_mutability_guard_is_based_on_role_and_state_only(self):
        source = inspect.getsource(SessionAccessPolicy.require_mutable)
        assert "session_at" not in source
        assert "started_at" not in source
        assert "ended_at" not in source
        assert "created_at" not in source
