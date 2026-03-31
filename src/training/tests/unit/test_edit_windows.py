"""
TM-103 — Edit windows por role e tempo.
Fonte: INVARIANTS_TRAINING.md (INV-TRAIN-004).
target-state: regras de janela de edição não implementadas em rules.py ainda.
"""
import pytest

from training.domain.rules import (
    SessionNotMutable,
    assert_session_mutable,
    assert_session_not_historical,
)
from training.domain.entities import TrainingSessionStatus


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

    @pytest.mark.skip(reason="target-state: INV-TRAIN-004 role-based edit windows not yet in rules.py")
    def test_athlete_cannot_edit_after_window(self):
        pass

    @pytest.mark.skip(reason="target-state: INV-TRAIN-004 role-based edit windows not yet in rules.py")
    def test_coach_can_edit_within_extended_window(self):
        pass
