from __future__ import annotations
from uuid import UUID
from typing import List, Optional, Tuple

from ..domain.entities import IngestionJob
from .models import IngestionJobModel


def _job_from_model(m: IngestionJobModel) -> IngestionJob:
    return IngestionJob(
        id=m.id,
        source_label=m.source_label,
        ingestion_mode=m.ingestion_mode,
        payload_schema_ref=m.payload_schema_ref,
        mapping_profile=m.mapping_profile,
        idempotency_key=m.idempotency_key,
        execution_binding_label=m.execution_binding_label,
        status_label=m.status_label,
        received_at=m.received_at,
        completed_at=m.completed_at,
        error_message=m.error_message,
        origin_job_id=m.origin_job_id,
    )


class IngestionJobRepository:
    def save(self, job: IngestionJob) -> IngestionJob:
        obj, _ = IngestionJobModel.objects.update_or_create(
            id=job.id,
            defaults={
                "source_label": job.source_label,
                "ingestion_mode": job.ingestion_mode,
                "payload_schema_ref": job.payload_schema_ref,
                "mapping_profile": job.mapping_profile,
                "idempotency_key": job.idempotency_key,
                "execution_binding_label": job.execution_binding_label,
                "status_label": job.status_label,
                "received_at": job.received_at,
                "completed_at": job.completed_at,
                "error_message": job.error_message,
                "origin_job_id": job.origin_job_id,
            },
        )
        return _job_from_model(obj)

    def get_by_id(self, job_id: UUID) -> Optional[IngestionJob]:
        try:
            return _job_from_model(IngestionJobModel.objects.get(id=job_id))
        except IngestionJobModel.DoesNotExist:
            return None

    def get_by_idempotency_key(self, key: str) -> Optional[IngestionJob]:
        try:
            return _job_from_model(IngestionJobModel.objects.get(idempotency_key=key))
        except IngestionJobModel.DoesNotExist:
            return None

    def list_jobs(
        self,
        source_label: Optional[str] = None,
        ingestion_mode: Optional[str] = None,
        status_label: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[IngestionJob], int]:
        qs = IngestionJobModel.objects.all()
        if source_label:
            qs = qs.filter(source_label=source_label)
        if ingestion_mode:
            qs = qs.filter(ingestion_mode=ingestion_mode)
        if status_label:
            qs = qs.filter(status_label=status_label)
        total = qs.count()
        offset = (page - 1) * page_size
        items = qs[offset: offset + page_size]
        return [_job_from_model(m) for m in items], total
