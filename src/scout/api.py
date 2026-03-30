from __future__ import annotations
from typing import Optional
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest

from scout.application.use_cases import (
    CreateScoutEvent, ListScoutEvents, GetScoutEvent,
    GetScoutAggregations, CompleteScoutSession,
)
from scout.domain.rules import (
    RoleLabel, InsufficientPrivilege, ScoutEventNotFound,
)
from scout.infrastructure.repository import ScoutEventRepository
from scout.schemas import (
    ScoutEventOut, ScoutEventListOut, CreateScoutEventIn,
    ScoutAggregationsOut, CompleteSessionIn, CompleteSessionOut, ErrorOut,
)

router = Router()
_repo = ScoutEventRepository()


def _get_role(request: HttpRequest) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")


def _get_actor_id(request: HttpRequest) -> UUID:
    """Extrai actor_id do JWT validado."""
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")


def _get_team_ids(request: HttpRequest):
    return getattr(request, "actor_team_ids", []) or []


@router.get("/events", response={200: ScoutEventListOut, 401: ErrorOut, 403: ErrorOut, 400: ErrorOut})
def list_scout_events(
    request: HttpRequest,
    matchId: Optional[UUID] = None,
    athleteUserId: Optional[UUID] = None,
    teamId: Optional[UUID] = None,
    eventLabel: Optional[str] = None,
    page: int = 1,
    pageSize: int = 50,
):
    role = _get_role(request)
    actor_id = _get_actor_id(request)
    uc = ListScoutEvents(_repo)
    try:
        items, total = uc.execute(
            actor_role=role,
            actor_id=actor_id,
            team_id=teamId,
            match_id=matchId,
            athlete_user_id=athleteUserId,
            event_label=eventLabel,
            page=page,
            page_size=pageSize,
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    out_items = [ScoutEventOut.from_domain(ev) for ev in items]
    return 200, ScoutEventListOut(items=out_items, totalCount=total)


@router.post("/events", response={201: ScoutEventOut, 401: ErrorOut, 403: ErrorOut, 400: ErrorOut})
def create_scout_event(request: HttpRequest, payload: CreateScoutEventIn):
    role = _get_role(request)
    uc = CreateScoutEvent(_repo)
    try:
        event = uc.execute(
            actor_role=role,
            match_id=payload.matchId,
            event_label=payload.eventLabel,
            recorded_at=payload.recordedAt,
            athlete_user_id=payload.athleteUserId,
            team_id=payload.teamId,
            tag_labels=payload.tagLabels,
            clip_asset_refs=payload.clipAssetRefs,
            coding_schema_label=payload.codingSchemaLabel,
            tactical_aggregation_label=payload.tacticalAggregationLabel,
            session_id=payload.sessionId,
            position_x=payload.positionX,
            position_y=payload.positionY,
            duration_ms=payload.durationMs,
            notes=payload.notes,
            metadata=payload.metadata,
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    except ValueError as e:
        return 400, ErrorOut(detail=str(e))
    return 201, ScoutEventOut.from_domain(event)


@router.get("/events/aggregations", response={200: ScoutAggregationsOut, 401: ErrorOut, 403: ErrorOut, 400: ErrorOut})
def get_scout_aggregations(
    request: HttpRequest,
    matchId: UUID,
    teamId: Optional[UUID] = None,
):
    role = _get_role(request)
    uc = GetScoutAggregations(_repo)
    try:
        result = uc.execute(match_id=matchId, actor_role=role, team_id=teamId)
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 200, ScoutAggregationsOut(
        matchId=result["matchId"],
        totalEvents=result["totalEvents"],
        eventLabelDistribution=result["eventLabelDistribution"],
        athleteBreakdown=result.get("athleteBreakdown", []),
    )


@router.get("/events/{event_id}", response={200: ScoutEventOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut})
def get_scout_event(request: HttpRequest, event_id: UUID):
    role = _get_role(request)
    actor_id = _get_actor_id(request)
    actor_team_ids = _get_team_ids(request)
    uc = GetScoutEvent(_repo)
    try:
        event = uc.execute(
            event_id=event_id,
            actor_role=role,
            actor_id=actor_id,
            actor_team_ids=actor_team_ids,
        )
    except ScoutEventNotFound as e:
        return 404, ErrorOut(detail=str(e))
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 200, ScoutEventOut.from_domain(event)


@router.post("/sessions/{match_id}/complete", response={200: CompleteSessionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut})
def complete_scout_session(
    request: HttpRequest,
    match_id: UUID,
    payload: Optional[CompleteSessionIn] = None,
):
    role = _get_role(request)
    uc = CompleteScoutSession(_repo)
    try:
        result = uc.execute(
            match_id=match_id,
            actor_role=role,
            notes=payload.notes if payload else None,
        )
    except InsufficientPrivilege as e:
        return 403, ErrorOut(detail=str(e))
    return 200, CompleteSessionOut(
        matchId=result["matchId"],
        completedAt=result["completedAt"],
        totalEvents=result["totalEvents"],
    )
