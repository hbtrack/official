from __future__ import annotations
from typing import Optional
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest

# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases  # noqa: F401
from .generated.infrastructure import repository as _gen_repository  # noqa: F401


from .schemas import (
    ReportJobOut, ReportJobListOut, CreateReportJobIn, UpdateReportJobIn, ErrorOut,

)
from .domain.rules import RoleLabel, InsufficientPrivilege, ReportJobNotFound, ReportJobConflict
from .infrastructure.repository import ReportJobRepository
from .application.use_cases import (
    ListReportJobs, CreateReportJob, GetReportJob, UpdateReportJob, DownloadReportArtifact,
)

router = Router()
_repo = ReportJobRepository()
_list_uc = ListReportJobs(_repo)
_create_uc = CreateReportJob(_repo)
_get_uc = GetReportJob(_repo)
_update_uc = UpdateReportJob(_repo)
_download_uc = DownloadReportArtifact(_repo)

def _role(request: HttpRequest) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")

def _uid(request: HttpRequest) -> UUID:
    """Extrai actor_id do JWT validado."""
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")

@router.get("/jobs", response={200: ReportJobListOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})
def list_report_jobs(
    request: HttpRequest,
    reportType: Optional[str] = None,
    formatLabel: Optional[str] = None,
    statusLabel: Optional[str] = None,
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    ownerUserId: Optional[UUID] = None,
    pageSize: int = 20,
    pageToken: Optional[str] = None,
):
    try:
        role = _role(request)
        requester_id = _uid(request)
        jobs, next_token = _list_uc.execute(
            role=role, requester_id=requester_id,
            report_type=reportType, format_label=formatLabel,
            status_label=statusLabel, date_from=dateFrom, date_to=dateTo,
            owner_user_id=ownerUserId, page_size=pageSize, page_token=pageToken,
        )
        return 200, ReportJobListOut(
            data=[ReportJobOut.from_domain(j) for j in jobs],
            nextPageToken=next_token,
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))

@router.post("/jobs", response={201: ReportJobOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})
def create_report_job(request: HttpRequest, payload: CreateReportJobIn):
    try:
        role = _role(request)
        requester_id = _uid(request)
        job = _create_uc.execute(
            role=role, requester_id=requester_id,
            report_type=payload.reportType,
            format_label=payload.formatLabel,
            parameter_summary=payload.parameterSummary,
            source_metric_names=payload.sourceMetricNames,
            retention_label=payload.retentionLabel,
        )
        return 201, ReportJobOut.from_domain(job)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))

@router.get("/jobs/{job_id}", response={200: ReportJobOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut})
def get_report_job(request: HttpRequest, job_id: UUID):
    try:
        role = _role(request)
        requester_id = _uid(request)
        job = _get_uc.execute(role=role, requester_id=requester_id, job_id=job_id)
        return 200, ReportJobOut.from_domain(job)
    except ReportJobNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))

@router.patch("/jobs/{job_id}", response={200: ReportJobOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut, 422: ErrorOut})
def update_report_job(request: HttpRequest, job_id: UUID, payload: UpdateReportJobIn):
    try:
        role = _role(request)
        requester_id = _uid(request)
        job = _update_uc.execute(
            role=role, requester_id=requester_id, job_id=job_id,
            status_label=payload.statusLabel,
            retention_label=payload.retentionLabel,
        )
        return 200, ReportJobOut.from_domain(job)
    except ReportJobNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except ReportJobConflict as e:
        return 409, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 422, ErrorOut(detail=str(e))

@router.get("/jobs/{job_id}/download", response={200: ReportJobOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut})
def download_report_artifact(request: HttpRequest, job_id: UUID):
    try:
        role = _role(request)
        requester_id = _uid(request)
        job = _download_uc.execute(role=role, requester_id=requester_id, job_id=job_id)
        return 200, ReportJobOut.from_domain(job)
    except ReportJobNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except ReportJobConflict as e:
        return 409, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
