"""
TM-036 — Session reviews.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-023, DR-TRAIN-024).
target-state: review workflow não implementado em domain layer.
"""
import uuid
from datetime import datetime, timezone, timedelta

import pytest

from training.domain.entities.communication import FeedbackThread
from training.domain.common.enums import ConversationOutcome


class TestReviewFeedbackFlow:
    """DR-TRAIN-023/024: review workflow via FeedbackThread."""

    def test_pending_followup_thread_creates(self):
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            conversation_outcome=ConversationOutcome.PENDING_FOLLOWUP,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        thread.validate_invariants()

    def test_reflection_documented_passes(self):
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            conversation_outcome=ConversationOutcome.REFLECTION_DOCUMENTED,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        thread.validate_invariants()

    @pytest.mark.skip(reason="target-state: review approval workflow not yet in domain layer")
    def test_review_requires_completed_session(self):
        pass

    @pytest.mark.skip(reason="target-state: review approval workflow not yet in domain layer")
    def test_review_summary_field_required(self):
        pass
