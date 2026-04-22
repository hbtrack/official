"""
Agregado: FeedbackThread + AttentionQueueItem + Recommendation.

Colaboração coach-atleta e fila de atenção analítica.
TRAIN-DEC-010/015, DR-TRAIN-020/021/022.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..common.enums import (
    ConversationOutcome,
    RecommendationActionType,
    RecommendationPriority,
    RecommendationStatus,
)


@dataclass
class FeedbackThread:
    """
    Thread de feedback técnico.
    TRAIN-DEC-010/015. DR-TRAIN-020/021/022.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    created_by_user_id: uuid.UUID
    conversation_outcome: ConversationOutcome
    created_at: datetime
    updated_at: datetime

    block_id: Optional[uuid.UUID] = None
    athlete_id: Optional[uuid.UUID] = None
    objective_id: Optional[uuid.UUID] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None
    closed_at: Optional[datetime] = None

    def validate_invariants(self) -> None:
        if self.conversation_outcome == ConversationOutcome.FOLLOWUP_SCHEDULED:
            if self.follow_up_at is None:
                raise ValueError(
                    "DR-TRAIN-022: followUpAt obrigatório quando outcome=FOLLOWUP_SCHEDULED"
                )
        if self.conversation_outcome == ConversationOutcome.COMMITMENT_MADE:
            if not self.commitment_text:
                raise ValueError(
                    "DR-TRAIN-022: commitmentText obrigatório quando outcome=COMMITMENT_MADE"
                )
        if self.conversation_outcome == ConversationOutcome.DECISION_RECORDED:
            if not self.decision_text:
                raise ValueError(
                    "DR-TRAIN-022: decisionText obrigatório quando outcome=DECISION_RECORDED"
                )


@dataclass
class AttentionQueueItem:
    """Item da fila de atenção técnica do treinador."""
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    reason: str
    severity: str
    created_at: datetime
    updated_at: datetime

    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None
    dismissed_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class Recommendation:
    """Recomendação analítica pendente de decisão explícita do coach."""

    id: uuid.UUID
    session_id: uuid.UUID
    generated_by_rule: str
    action_type: RecommendationActionType
    description: str
    status: RecommendationStatus
    generated_by_module: str
    created_at: datetime
    updated_at: datetime

    priority: Optional[RecommendationPriority] = None
    coach_note: Optional[str] = None
    dismissal_reason: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[uuid.UUID] = None

    def validate_invariants(self) -> None:
        if not self.generated_by_rule or len(self.generated_by_rule) > 128:
            raise ValueError("generatedByRule é obrigatório e deve ter <= 128 caracteres")
        if not self.generated_by_rule.replace("_", "").isalnum() or self.generated_by_rule.upper() != self.generated_by_rule:
            raise ValueError("generatedByRule deve estar em UPPER_SNAKE_CASE")
        if not self.description or len(self.description) > 1000:
            raise ValueError("description é obrigatória e deve ter <= 1000 caracteres")
        if not self.generated_by_module or len(self.generated_by_module) > 64:
            raise ValueError("generatedByModule é obrigatório e deve ter <= 64 caracteres")
        if self.status == RecommendationStatus.DISMISSED and not self.dismissal_reason:
            raise ValueError("dismissalReason é obrigatório quando status=DISMISSED")
        if self.status == RecommendationStatus.PENDING:
            if self.dismissal_reason or self.coach_note or self.resolved_at or self.resolved_by_user_id:
                raise ValueError("Recommendation pendente não pode ter campos de resolução preenchidos")
        else:
            if self.resolved_at is None or self.resolved_by_user_id is None:
                raise ValueError("Recommendation resolvida exige resolvedAt e resolvedByUserId")
        if self.coach_note and len(self.coach_note) > 500:
            raise ValueError("coachNote deve ter <= 500 caracteres")
        if self.dismissal_reason and len(self.dismissal_reason) > 500:
            raise ValueError("dismissalReason deve ter <= 500 caracteres")


__all__ = ["FeedbackThread", "AttentionQueueItem", "Recommendation"]
