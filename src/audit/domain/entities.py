from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

VALID_OUTCOMES = frozenset(["success", "failure", "partial"])


@dataclass
class AuditEntry:
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

    def validate_invariants(self) -> None:
        # INV-AUD-001: required fields
        if not self.id:
            raise ValueError("INV-AUD-001: id is required")
        if not self.actor_user_id:
            raise ValueError("INV-AUD-001: actorUserId is required")
        if not self.action:
            raise ValueError("INV-AUD-001: action is required")
        if not self.occurred_at:
            raise ValueError("INV-AUD-001: occurredAt is required")
        # INV-AUD-003: targetResourceId <-> targetResourceType
        if bool(self.target_resource_id) != bool(self.target_resource_type):
            raise ValueError(
                "INV-AUD-003: targetResourceId and targetResourceType must both "
                "be present or both absent"
            )
