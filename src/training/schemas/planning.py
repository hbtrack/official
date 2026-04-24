from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, List, Optional

from ninja import Schema
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

_CAMEL = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# SmallIntegerField range; domain rule: >= 1
_WeekNumber = Annotated[int, Field(ge=1, le=32767)]
# SmallIntegerField range for planned_sessions_count (nullable)
_PlannedCount = Annotated[int, Field(ge=0, le=32767)]


# ---------------------------------------------------------------------------
# Mesocycle schemas
# ---------------------------------------------------------------------------

class MesocycleOut(Schema):
    model_config = _CAMEL
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    started_at: datetime
    ended_at: datetime
    created_at: datetime
    updated_at: datetime
    season_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    objective: Optional[str] = None
    notes: Optional[str] = None


class MesocycleListOut(Schema):
    model_config = _CAMEL
    items: List[MesocycleOut]


class CreateMesocycleIn(Schema):
    model_config = _CAMEL
    organization_id: uuid.UUID
    name: str
    started_at: datetime
    ended_at: datetime
    season_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    objective: Optional[str] = None
    notes: Optional[str] = None


class UpdateMesocycleIn(Schema):
    model_config = _CAMEL
    name: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    season_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    objective: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Microcycle schemas
# ---------------------------------------------------------------------------

class MicrocycleOut(Schema):
    model_config = _CAMEL
    id: uuid.UUID
    organization_id: uuid.UUID
    mesocycle_id: uuid.UUID
    week_number: _WeekNumber
    started_at: datetime
    ended_at: datetime
    created_at: datetime
    updated_at: datetime
    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[_PlannedCount] = None
    notes: Optional[str] = None


class MicrocycleListOut(Schema):
    model_config = _CAMEL
    items: List[MicrocycleOut]


class CreateMicrocycleIn(Schema):
    model_config = _CAMEL
    organization_id: uuid.UUID
    mesocycle_id: uuid.UUID
    week_number: _WeekNumber
    started_at: datetime
    ended_at: datetime
    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[_PlannedCount] = None
    notes: Optional[str] = None


class UpdateMicrocycleIn(Schema):
    model_config = _CAMEL
    week_number: Optional[_WeekNumber] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[_PlannedCount] = None
    notes: Optional[str] = None
