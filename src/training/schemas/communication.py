from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema


# ---------------------------------------------------------------------------
# Feedback Threads schemas
# ---------------------------------------------------------------------------

class FeedbackThreadOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    context_type: str
    context_ref_id: uuid.UUID
    conversation_outcome: str
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    athlete_id: Optional[uuid.UUID] = None
    content: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None


class FeedbackThreadListOut(Schema):
    data: List[FeedbackThreadOut]


class CreateFeedbackThreadIn(Schema):
    context_type: str
    context_ref_id: uuid.UUID
    conversation_outcome: str
    athlete_id: Optional[uuid.UUID] = None
    content: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None


class CloseFeedbackThreadIn(Schema):
    resolution_summary: str


# ---------------------------------------------------------------------------
# Attention Queue schemas
# ---------------------------------------------------------------------------

class AttentionQueueItemOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    severity: str
    reason_code: str
    target_entity_type: str
    target_entity_id: uuid.UUID
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[uuid.UUID] = None


class AttentionQueueListOut(Schema):
    data: List[AttentionQueueItemOut]


class ResolveAttentionQueueItemIn(Schema):
    resolution_evidence: str


class DismissAttentionQueueItemIn(Schema):
    dismissal_reason: str


class EscalateAttentionQueueItemIn(Schema):
    escalation_target: str
    escalation_note: str


# ---------------------------------------------------------------------------
# Recommendation schemas
# ---------------------------------------------------------------------------

class RecommendationOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    generated_by_rule: str
    action_type: str
    description: str
    status: str
    generated_by_module: str
    created_at: datetime
    updated_at: datetime
    priority: Optional[str] = None
    coach_note: Optional[str] = None
    dismissal_reason: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[uuid.UUID] = None


class RecommendationListOut(Schema):
    data: List[RecommendationOut]


class AcceptRecommendationIn(Schema):
    coach_note: Optional[str] = None


class DismissRecommendationIn(Schema):
    dismissal_reason: str


# ---------------------------------------------------------------------------
# Training Suggestion schemas (Onda E)
# ---------------------------------------------------------------------------

class SubmitTrainingSuggestionIn(Schema):
    athlete_id: uuid.UUID
    subject: str
    body: str
