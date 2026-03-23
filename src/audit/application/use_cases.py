from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from ..domain.entities import AuditEntry
from ..domain.rules import (
    RoleLabel, InsufficientPrivilege, AuditEntryNotFound,
    assert_can_list_entries, assert_can_create_entry,
    assert_can_get_entry, assert_can_export_entries,
)
from ..infrastructure.repository import AuditEntryRepository


class ListAuditEntries:
    def __init__(self, repo: AuditEntryRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        actor_user_id: Optional[str] = None,
        target_resource_id: Optional[str] = None,
        target_resource_type: Optional[str] = None,
        action: Optional[str] = None,
        team_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        occurred_after: Optional[datetime] = None,
        occurred_before: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: int = 50,
    ) -> dict:
        assert_can_list_entries(role, team_id=team_id, organization_id=organization_id)
        items, next_token = self.repo.list_entries(
            actor_user_id=actor_user_id,
            target_resource_id=target_resource_id,
            target_resource_type=target_resource_type,
            action=action,
            team_id=team_id,
            organization_id=organization_id,
            occurred_after=occurred_after,
            occurred_before=occurred_before,
            correlation_id=correlation_id,
            page_token=page_token,
            page_size=page_size,
        )
        return {"items": items, "nextPageToken": next_token}


class CreateAuditEntry:
    def __init__(self, repo: AuditEntryRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        actor_user_id: UUID,
        action: str,
        occurred_at: datetime,
        target_resource_id: Optional[UUID] = None,
        target_resource_type: Optional[str] = None,
        outcome_label: Optional[str] = None,
        origin_label: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
        before_summary: Optional[str] = None,
        after_summary: Optional[str] = None,
    ) -> AuditEntry:
        assert_can_create_entry(role)
        entry = AuditEntry(
            id=uuid.uuid4(),
            actor_user_id=actor_user_id,
            action=action,
            occurred_at=occurred_at,
            target_resource_id=target_resource_id,
            target_resource_type=target_resource_type,
            outcome_label=outcome_label,
            origin_label=origin_label,
            correlation_id=correlation_id,
            before_summary=before_summary,
            after_summary=after_summary,
        )
        entry.validate_invariants()
        return self.repo.save(entry)


class GetAuditEntry:
    def __init__(self, repo: AuditEntryRepository):
        self.repo = repo

    def execute(self, role: RoleLabel, entry_id: UUID) -> AuditEntry:
        assert_can_get_entry(role)
        entry = self.repo.get_by_id(entry_id)
        if entry is None:
            raise AuditEntryNotFound(f"AuditEntry {entry_id} not found")
        return entry


class ExportAuditEntries:
    def __init__(self, repo: AuditEntryRepository):
        self.repo = repo

    def execute(
        self, role: RoleLabel,
        occurred_after: datetime,
        occurred_before: datetime,
        team_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        format: str = "json",
    ) -> dict:
        assert_can_export_entries(role, team_id=team_id, organization_id=organization_id)
        entries, truncated = self.repo.export_entries(
            occurred_after=occurred_after,
            occurred_before=occurred_before,
            team_id=team_id,
            organization_id=organization_id,
        )
        exported_at = datetime.now(timezone.utc)
        return {
            "entries": entries,
            "exportedCount": len(entries),
            "exportedAt": exported_at,
            "truncated": truncated,
        }
