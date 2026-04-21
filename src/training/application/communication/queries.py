from __future__ import annotations

from ...domain.entities import AttentionQueueItem, FeedbackThread, Recommendation
from ...domain.policies.feedback_context import feedback_context_type
from ...domain.rules import (
    TrainingSessionNotFound,
    assert_can_modify_session,
)
from ...infrastructure.repository import (
    AttentionQueueRepository,
    FeedbackThreadRepository,
    RecommendationRepository,
    TrainingSessionRepository,
)
from .dto import (
    ListAttentionQueueItemsInput,
    ListChatMessagesInput,
    ListFeedbackThreadsInput,
    ListRecommendationsInput,
)


class ListFeedbackThreadsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._thread_repo = thread_repo

    def execute(self, inp: ListFeedbackThreadsInput) -> list[FeedbackThread]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        items = self._thread_repo.list_by_session(inp.session_id)
        if inp.context_type:
            items = [item for item in items if feedback_context_type(item) == inp.context_type]
        if inp.athlete_id:
            items = [item for item in items if item.athlete_id == inp.athlete_id]
        return items


class ListAttentionQueueItemsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: ListAttentionQueueItemsInput) -> list[AttentionQueueItem]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        return self._queue_repo.list_by_session(
            session_id=inp.session_id,
            resolved=inp.resolved,
            severity=inp.severity,
        )


class ListRecommendationsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, recommendation_repo: RecommendationRepository):
        self._session_repo = session_repo
        self._recommendation_repo = recommendation_repo

    def execute(self, inp: ListRecommendationsInput) -> list[Recommendation]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        return self._recommendation_repo.list_by_session(inp.session_id, status=inp.status)


class ListChatMessagesUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, feedback_thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._feedback_thread_repo = feedback_thread_repo

    def execute(self, inp: ListChatMessagesInput) -> list[FeedbackThread]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        return self._feedback_thread_repo.list_by_session(inp.session_id)
