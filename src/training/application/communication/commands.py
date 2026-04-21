from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from ...domain.entities import (
    AttentionQueueItem,
    ConversationOutcome,
    FeedbackThread,
    Recommendation,
    RecommendationStatus,
    TrainingSessionStatus,
)
from ...domain.rules import (
    AttentionQueueConflict,
    AttentionQueueItemNotFound,
    FeedbackThreadAlreadyClosed,
    FeedbackThreadNotFound,
    InsufficientPrivilege,
    RecommendationConflict,
    RecommendationNotFound,
    RoleLabel,
    SuggestionStateConflict,
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
    AcceptRecommendationInput,
    CloseFeedbackThreadInput,
    CreateFeedbackThreadInput,
    DismissAttentionQueueItemInput,
    DismissRecommendationInput,
    EscalateAttentionQueueItemInput,
    ResolveAttentionQueueItemInput,
    SubmitTrainingSuggestionInput,
)


def _append_note(existing: Optional[str], prefix: str, detail: str) -> str:
    parts = [existing.strip()] if existing and existing.strip() else []
    parts.append(f"{prefix}: {detail}")
    return "\n".join(parts)


class CreateFeedbackThreadUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._thread_repo = thread_repo

    def execute(self, inp: CreateFeedbackThreadInput) -> FeedbackThread:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)

        context_type = inp.context_type
        athlete_id = inp.athlete_id
        block_id = None
        objective_id = None
        if context_type == "SESSION":
            if inp.context_ref_id != inp.session_id:
                raise ValueError("contextRefId deve apontar para a própria sessão quando contextType=SESSION")
        elif context_type == "BLOCK":
            block_id = inp.context_ref_id
        elif context_type == "OBJECTIVE":
            objective_id = inp.context_ref_id
        elif context_type == "ATHLETE":
            athlete_id = athlete_id or inp.context_ref_id
        elif context_type not in {"EVIDENCE", "GROUP"}:
            raise ValueError(f"contextType inválido: {context_type}")

        now = datetime.now(tz=timezone.utc)
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            block_id=block_id,
            athlete_id=athlete_id,
            objective_id=objective_id,
            created_by_user_id=inp.actor_id,
            subject=context_type,
            body=inp.content,
            conversation_outcome=ConversationOutcome(inp.conversation_outcome),
            follow_up_at=inp.follow_up_at,
            commitment_text=inp.commitment_text,
            decision_text=inp.decision_text,
            created_at=now,
            updated_at=now,
        )
        thread.validate_invariants()
        return self._thread_repo.save(thread)


class CloseFeedbackThreadUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._thread_repo = thread_repo

    def execute(self, inp: CloseFeedbackThreadInput) -> FeedbackThread:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        thread = self._thread_repo.get_by_id(inp.thread_id)
        if not thread or thread.session_id != inp.session_id:
            raise FeedbackThreadNotFound(
                f"Feedback thread {inp.thread_id} não encontrada para a sessão {inp.session_id}"
            )
        if thread.closed_at is not None:
            raise FeedbackThreadAlreadyClosed("Feedback thread já está fechada")
        if inp.actor_id != thread.created_by_user_id and inp.actor_role not in {
            RoleLabel.ADMIN,
            RoleLabel.COORDINATOR,
        }:
            raise InsufficientPrivilege(
                "Somente o criador da thread ou admin/coordinator pode fechá-la"
            )
        thread.closed_at = datetime.now(tz=timezone.utc)
        thread.updated_at = thread.closed_at
        thread.decision_text = inp.resolution_summary
        return self._thread_repo.save(thread)


class ResolveAttentionQueueItemUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: ResolveAttentionQueueItemInput) -> AttentionQueueItem:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        item = self._queue_repo.get_by_id(inp.item_id)
        if not item or item.session_id != inp.session_id:
            raise AttentionQueueItemNotFound(
                f"Attention queue item {inp.item_id} não encontrado para a sessão {inp.session_id}"
            )
        if item.resolved_at or item.dismissed_at or item.escalated_at:
            raise AttentionQueueConflict("Attention queue item já foi actionado")
        now = datetime.now(tz=timezone.utc)
        item.resolved_at = now
        item.resolved_by = inp.actor_id
        item.updated_at = now
        item.notes = _append_note(item.notes, "RESOLUTION", inp.resolution_evidence)
        return self._queue_repo.save(item)


class DismissAttentionQueueItemUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: DismissAttentionQueueItemInput) -> AttentionQueueItem:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        item = self._queue_repo.get_by_id(inp.item_id)
        if not item or item.session_id != inp.session_id:
            raise AttentionQueueItemNotFound(
                f"Attention queue item {inp.item_id} não encontrado para a sessão {inp.session_id}"
            )
        if item.resolved_at or item.dismissed_at or item.escalated_at:
            raise AttentionQueueConflict("Attention queue item já foi actionado")
        now = datetime.now(tz=timezone.utc)
        item.dismissed_at = now
        item.resolved_by = inp.actor_id
        item.updated_at = now
        item.notes = _append_note(item.notes, "DISMISSAL", inp.dismissal_reason)
        return self._queue_repo.save(item)


class EscalateAttentionQueueItemUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: EscalateAttentionQueueItemInput) -> AttentionQueueItem:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        if inp.escalation_target not in {"MEDICAL", "COORDINATOR", "HEAD_COACH"}:
            raise ValueError("escalationTarget inválido")
        item = self._queue_repo.get_by_id(inp.item_id)
        if not item or item.session_id != inp.session_id:
            raise AttentionQueueItemNotFound(
                f"Attention queue item {inp.item_id} não encontrado para a sessão {inp.session_id}"
            )
        if item.resolved_at or item.dismissed_at or item.escalated_at:
            raise AttentionQueueConflict("Attention queue item já foi actionado")
        now = datetime.now(tz=timezone.utc)
        item.escalated_at = now
        item.resolved_by = inp.actor_id
        item.updated_at = now
        item.notes = _append_note(
            item.notes,
            f"ESCALATED[{inp.escalation_target}]",
            inp.escalation_note,
        )
        return self._queue_repo.save(item)


class AcceptRecommendationUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, recommendation_repo: RecommendationRepository):
        self._session_repo = session_repo
        self._recommendation_repo = recommendation_repo

    def execute(self, inp: AcceptRecommendationInput) -> Recommendation:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        recommendation = self._recommendation_repo.get_by_id(inp.recommendation_id)
        if not recommendation or recommendation.session_id != inp.session_id:
            raise RecommendationNotFound(
                f"Recommendation {inp.recommendation_id} não encontrada para a sessão {inp.session_id}"
            )
        if recommendation.status != RecommendationStatus.PENDING:
            raise RecommendationConflict("Recommendation não está em status PENDING")
        now = datetime.now(tz=timezone.utc)
        recommendation.status = RecommendationStatus.ACCEPTED
        recommendation.coach_note = inp.coach_note
        recommendation.dismissal_reason = None
        recommendation.resolved_at = now
        recommendation.resolved_by_user_id = inp.actor_id
        recommendation.updated_at = now
        recommendation.validate_invariants()
        return self._recommendation_repo.save(recommendation)


class DismissRecommendationUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, recommendation_repo: RecommendationRepository):
        self._session_repo = session_repo
        self._recommendation_repo = recommendation_repo

    def execute(self, inp: DismissRecommendationInput) -> Recommendation:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        recommendation = self._recommendation_repo.get_by_id(inp.recommendation_id)
        if not recommendation or recommendation.session_id != inp.session_id:
            raise RecommendationNotFound(
                f"Recommendation {inp.recommendation_id} não encontrada para a sessão {inp.session_id}"
            )
        if recommendation.status != RecommendationStatus.PENDING:
            raise RecommendationConflict("Recommendation não está em status PENDING")
        now = datetime.now(tz=timezone.utc)
        recommendation.status = RecommendationStatus.DISMISSED
        recommendation.dismissal_reason = inp.dismissal_reason
        recommendation.coach_note = None
        recommendation.resolved_at = now
        recommendation.resolved_by_user_id = inp.actor_id
        recommendation.updated_at = now
        recommendation.validate_invariants()
        return self._recommendation_repo.save(recommendation)


class SubmitTrainingSuggestionUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, feedback_thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._feedback_thread_repo = feedback_thread_repo

    def execute(self, inp: SubmitTrainingSuggestionInput) -> FeedbackThread:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        if session.status not in {TrainingSessionStatus.PUBLISHED, TrainingSessionStatus.IN_PROGRESS}:
            raise SuggestionStateConflict("Sugestão só pode ser submetida em sessões PUBLISHED ou IN_PROGRESS")
        if inp.actor_role != RoleLabel.ATHLETE or inp.actor_id != inp.athlete_id:
            raise InsufficientPrivilege("Athlete só pode submeter sugestão para si mesmo")
        now = datetime.now(tz=timezone.utc)
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            created_by_user_id=inp.actor_id,
            subject=inp.subject,
            body=inp.body,
            conversation_outcome=ConversationOutcome.PENDING_FOLLOWUP,
            created_at=now,
            updated_at=now,
        )
        thread.validate_invariants()
        return self._feedback_thread_repo.save(thread)
