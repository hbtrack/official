"""
TM-004, TM-027, TM-030, TM-039, TM-105, TM-110 — FSM training_session.
Fonte: STATE_MODEL_TRAINING.md + ADR-017 + INV-TRAIN-006 + INV-TRAIN-017.
"""
import pytest

from training.domain.common.enums import TrainingSessionStatus
from training.domain.rules import (
    InvalidStatusTransition,
    SessionNotMutable,
    assert_session_mutable,
    assert_valid_transition,
)


class TestTrainingSessionFSM:
    """INV-TRAIN-006: FSM fechada de 7 estados canônicos."""

    def test_draft_to_scheduled_valid(self):
        assert_valid_transition(TrainingSessionStatus.DRAFT, TrainingSessionStatus.SCHEDULED)

    def test_draft_to_published_invalid(self):
        """DRAFT → PUBLISHED é proibido por STATE_MODEL_TRAINING.md linha 96."""
        with pytest.raises(InvalidStatusTransition, match="INV-TRAIN-006"):
            assert_valid_transition(TrainingSessionStatus.DRAFT, TrainingSessionStatus.PUBLISHED)

    def test_scheduled_to_in_progress_invalid(self):
        """SCHEDULED → IN_PROGRESS é proibido por STATE_MODEL_TRAINING.md linha 100."""
        with pytest.raises(InvalidStatusTransition, match="INV-TRAIN-006"):
            assert_valid_transition(TrainingSessionStatus.SCHEDULED, TrainingSessionStatus.IN_PROGRESS)

    def test_draft_to_completed_invalid(self):
        with pytest.raises(InvalidStatusTransition, match="INV-TRAIN-006"):
            assert_valid_transition(TrainingSessionStatus.DRAFT, TrainingSessionStatus.COMPLETED)

    def test_completed_to_archived_valid(self):
        assert_valid_transition(TrainingSessionStatus.COMPLETED, TrainingSessionStatus.ARCHIVED)

    def test_archived_terminal(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_transition(TrainingSessionStatus.ARCHIVED, TrainingSessionStatus.DRAFT)

    def test_cancelled_terminal(self):
        with pytest.raises(InvalidStatusTransition):
            assert_valid_transition(TrainingSessionStatus.CANCELLED, TrainingSessionStatus.DRAFT)

    def test_in_progress_to_completed_valid(self):
        assert_valid_transition(TrainingSessionStatus.IN_PROGRESS, TrainingSessionStatus.COMPLETED)

    def test_in_progress_to_cancelled_valid(self):
        assert_valid_transition(TrainingSessionStatus.IN_PROGRESS, TrainingSessionStatus.CANCELLED)

    def test_published_to_in_progress_valid(self):
        assert_valid_transition(TrainingSessionStatus.PUBLISHED, TrainingSessionStatus.IN_PROGRESS)

    def test_published_to_scheduled_valid(self):
        """Unpublish: PUBLISHED → SCHEDULED (INV-TRAIN-017)."""
        assert_valid_transition(TrainingSessionStatus.PUBLISHED, TrainingSessionStatus.SCHEDULED)

    def test_scheduled_to_published_valid(self):
        assert_valid_transition(TrainingSessionStatus.SCHEDULED, TrainingSessionStatus.PUBLISHED)


class TestSessionMutability:
    """TM-030: sessão COMPLETED imutável por edição destrutiva."""

    def test_draft_mutable(self):
        assert_session_mutable(TrainingSessionStatus.DRAFT)

    def test_scheduled_mutable(self):
        assert_session_mutable(TrainingSessionStatus.SCHEDULED)

    def test_published_mutable(self):
        assert_session_mutable(TrainingSessionStatus.PUBLISHED)

    def test_completed_raises(self):
        with pytest.raises(SessionNotMutable):
            assert_session_mutable(TrainingSessionStatus.COMPLETED)

    def test_archived_raises(self):
        with pytest.raises(SessionNotMutable):
            assert_session_mutable(TrainingSessionStatus.ARCHIVED)

    def test_cancelled_raises(self):
        with pytest.raises(SessionNotMutable):
            assert_session_mutable(TrainingSessionStatus.CANCELLED)

    def test_in_progress_raises(self):
        with pytest.raises(SessionNotMutable):
            assert_session_mutable(TrainingSessionStatus.IN_PROGRESS)
