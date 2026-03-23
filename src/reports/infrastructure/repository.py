from __future__ import annotations
from uuid import UUID
from typing import List, Optional, Tuple

from ..domain.entities import ReportJob
from .models import ReportJobModel


def _job_from_model(m: ReportJobModel) -> ReportJob:
    return ReportJob(
        id=m.id,
        owner_user_id=m.owner_user_id,
        report_type=m.report_type,
        format_label=m.format_label,
        parameter_summary=m.parameter_summary,
        source_metric_names=m.source_metric_names or [],
        generated_artifact_ref=m.generated_artifact_ref,
        retention_label=m.retention_label,
        status_label=m.status_label,
        requested_at=m.requested_at,
        completed_at=m.completed_at,
        error_message=m.error_message,
    )


class ReportJobRepository:
    def save(self, job: ReportJob) -> ReportJob:
        obj, _ = ReportJobModel.objects.update_or_create(
            id=job.id,
            defaults={
                "owner_user_id": job.owner_user_id,
                "report_type": job.report_type,
                "format_label": job.format_label,
                "parameter_summary": job.parameter_summary,
                "source_metric_names": job.source_metric_names,
                "generated_artifact_ref": job.generated_artifact_ref,
                "retention_label": job.retention_label,
                "status_label": job.status_label,
                "requested_at": job.requested_at,
                "completed_at": job.completed_at,
                "error_message": job.error_message,
            },
        )
        return _job_from_model(obj)

    def get_by_id(self, job_id: UUID) -> Optional[ReportJob]:
        try:
            return _job_from_model(ReportJobModel.objects.get(id=job_id))
        except ReportJobModel.DoesNotExist:
            return None

    def list_jobs(
        self,
        requester_id: Optional[UUID] = None,
        owner_scoped: bool = False,
        report_type: Optional[str] = None,
        format_label: Optional[str] = None,
        status_label: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        owner_user_id: Optional[UUID] = None,
        page_size: int = 20,
        page_token: Optional[str] = None,
    ) -> Tuple[List[ReportJob], Optional[str]]:
        qs = ReportJobModel.objects.all()
        if owner_scoped and requester_id:
            qs = qs.filter(owner_user_id=requester_id)
        if owner_user_id:
            qs = qs.filter(owner_user_id=owner_user_id)
        if report_type:
            qs = qs.filter(report_type=report_type)
        if format_label:
            qs = qs.filter(format_label=format_label)
        if status_label:
            qs = qs.filter(status_label=status_label)
        if date_from:
            qs = qs.filter(requested_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(requested_at__date__lte=date_to)

        offset = 0
        if page_token:
            try:
                offset = int(page_token)
            except ValueError:
                offset = 0

        total = qs.count()
        items = qs[offset: offset + page_size]
        jobs = [_job_from_model(m) for m in items]
        next_token = str(offset + page_size) if (offset + page_size) < total else None
        return jobs, next_token
