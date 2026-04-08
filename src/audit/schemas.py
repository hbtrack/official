from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ninja import Schema

# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


class AuditEntryOut(Schema):
    id: UUID
    actor_user_id: UUID
    action: str
    occurred_at: datetime
    target_resource_id: Optional[UUID] = None
    target_resource_type: Optional[str] = None
    outcome_label: Optional[str] = None
    origin_label: Optional[str] = None
    correlation_id: Optional[UUID] = None
    before_summary: Optional[str] = None
    after_summary: Optional[str] = None

    @classmethod
    def from_domain(cls, e) -> "AuditEntryOut":
        return cls(
            id=e.id,
            actor_user_id=e.actor_user_id,
            action=e.action,
            occurred_at=e.occurred_at,
            target_resource_id=e.target_resource_id,
            target_resource_type=e.target_resource_type,
            outcome_label=e.outcome_label,
            origin_label=e.origin_label,
            correlation_id=e.correlation_id,
            before_summary=e.before_summary,
            after_summary=e.after_summary,
        )

class AuditEntryListOut(Schema):
    items: List[AuditEntryOut]
    nextPageToken: Optional[str] = None

class CreateAuditEntryIn(Schema):
    actorUserId: UUID
    action: str
    occurredAt: datetime
    targetResourceId: Optional[UUID] = None
    targetResourceType: Optional[str] = None
    outcomeLabel: Optional[str] = None
    originLabel: Optional[str] = None
    correlationId: Optional[UUID] = None
    beforeSummary: Optional[str] = None
    afterSummary: Optional[str] = None

class ExportOut(Schema):
    entries: List[AuditEntryOut]
    exportedCount: int
    exportedAt: datetime
    truncated: Optional[bool] = False

class ErrorOut(Schema):
    detail: str
