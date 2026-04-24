from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

_CAMEL = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---------------------------------------------------------------------------
# Feedback Threads schemas
# ---------------------------------------------------------------------------

class FeedbackThreadOut(Schema):
    model_config = _CAMEL
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
    model_config = _CAMEL
    data: List[FeedbackThreadOut]


class CreateFeedbackThreadIn(Schema):
    model_config = _CAMEL
    context_type: str
    context_ref_id: uuid.UUID
    conversation_outcome: str
    athlete_id: Optional[uuid.UUID] = None
    content: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None


class CloseFeedbackThreadIn(Schema):
    model_config = _CAMEL
    resolution_summary: str


# ---------------------------------------------------------------------------
# Attention Queue schemas
# ---------------------------------------------------------------------------

class AttentionQueueItemOut(Schema):
    model_config = _CAMEL
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
    model_config = _CAMEL
    data: List[AttentionQueueItemOut]


class ResolveAttentionQueueItemIn(Schema):
    model_config = _CAMEL
    resolution_evidence: str


class DismissAttentionQueueItemIn(Schema):
    model_config = _CAMEL
    dismissal_reason: str


class EscalateAttentionQueueItemIn(Schema):
    model_config = _CAMEL
    escalation_target: str
    escalation_note: str


# ---------------------------------------------------------------------------
# Recommendation schemas
# ---------------------------------------------------------------------------

class RecommendationOut(Schema):
    model_config = _CAMEL
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
    model_config = _CAMEL
    data: List[RecommendationOut]


class AcceptRecommendationIn(Schema):
    model_config = _CAMEL
    coach_note: Optional[str] = None


class DismissRecommendationIn(Schema):
    model_config = _CAMEL
    dismissal_reason: str


# ---------------------------------------------------------------------------
# Training Suggestion schemas (Onda E)
# ---------------------------------------------------------------------------

class SubmitTrainingSuggestionIn(Schema):
    model_config = _CAMEL
    athlete_id: uuid.UUID
    subject: str
    body: str
