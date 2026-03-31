"""
TM-032..TM-035, TM-108, TM-109 — FeedbackThread invariants.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-020, DR-TRAIN-021, DR-TRAIN-022).
"""
import uuid
from datetime import datetime, timezone, timedelta

import pytest

from training.domain.entities import (
    ConversationOutcome,
    FeedbackThread,
)


def _make_thread(**kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        conversation_outcome=ConversationOutcome.REFLECTION_DOCUMENTED,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    defaults.update(kwargs)
    return FeedbackThread(**defaults)


class TestFeedbackThreadInvariants:
    """DR-TRAIN-022: campos condicionais por conversationOutcome."""

    def test_followup_scheduled_without_followup_at_raises(self):
        thread = _make_thread(
            conversation_outcome=ConversationOutcome.FOLLOWUP_SCHEDULED,
            follow_up_at=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-022"):
            thread.validate_invariants()

    def test_followup_scheduled_with_date_passes(self):
        thread = _make_thread(
            conversation_outcome=ConversationOutcome.FOLLOWUP_SCHEDULED,
            follow_up_at=datetime.now(tz=timezone.utc) + timedelta(days=7),
        )
        thread.validate_invariants()

    def test_commitment_made_requires_text(self):
        thread = _make_thread(
            conversation_outcome=ConversationOutcome.COMMITMENT_MADE,
            commitment_text=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-022"):
            thread.validate_invariants()

    def test_commitment_made_with_text_passes(self):
        thread = _make_thread(
            conversation_outcome=ConversationOutcome.COMMITMENT_MADE,
            commitment_text="Atleta se comprometeu a melhorar posicionamento",
        )
        thread.validate_invariants()

    def test_decision_recorded_requires_text(self):
        thread = _make_thread(
            conversation_outcome=ConversationOutcome.DECISION_RECORDED,
            decision_text=None,
        )
        with pytest.raises(ValueError, match="DR-TRAIN-022"):
            thread.validate_invariants()

    def test_decision_recorded_with_text_passes(self):
        thread = _make_thread(
            conversation_outcome=ConversationOutcome.DECISION_RECORDED,
            decision_text="Decisão: rodar pivô na segunda fase",
        )
        thread.validate_invariants()

    def test_reflection_documented_no_extra_fields_required(self):
        thread = _make_thread(
            conversation_outcome=ConversationOutcome.REFLECTION_DOCUMENTED,
        )
        thread.validate_invariants()
