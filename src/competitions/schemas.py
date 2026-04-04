"""
Schemas I/O — módulo competitions (Django Ninja).
Fonte: contracts/openapi/paths/competitions.yaml
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

from ninja import Schema


class CompetitionOut(Schema):
    competitionId: uuid.UUID
    seasonId: uuid.UUID
    organizationId: Optional[uuid.UUID] = None
    name: str
    startDate: date
    endDate: Optional[date] = None
    formatLabel: Optional[str] = None
    statusLabel: str
    stageLabels: List[str] = []
    calendarEntryIds: List[uuid.UUID] = []
    registrationTeamIds: List[uuid.UUID] = []
    standingsSummary: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_domain(cls, comp) -> "CompetitionOut":
        return cls(
            competitionId=comp.id,
            seasonId=comp.season_id,
            organizationId=comp.organization_id,
            name=comp.name,
            startDate=comp.start_date,
            endDate=comp.end_date,
            formatLabel=comp.format_label,
            statusLabel=comp.status_label.value,
            stageLabels=comp.stage_labels,
            calendarEntryIds=comp.calendar_entry_ids,
            registrationTeamIds=comp.registration_team_ids,
            standingsSummary=comp.standings_summary,
            createdAt=comp.created_at,
            updatedAt=comp.updated_at,
        )


class CompetitionListOut(Schema):
    data: List[CompetitionOut]
    page: int
    pageSize: int
    total: int


class CreateCompetitionIn(Schema):
    seasonId: uuid.UUID
    name: str
    startDate: date
    organizationId: Optional[uuid.UUID] = None
    endDate: Optional[date] = None
    formatLabel: Optional[str] = None
    stageLabels: List[str] = []
    calendarEntryIds: List[uuid.UUID] = []
    registrationTeamIds: List[uuid.UUID] = []


class PatchCompetitionIn(Schema):
    name: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    formatLabel: Optional[str] = None
    statusLabel: Optional[str] = None
    stageLabels: Optional[List[str]] = None
    standingsSummary: Optional[str] = None


class ErrorOut(Schema):
    detail: str
