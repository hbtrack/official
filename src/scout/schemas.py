from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from ninja import Schema

from scout.domain.entities import ScoutEvent


class ScoutEventOut(Schema):
    id: UUID
    matchId: UUID
    eventLabel: str
    recordedAt: datetime
    athleteUserId: Optional[UUID] = None
    teamId: Optional[UUID] = None
    tagLabels: List[str] = []
    clipAssetRefs: List[str] = []
    codingSchemaLabel: Optional[str] = None
    tacticalAggregationLabel: Optional[str] = None
    sessionId: Optional[UUID] = None
    positionX: Optional[float] = None
    positionY: Optional[float] = None
    durationMs: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    @classmethod
    def from_domain(cls, e: ScoutEvent) -> "ScoutEventOut":
        return cls(
            id=e.id,
            matchId=e.match_id,
            eventLabel=e.event_label,
            recordedAt=e.recorded_at,
            athleteUserId=e.athlete_user_id,
            teamId=e.team_id,
            tagLabels=e.tag_labels or [],
            clipAssetRefs=e.clip_asset_refs or [],
            codingSchemaLabel=e.coding_schema_label,
            tacticalAggregationLabel=e.tactical_aggregation_label,
            sessionId=e.session_id,
            positionX=e.position_x,
            positionY=e.position_y,
            durationMs=e.duration_ms,
            notes=e.notes,
            metadata=e.metadata,
            createdAt=e.created_at,
            updatedAt=e.updated_at,
        )


class ScoutEventListOut(Schema):
    items: List[ScoutEventOut]
    nextPageToken: Optional[str] = None
    totalCount: int


class CreateScoutEventIn(Schema):
    matchId: UUID
    eventLabel: str
    recordedAt: datetime
    athleteUserId: Optional[UUID] = None
    teamId: Optional[UUID] = None
    tagLabels: Optional[List[str]] = None
    clipAssetRefs: Optional[List[str]] = None
    codingSchemaLabel: Optional[str] = None
    tacticalAggregationLabel: Optional[str] = None
    sessionId: Optional[UUID] = None
    positionX: Optional[float] = None
    positionY: Optional[float] = None
    durationMs: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class ScoutAggregationsOut(Schema):
    matchId: UUID
    totalEvents: int
    eventLabelDistribution: List[dict]
    athleteBreakdown: Optional[List[dict]] = []


class CompleteSessionIn(Schema):
    notes: Optional[str] = None


class CompleteSessionOut(Schema):
    matchId: UUID
    completedAt: str
    totalEvents: int


class ErrorOut(Schema):
    detail: str
