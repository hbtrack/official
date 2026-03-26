from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

VALID_STATUSES = frozenset(["queued", "processing", "completed", "failed"])
RETRYABLE_STATUSES = frozenset(["failed"])


@dataclass
class IngestionJob:
    id: UUID
    source_label: str
    ingestion_mode: str
    received_at: datetime
    completed_at: Optional[datetime] = None
    payload_schema_ref: Optional[str] = None
    mapping_profile: Optional[str] = None
    idempotency_key: Optional[str] = None
    execution_binding_label: Optional[str] = None
    status_label: str = "queued"
    error_message: Optional[str] = None
    origin_job_id: Optional[UUID] = None  # set for retry jobs

    def validate_invariants(self) -> None:
        # INV-ING-001: required fields
        if not self.id:
            raise ValueError("INV-ING-001: id is required")
        if not self.source_label:
            raise ValueError("INV-ING-001: sourceLabel is required")
        if not self.ingestion_mode:
            raise ValueError("INV-ING-001: ingestionMode is required")
        if not self.received_at:
            raise ValueError("INV-ING-001: receivedAt is required")
        # INV-ING-002: completedAt >= receivedAt
        if self.completed_at and self.completed_at < self.received_at:
            raise ValueError("INV-ING-002: completedAt must be >= receivedAt")
        # INV-ING-003: payloadSchemaRef and mappingProfile must both be present if either is set
        if bool(self.payload_schema_ref) != bool(self.mapping_profile):
            raise ValueError(
                "INV-ING-003: payloadSchemaRef and mappingProfile must both be "
                "present or both absent (explicit normalization contract required)"
            )

    def can_be_retried(self) -> bool:
        return self.status_label in RETRYABLE_STATUSES
