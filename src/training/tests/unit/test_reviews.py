"""
TM-036 — Session reviews.
Fonte: DOMAIN_RULES_TRAINING.md (DR-TRAIN-023, DR-TRAIN-024).
target-state: review workflow não implementado em domain layer.
"""
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest

from training.application.communication.commands import CloseFeedbackThreadUseCase
from training.application.communication.dto import CloseFeedbackThreadInput
from training.domain.entities.communication import FeedbackThread
from training.domain.common.enums import ConversationOutcome
from training.domain.rules import InsufficientPrivilege, RoleLabel

from .conftest import make_session


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

    def test_creator_can_close_thread_and_persist_resolution_summary(self):
        actor_id = uuid.uuid4()
        session = make_session()
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=session.id,
            created_by_user_id=actor_id,
            conversation_outcome=ConversationOutcome.PENDING_FOLLOWUP,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = session
        thread_repo = MagicMock()
        thread_repo.get_by_id.return_value = thread
        thread_repo.save.side_effect = lambda saved: saved

        result = CloseFeedbackThreadUseCase(session_repo, thread_repo).execute(
            CloseFeedbackThreadInput(
                session_id=session.id,
                thread_id=thread.id,
                actor_role=RoleLabel.COACH,
                actor_id=actor_id,
                resolution_summary="Sessão revisada com encaminhamento técnico",
            )
        )

        assert result.decision_text == "Sessão revisada com encaminhamento técnico"
        assert result.closed_at is not None
        assert result.updated_at == result.closed_at

    def test_non_creator_non_admin_cannot_close_thread(self):
        session = make_session()
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=session.id,
            created_by_user_id=uuid.uuid4(),
            conversation_outcome=ConversationOutcome.PENDING_FOLLOWUP,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = session
        thread_repo = MagicMock()
        thread_repo.get_by_id.return_value = thread

        with pytest.raises(InsufficientPrivilege, match="Somente o criador"):
            CloseFeedbackThreadUseCase(session_repo, thread_repo).execute(
                CloseFeedbackThreadInput(
                    session_id=session.id,
                    thread_id=thread.id,
                    actor_role=RoleLabel.COACH,
                    actor_id=uuid.uuid4(),
                    resolution_summary="Resumo",
                )
            )
