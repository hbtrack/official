from __future__ import annotations
from typing import Optional, List
from uuid import UUID
from django.db.models import Count

from scout.domain.entities import ScoutEvent
from scout.infrastructure.models import ScoutEventModel


def _to_domain(m: ScoutEventModel) -> ScoutEvent:
    return ScoutEvent(
        id=m.id,
        match_id=m.match_id,
        event_label=m.event_label,
        recorded_at=m.recorded_at,
        athlete_user_id=m.athlete_user_id,
        team_id=m.team_id,
        tag_labels=list(m.tag_labels or []),
        clip_asset_refs=list(m.clip_asset_refs or []),
        coding_schema_label=m.coding_schema_label,
        tactical_aggregation_label=m.tactical_aggregation_label,
        session_id=m.session_id,
        position_x=m.position_x,
        position_y=m.position_y,
        duration_ms=m.duration_ms,
        notes=m.notes,
        metadata=m.metadata,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class ScoutEventRepository:
    def save(self, event: ScoutEvent) -> ScoutEvent:
        obj, _ = ScoutEventModel.objects.update_or_create(
            id=event.id,
            defaults={
                "match_id": event.match_id,
                "event_label": event.event_label,
                "recorded_at": event.recorded_at,
                "athlete_user_id": event.athlete_user_id,
                "team_id": event.team_id,
                "tag_labels": event.tag_labels,
                "clip_asset_refs": event.clip_asset_refs,
                "coding_schema_label": event.coding_schema_label,
                "tactical_aggregation_label": event.tactical_aggregation_label,
                "session_id": event.session_id,
                "position_x": event.position_x,
                "position_y": event.position_y,
                "duration_ms": event.duration_ms,
                "notes": event.notes,
                "metadata": event.metadata,
            },
        )
        return _to_domain(obj)

    def get_by_id(self, event_id: UUID) -> Optional[ScoutEvent]:
        try:
            return _to_domain(ScoutEventModel.objects.get(id=event_id))
        except ScoutEventModel.DoesNotExist:
            return None

    def list_events(
        self,
        match_id: Optional[UUID] = None,
        athlete_user_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        event_label: Optional[str] = None,
        session_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        qs = ScoutEventModel.objects.all()
        if match_id:
            qs = qs.filter(match_id=match_id)
        if athlete_user_id:
            qs = qs.filter(athlete_user_id=athlete_user_id)
        if team_id:
            qs = qs.filter(team_id=team_id)
        if event_label:
            qs = qs.filter(event_label=event_label)
        if session_id:
            qs = qs.filter(session_id=session_id)
        total = qs.count()
        offset = (page - 1) * page_size
        items = [_to_domain(m) for m in qs[offset: offset + page_size]]
        return items, total

    def compute_aggregations(self, match_id: UUID, team_id: Optional[UUID] = None):
        qs = ScoutEventModel.objects.filter(match_id=match_id)
        if team_id:
            qs = qs.filter(team_id=team_id)
        total = qs.count()
        label_dist = list(
            qs.values("event_label").annotate(count=Count("id")).order_by("-count")
        )
        athlete_breakdown = list(
            qs.exclude(athlete_user_id=None)
            .values("athlete_user_id")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return total, label_dist, athlete_breakdown

    def count_events_for_match(self, match_id: UUID) -> int:
        return ScoutEventModel.objects.filter(match_id=match_id).count()
