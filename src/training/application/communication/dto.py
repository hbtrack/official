from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...domain.rules import RoleLabel


@dataclass
class ListFeedbackThreadsInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    context_type: Optional[str] = None
    athlete_id: Optional[uuid.UUID] = None


@dataclass
class CreateFeedbackThreadInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    context_type: str
    context_ref_id: uuid.UUID
    conversation_outcome: str
    athlete_id: Optional[uuid.UUID] = None
    content: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None


@dataclass
class CloseFeedbackThreadInput:
    session_id: uuid.UUID
    thread_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    resolution_summary: str


@dataclass
class ListAttentionQueueItemsInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    severity: Optional[str] = None
    resolved: bool = False


@dataclass
class ResolveAttentionQueueItemInput:
    session_id: uuid.UUID
    item_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    resolution_evidence: str


@dataclass
class DismissAttentionQueueItemInput:
    session_id: uuid.UUID
    item_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    dismissal_reason: str


@dataclass
class EscalateAttentionQueueItemInput:
    session_id: uuid.UUID
    item_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    escalation_target: str
    escalation_note: str


@dataclass
class ListRecommendationsInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    status: Optional[str] = None


@dataclass
class AcceptRecommendationInput:
    session_id: uuid.UUID
    recommendation_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    coach_note: Optional[str] = None


@dataclass
class DismissRecommendationInput:
    session_id: uuid.UUID
    recommendation_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    dismissal_reason: str


@dataclass
class ListChatMessagesInput:
    session_id: uuid.UUID
    actor_role: RoleLabel


@dataclass
class SubmitTrainingSuggestionInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    athlete_id: uuid.UUID
    subject: str
    body: str
