from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from scout.domain.entities import ScoutEvent
from scout.domain.rules import (
    RoleLabel, InsufficientPrivilege,
    assert_can_create_event, assert_can_read_event,
    assert_can_list_events, assert_can_complete_session,
    assert_can_get_aggregations,
)
from scout.infrastructure.repository import ScoutEventRepository


class CreateScoutEvent:
    def __init__(self, repo: ScoutEventRepository):
        self._repo = repo

    def execute(
        self,
        actor_role: RoleLabel,
        match_id: UUID,
        event_label: str,
        recorded_at: datetime,
        athlete_user_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        tag_labels: Optional[List[str]] = None,
        clip_asset_refs: Optional[List[str]] = None,
        coding_schema_label: Optional[str] = None,
        tactical_aggregation_label: Optional[str] = None,
        session_id: Optional[UUID] = None,
        position_x: Optional[float] = None,
        position_y: Optional[float] = None,
        duration_ms: Optional[int] = None,
        notes: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ScoutEvent:
        assert_can_create_event(actor_role)
        event = ScoutEvent(
            id=uuid4(),
            match_id=match_id,
            event_label=event_label,
            recorded_at=recorded_at,
            athlete_user_id=athlete_user_id,
            team_id=team_id,
            tag_labels=list(tag_labels or []),
            clip_asset_refs=list(clip_asset_refs or []),
            coding_schema_label=coding_schema_label,
            tactical_aggregation_label=tactical_aggregation_label,
            session_id=session_id,
            position_x=position_x,
            position_y=position_y,
            duration_ms=duration_ms,
            notes=notes,
            metadata=metadata,
        )
        event.validate_invariants()
        return self._repo.save(event)


class ListScoutEvents:
    def __init__(self, repo: ScoutEventRepository):
        self._repo = repo

    def execute(
        self,
        actor_role: RoleLabel,
        actor_id: UUID,
        team_id: Optional[UUID] = None,
        match_id: Optional[UUID] = None,
        athlete_user_id: Optional[UUID] = None,
        event_label: Optional[str] = None,
        session_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        assert_can_list_events(actor_role, team_id)
        # Athlete ve apenas seus proprios eventos
        if actor_role == RoleLabel.ATHLETE:
            athlete_user_id = actor_id
        # coordinator/coach filtra por time obrigatoriamente
        effective_team_id = team_id
        items, total = self._repo.list_events(
            match_id=match_id,
            athlete_user_id=athlete_user_id,
            team_id=effective_team_id,
            event_label=event_label,
            session_id=session_id,
            page=page,
            page_size=page_size,
        )
        return items, total


class GetScoutEvent:
    def __init__(self, repo: ScoutEventRepository):
        self._repo = repo

    def execute(
        self,
        event_id: UUID,
        actor_role: RoleLabel,
        actor_id: UUID,
        actor_team_ids: Optional[List[UUID]] = None,
    ) -> ScoutEvent:
        event = self._repo.get_by_id(event_id)
        if event is None:
            from scout.domain.rules import ScoutEventNotFound
            raise ScoutEventNotFound(f"Evento scout {event_id} nao encontrado")
        assert_can_read_event(
            role=actor_role,
            actor_id=actor_id,
            event_athlete_user_id=event.athlete_user_id,
            event_team_id=event.team_id,
            actor_team_ids=actor_team_ids,
        )
        return event


class GetScoutAggregations:
    def __init__(self, repo: ScoutEventRepository):
        self._repo = repo

    def execute(
        self,
        match_id: UUID,
        actor_role: RoleLabel,
        team_id: Optional[UUID] = None,
    ) -> dict:
        assert_can_get_aggregations(actor_role, team_id)
        total, label_dist, athlete_breakdown = self._repo.compute_aggregations(
            match_id=match_id, team_id=team_id
        )
        return {
            "matchId": str(match_id),
            "totalEvents": total,
            "eventLabelDistribution": [
                {"eventLabel": r["event_label"], "count": r["count"]}
                for r in label_dist
            ],
            "athleteBreakdown": [
                {"athleteUserId": str(r["athlete_user_id"]), "count": r["count"]}
                for r in athlete_breakdown
            ],
        }


class CompleteScoutSession:
    def __init__(self, repo: ScoutEventRepository):
        self._repo = repo

    def execute(
        self,
        match_id: UUID,
        actor_role: RoleLabel,
        notes: Optional[str] = None,
    ) -> dict:
        assert_can_complete_session(actor_role)
        total_events = self._repo.count_events_for_match(match_id)
        completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return {
            "matchId": str(match_id),
            "completedAt": completed_at,
            "totalEvents": total_events,
        }
