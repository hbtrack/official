from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from ..domain.entities import IngestionJob
from ..domain.rules import (
    RoleLabel, InsufficientPrivilege, IngestionJobNotFound, IngestionJobConflict,
    assert_can_list_jobs, assert_can_create_job, assert_can_get_job, assert_can_retry_job,
)
from ..infrastructure.repository import IngestionJobRepository


class ListIngestionJobs:
    def __init__(self, repo: IngestionJobRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        source_label: Optional[str] = None,
        ingestion_mode: Optional[str] = None,
        status_label: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        assert_can_list_jobs(role)
        items, total = self.repo.list_jobs(
            source_label=source_label,
            ingestion_mode=ingestion_mode,
            status_label=status_label,
            page=page,
            page_size=page_size,
        )
        return {"data": items, "page": page, "pageSize": page_size, "total": total}


class CreateIngestionJob:
    def __init__(self, repo: IngestionJobRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        source_label: str,
        ingestion_mode: str,
        payload_schema_ref: Optional[str] = None,
        mapping_profile: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        execution_binding_label: Optional[str] = None,
    ) -> Tuple[IngestionJob, bool]:
        """Returns (job, is_duplicate). is_duplicate=True when idempotencyKey already exists."""
        assert_can_create_job(role)
        # DR-ING-004: idempotency check
        if idempotency_key:
            existing = self.repo.get_by_idempotency_key(idempotency_key)
            if existing:
                return existing, True
        job = IngestionJob(
            id=uuid.uuid4(),
            source_label=source_label,
            ingestion_mode=ingestion_mode,
            payload_schema_ref=payload_schema_ref,
            mapping_profile=mapping_profile,
            idempotency_key=idempotency_key,
            execution_binding_label=execution_binding_label,
            status_label="queued",
            received_at=datetime.now(timezone.utc),
        )
        job.validate_invariants()
        return self.repo.save(job), False


class GetIngestionJob:
    def __init__(self, repo: IngestionJobRepository):
        self.repo = repo

    def execute(self, role: RoleLabel, job_id: UUID) -> IngestionJob:
        assert_can_get_job(role)
        job = self.repo.get_by_id(job_id)
        if job is None:
            raise IngestionJobNotFound(f"IngestionJob {job_id} not found")
        return job


class RetryIngestionJob:
    def __init__(self, repo: IngestionJobRepository):
        self.repo = repo

    def execute(self, role: RoleLabel, job_id: UUID) -> IngestionJob:
        original = self.repo.get_by_id(job_id)
        if original is None:
            raise IngestionJobNotFound(f"IngestionJob {job_id} not found")
        assert_can_retry_job(role, original)
        # INV-ING-004: create new job referencing original; new idempotencyKey
        retry_job = IngestionJob(
            id=uuid.uuid4(),
            source_label=original.source_label,
            ingestion_mode=original.ingestion_mode,
            payload_schema_ref=original.payload_schema_ref,
            mapping_profile=original.mapping_profile,
            idempotency_key=None,  # new job, no key duplication
            execution_binding_label=original.execution_binding_label,
            status_label="queued",
            received_at=datetime.now(timezone.utc),
            origin_job_id=job_id,
        )
        retry_job.validate_invariants()
        return self.repo.save(retry_job)
