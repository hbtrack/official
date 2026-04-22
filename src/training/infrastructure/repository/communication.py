"""Repositórios dos agregados de comunicação: FeedbackThread, AttentionQueue, Recommendation."""
from __future__ import annotations

import uuid
from typing import Optional

from ...domain.entities import (
    AttentionQueueItem,
    ConversationOutcome,
    FeedbackThread,
    Recommendation,
    RecommendationActionType,
    RecommendationPriority,
    RecommendationStatus,
)
from ..models import (
    AttentionQueueItemModel,
    FeedbackThreadModel,
    RecommendationModel,
)


class FeedbackThreadRepository:
    def get_by_id(self, id: uuid.UUID) -> Optional[FeedbackThread]:
        try:
            return self._to_domain(FeedbackThreadModel.objects.get(pk=id))
        except FeedbackThreadModel.DoesNotExist:
            return None

    def list_by_session(self, session_id: uuid.UUID) -> list[FeedbackThread]:
        return [
            self._to_domain(m)
            for m in FeedbackThreadModel.objects.filter(session_id=session_id).order_by("-created_at")
        ]

    def save(self, thread: FeedbackThread) -> FeedbackThread:
        defaults = {
            "session_id": thread.session_id,
            "block_id": thread.block_id,
            "athlete_id": thread.athlete_id,
            "objective_id": thread.objective_id,
            "created_by_user_id": thread.created_by_user_id,
            "subject": thread.subject or "",
            "body": thread.body or "",
            "conversation_outcome": thread.conversation_outcome.value,
            "follow_up_at": thread.follow_up_at,
            "commitment_text": thread.commitment_text or "",
            "decision_text": thread.decision_text or "",
            "closed_at": thread.closed_at,
        }
        m, _ = FeedbackThreadModel.objects.update_or_create(pk=thread.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: FeedbackThreadModel) -> FeedbackThread:
        return FeedbackThread(
            id=m.id,
            session_id=m.session_id,
            block_id=m.block_id,
            athlete_id=m.athlete_id,
            objective_id=m.objective_id,
            created_by_user_id=m.created_by_user_id,
            subject=m.subject or None,
            body=m.body or None,
            conversation_outcome=ConversationOutcome(m.conversation_outcome),
            follow_up_at=m.follow_up_at,
            commitment_text=m.commitment_text or None,
            decision_text=m.decision_text or None,
            closed_at=m.closed_at,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class AttentionQueueRepository:
    def list_by_session(
        self,
        session_id: uuid.UUID,
        resolved: bool = False,
        severity: Optional[str] = None,
    ) -> list[AttentionQueueItem]:
        qs = AttentionQueueItemModel.objects.filter(session_id=session_id)
        if severity:
            qs = qs.filter(severity=severity)
        if resolved:
            qs = qs.exclude(
                resolved_at__isnull=True,
                dismissed_at__isnull=True,
                escalated_at__isnull=True,
            )
        else:
            qs = qs.filter(
                resolved_at__isnull=True,
                dismissed_at__isnull=True,
                escalated_at__isnull=True,
            )
        return [self._to_domain(m) for m in qs.order_by("-created_at")]

    def get_by_id(self, id: uuid.UUID) -> Optional[AttentionQueueItem]:
        try:
            return self._to_domain(AttentionQueueItemModel.objects.get(pk=id))
        except AttentionQueueItemModel.DoesNotExist:
            return None

    def save(self, item: AttentionQueueItem) -> AttentionQueueItem:
        defaults = {
            "session_id": item.session_id,
            "athlete_id": item.athlete_id,
            "reason": item.reason,
            "severity": item.severity,
            "resolved_at": item.resolved_at,
            "resolved_by": item.resolved_by,
            "dismissed_at": item.dismissed_at,
            "escalated_at": item.escalated_at,
            "notes": item.notes or "",
        }
        m, _ = AttentionQueueItemModel.objects.update_or_create(pk=item.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: AttentionQueueItemModel) -> AttentionQueueItem:
        return AttentionQueueItem(
            id=m.id,
            session_id=m.session_id,
            athlete_id=m.athlete_id,
            reason=m.reason,
            severity=m.severity,
            resolved_at=m.resolved_at,
            resolved_by=m.resolved_by,
            dismissed_at=m.dismissed_at,
            escalated_at=m.escalated_at,
            notes=m.notes or None,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class RecommendationRepository:
    def list_by_session(
        self,
        session_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> list[Recommendation]:
        qs = RecommendationModel.objects.filter(session_id=session_id).order_by("-created_at")
        if status:
            qs = qs.filter(status=status)
        return [self._to_domain(m) for m in qs]

    def get_by_id(self, id: uuid.UUID) -> Optional[Recommendation]:
        try:
            return self._to_domain(RecommendationModel.objects.get(pk=id))
        except RecommendationModel.DoesNotExist:
            return None

    def save(self, recommendation: Recommendation) -> Recommendation:
        defaults = {
            "session_id": recommendation.session_id,
            "generated_by_rule": recommendation.generated_by_rule,
            "action_type": recommendation.action_type.value,
            "description": recommendation.description,
            "status": recommendation.status.value,
            "priority": recommendation.priority.value if recommendation.priority else None,
            "generated_by_module": recommendation.generated_by_module,
            "coach_note": recommendation.coach_note or "",
            "dismissal_reason": recommendation.dismissal_reason or "",
            "resolved_at": recommendation.resolved_at,
            "resolved_by_user_id": recommendation.resolved_by_user_id,
        }
        m, _ = RecommendationModel.objects.update_or_create(pk=recommendation.id, defaults=defaults)
        return self._to_domain(m)

    def _to_domain(self, m: RecommendationModel) -> Recommendation:
        return Recommendation(
            id=m.id,
            session_id=m.session_id,
            generated_by_rule=m.generated_by_rule,
            action_type=RecommendationActionType(m.action_type),
            description=m.description,
            status=RecommendationStatus(m.status),
            priority=RecommendationPriority(m.priority) if m.priority else None,
            generated_by_module=m.generated_by_module,
            coach_note=m.coach_note or None,
            dismissal_reason=m.dismissal_reason or None,
            resolved_at=m.resolved_at,
            resolved_by_user_id=m.resolved_by_user_id,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


__all__ = [
    "FeedbackThreadRepository",
    "AttentionQueueRepository",
    "RecommendationRepository",
]
