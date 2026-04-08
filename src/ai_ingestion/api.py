from __future__ import annotations
from typing import Optional
from uuid import UUID
from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest

# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases  # noqa: F401
from .generated.infrastructure import repository as _gen_repository  # noqa: F401


from ai_ingestion.application.use_cases import (
    ListIngestionJobs,
    CreateIngestionJob,
    GetIngestionJob,
    RetryIngestionJob,

)
from ai_ingestion.infrastructure.repository import IngestionJobRepository
from ai_ingestion.domain.rules import (
    InsufficientPrivilege,
    IngestionJobNotFound,
    IngestionJobConflict,
)
from ai_ingestion.schemas import (
    IngestionJobOut,
    IngestionJobListOut,
    CreateIngestionJobIn,
    ErrorOut,
)

router = Router(tags=["ai_ingestion"])

def _get_role(request: HttpRequest) -> str:
    """Extrai role do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        return role
    raise HttpError(401, "Unauthenticated")

@router.get("/jobs", response={200: IngestionJobListOut, 401: ErrorOut, 403: ErrorOut})
def list_ingestion_jobs(
    request: HttpRequest,
    page: int = 1,
    pageSize: int = 20,
    statusLabel: Optional[str] = None,
    sourceLabel: Optional[str] = None,
):
    role = _get_role(request)
    repo = IngestionJobRepository()
    try:
        result = ListIngestionJobs(repo).execute(
            role=role,
            page=page,
            page_size=pageSize,
            status_label=statusLabel,
            source_label=sourceLabel,
        )
        return 200, IngestionJobListOut(
            data=[IngestionJobOut.from_domain(j) for j in result["data"]],
            page=result["page"],
            pageSize=result["pageSize"],
            total=result["total"],
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))

@router.post("/jobs", response={202: IngestionJobOut, 401: ErrorOut, 403: ErrorOut, 409: IngestionJobOut})
def create_ingestion_job(request: HttpRequest, payload: CreateIngestionJobIn):
    role = _get_role(request)
    repo = IngestionJobRepository()
    try:
        job, is_duplicate = CreateIngestionJob(repo).execute(
            role=role,
            source_label=payload.sourceLabel,
            ingestion_mode=payload.ingestionMode,
            payload_schema_ref=payload.payloadSchemaRef,
            mapping_profile=payload.mappingProfile,
            idempotency_key=payload.idempotencyKey,
            execution_binding_label=payload.executionBindingLabel,
        )
        status_code = 409 if is_duplicate else 202
        return status_code, IngestionJobOut.from_domain(job)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))

@router.get("/jobs/{job_id}", response={200: IngestionJobOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut})
def get_ingestion_job(request: HttpRequest, job_id: UUID):
    role = _get_role(request)
    repo = IngestionJobRepository()
    try:
        job = GetIngestionJob(repo).execute(role=role, job_id=job_id)
        return 200, IngestionJobOut.from_domain(job)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except IngestionJobNotFound as e:
        return 404, ErrorOut(detail=str(e))

@router.post(
    "/jobs/{job_id}/retry",
    response={202: IngestionJobOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def retry_ingestion_job(request: HttpRequest, job_id: UUID):
    role = _get_role(request)
    repo = IngestionJobRepository()
    try:
        new_job = RetryIngestionJob(repo).execute(role=role, job_id=job_id)
        return 202, IngestionJobOut.from_domain(new_job)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except IngestionJobNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except IngestionJobConflict as e:
        return 409, ErrorOut(detail=str(e))
