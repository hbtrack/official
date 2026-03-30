from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest

from audit.application.use_cases import (
    ListAuditEntries,
    CreateAuditEntry,
    GetAuditEntry,
    ExportAuditEntries,
)
from audit.infrastructure.repository import AuditEntryRepository
from audit.domain.rules import (
    InsufficientPrivilege,
    AuditEntryNotFound,
)
from audit.schemas import (
    AuditEntryOut,
    AuditEntryListOut,
    CreateAuditEntryIn,
    ExportOut,
    ErrorOut,
)

router = Router(tags=["audit"])


def _get_role(request: HttpRequest) -> str:
    """Extrai role do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        return role
    raise HttpError(401, "Unauthenticated")


@router.get("/entries", response={200: AuditEntryListOut, 400: ErrorOut, 403: ErrorOut})
def list_audit_entries(
    request: HttpRequest,
    actorUserId: Optional[UUID] = None,
    targetResourceId: Optional[UUID] = None,
    targetResourceType: Optional[str] = None,
    action: Optional[str] = None,
    teamId: Optional[UUID] = None,
    organizationId: Optional[UUID] = None,
    occurredAfter: Optional[datetime] = None,
    occurredBefore: Optional[datetime] = None,
    correlationId: Optional[UUID] = None,
    pageToken: Optional[str] = None,
    pageSize: int = 50,
):
    role = _get_role(request)
    repo = AuditEntryRepository()
    try:
        result = ListAuditEntries(repo).execute(
            role=role,
            actor_user_id=str(actorUserId) if actorUserId else None,
            target_resource_id=str(targetResourceId) if targetResourceId else None,
            target_resource_type=targetResourceType,
            action=action,
            team_id=str(teamId) if teamId else None,
            organization_id=str(organizationId) if organizationId else None,
            occurred_after=occurredAfter,
            occurred_before=occurredBefore,
            correlation_id=str(correlationId) if correlationId else None,
            page_token=pageToken,
            page_size=pageSize,
        )
        return 200, AuditEntryListOut(
            items=[AuditEntryOut.from_domain(e) for e in result["items"]],
            nextPageToken=result["nextPageToken"],
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 400, ErrorOut(detail=str(e))


@router.post("/entries", response={201: AuditEntryOut, 400: ErrorOut, 403: ErrorOut})
def create_audit_entry(request: HttpRequest, payload: CreateAuditEntryIn):
    role = _get_role(request)
    repo = AuditEntryRepository()
    try:
        entry = CreateAuditEntry(repo).execute(
            role=role,
            actor_user_id=payload.actorUserId,
            action=payload.action,
            occurred_at=payload.occurredAt,
            target_resource_id=payload.targetResourceId,
            target_resource_type=payload.targetResourceType,
            outcome_label=payload.outcomeLabel,
            origin_label=payload.originLabel,
            correlation_id=payload.correlationId,
            before_summary=payload.beforeSummary,
            after_summary=payload.afterSummary,
        )
        return 201, AuditEntryOut.from_domain(entry)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 400, ErrorOut(detail=str(e))


@router.get("/entries/export", response={200: ExportOut, 400: ErrorOut, 403: ErrorOut})
def export_audit_entries(
    request: HttpRequest,
    occurredAfter: datetime,
    occurredBefore: datetime,
    teamId: Optional[UUID] = None,
    organizationId: Optional[UUID] = None,
    format: str = "json",
):
    role = _get_role(request)
    repo = AuditEntryRepository()
    try:
        result = ExportAuditEntries(repo).execute(
            role=role,
            occurred_after=occurredAfter,
            occurred_before=occurredBefore,
            team_id=str(teamId) if teamId else None,
            organization_id=str(organizationId) if organizationId else None,
            format=format,
        )
        return 200, ExportOut(
            entries=[AuditEntryOut.from_domain(e) for e in result["entries"]],
            exportedCount=result["exportedCount"],
            exportedAt=result["exportedAt"],
            truncated=result["truncated"],
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 400, ErrorOut(detail=str(e))


@router.get("/entries/{entry_id}", response={200: AuditEntryOut, 403: ErrorOut, 404: ErrorOut})
def get_audit_entry(request: HttpRequest, entry_id: UUID):
    role = _get_role(request)
    repo = AuditEntryRepository()
    try:
        entry = GetAuditEntry(repo).execute(role=role, entry_id=entry_id)
        return 200, AuditEntryOut.from_domain(entry)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except AuditEntryNotFound as e:
        return 404, ErrorOut(detail=str(e))
