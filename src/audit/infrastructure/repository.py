from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from ..domain.entities import AuditEntry
from .models import AuditEntryModel


def _entry_from_model(m: AuditEntryModel) -> AuditEntry:
    return AuditEntry(
        id=m.id,
        actor_user_id=m.actor_user_id,
        action=m.action,
        occurred_at=m.occurred_at,
        target_resource_id=m.target_resource_id,
        target_resource_type=m.target_resource_type,
        outcome_label=m.outcome_label,
        origin_label=m.origin_label,
        correlation_id=m.correlation_id,
        before_summary=m.before_summary,
        after_summary=m.after_summary,
    )


class AuditEntryRepository:
    def save(self, entry: AuditEntry) -> AuditEntry:
        obj = AuditEntryModel(
            id=entry.id,
            actor_user_id=entry.actor_user_id,
            action=entry.action,
            occurred_at=entry.occurred_at,
            target_resource_id=entry.target_resource_id,
            target_resource_type=entry.target_resource_type,
            outcome_label=entry.outcome_label,
            origin_label=entry.origin_label,
            correlation_id=entry.correlation_id,
            before_summary=entry.before_summary,
            after_summary=entry.after_summary,
        )
        obj.save()
        return _entry_from_model(obj)

    def get_by_id(self, entry_id: UUID) -> Optional[AuditEntry]:
        try:
            return _entry_from_model(AuditEntryModel.objects.get(id=entry_id))
        except AuditEntryModel.DoesNotExist:
            return None

    def list_entries(
        self,
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
    ) -> Tuple[List[AuditEntry], Optional[str]]:
        qs = AuditEntryModel.objects.all()
        if actor_user_id:
            qs = qs.filter(actor_user_id=actor_user_id)
        if target_resource_id:
            qs = qs.filter(target_resource_id=target_resource_id)
        if target_resource_type:
            qs = qs.filter(target_resource_type=target_resource_type)
        if action:
            qs = qs.filter(action=action)
        if occurred_after:
            qs = qs.filter(occurred_at__gte=occurred_after)
        if occurred_before:
            qs = qs.filter(occurred_at__lte=occurred_before)
        if correlation_id:
            qs = qs.filter(correlation_id=correlation_id)
        # cursor-based pagination via occurred_at cursor
        if page_token:
            qs = qs.filter(occurred_at__lt=page_token)
        items = list(qs[:page_size + 1])
        next_token = None
        if len(items) > page_size:
            items = items[:page_size]
            next_token = items[-1].occurred_at.isoformat()
        return [_entry_from_model(m) for m in items], next_token

    def export_entries(
        self,
        occurred_after: datetime,
        occurred_before: datetime,
        team_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = 10000,
    ) -> Tuple[List[AuditEntry], bool]:
        qs = AuditEntryModel.objects.filter(
            occurred_at__gte=occurred_after,
            occurred_at__lte=occurred_before,
        )
        items = list(qs[:limit + 1])
        truncated = len(items) > limit
        if truncated:
            items = items[:limit]
        return [_entry_from_model(m) for m in items], truncated
