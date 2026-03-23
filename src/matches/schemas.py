from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema

from matches.domain.entities import Match


class MatchOut(Schema):
    id: uuid.UUID
    competitionId: uuid.UUID
    homeTeamId: uuid.UUID
    awayTeamId: uuid.UUID
    statusLabel: str
    venueLabel: Optional[str] = None
    scheduledAt: datetime
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    homeScore: Optional[int] = None
    awayScore: Optional[int] = None
    refereeNames: List[str]
    lineupUserIds: List[uuid.UUID]
    officialIncidentIds: List[uuid.UUID]
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_domain(cls, m: Match) -> "MatchOut":
        return cls(
            id=m.id,
            competitionId=m.competition_id,
            homeTeamId=m.home_team_id,
            awayTeamId=m.away_team_id,
            statusLabel=m.status_label,
            venueLabel=m.venue_label,
            scheduledAt=m.scheduled_at,
            startedAt=m.started_at,
            endedAt=m.ended_at,
            homeScore=m.home_score,
            awayScore=m.away_score,
            refereeNames=m.referee_names,
            lineupUserIds=m.lineup_user_ids,
            officialIncidentIds=m.official_incident_ids,
            createdAt=m.created_at,
            updatedAt=m.updated_at,
        )


class MatchListOut(Schema):
    data: List[MatchOut]
    page: int
    pageSize: int
    total: int


class CreateMatchIn(Schema):
    competitionId: uuid.UUID
    homeTeamId: uuid.UUID
    awayTeamId: uuid.UUID
    scheduledAt: datetime
    venueLabel: Optional[str] = None
    refereeNames: List[str] = []


class PatchMatchIn(Schema):
    venueLabel: Optional[str] = None
    statusLabel: Optional[str] = None
    scheduledAt: Optional[datetime] = None
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    homeScore: Optional[int] = None
    awayScore: Optional[int] = None
    refereeNames: Optional[List[str]] = None
    officialIncidentIds: Optional[List[uuid.UUID]] = None


class ErrorOut(Schema):
    detail: str
