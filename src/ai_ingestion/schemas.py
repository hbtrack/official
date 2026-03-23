from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ninja import Schema


class IngestionJobOut(Schema):
    id: UUID
    source_label: str
    ingestion_mode: str
    payload_schema_ref: Optional[str] = None
    mapping_profile: Optional[str] = None
    idempotency_key: Optional[str] = None
    execution_binding_label: Optional[str] = None
    status_label: str
    received_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    origin_job_id: Optional[UUID] = None

    @classmethod
    def from_domain(cls, job) -> "IngestionJobOut":
        return cls(
            id=job.id,
            source_label=job.source_label,
            ingestion_mode=job.ingestion_mode,
            payload_schema_ref=job.payload_schema_ref,
            mapping_profile=job.mapping_profile,
            idempotency_key=job.idempotency_key,
            execution_binding_label=job.execution_binding_label,
            status_label=job.status_label,
            received_at=job.received_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            origin_job_id=job.origin_job_id,
        )


class IngestionJobListOut(Schema):
    data: List[IngestionJobOut]
    page: int
    pageSize: int
    total: int


class CreateIngestionJobIn(Schema):
    sourceLabel: str
    ingestionMode: str
    payloadSchemaRef: Optional[str] = None
    mappingProfile: Optional[str] = None
    idempotencyKey: Optional[str] = None
    executionBindingLabel: Optional[str] = None


class ErrorOut(Schema):
    detail: str
