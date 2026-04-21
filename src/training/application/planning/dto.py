from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...domain.rules import RoleLabel


@dataclass
class CreateMesocycleInput:
    actor_role: RoleLabel
    organization_id: uuid.UUID
    name: str
    started_at: datetime
    ended_at: datetime
    season_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    objective: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class CreateMicrocycleInput:
    actor_role: RoleLabel
    organization_id: uuid.UUID
    mesocycle_id: uuid.UUID
    week_number: int
    started_at: datetime
    ended_at: datetime
    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class ListMesocyclesInput:
    organization_id: Optional[uuid.UUID] = None


@dataclass
class GetMesocycleInput:
    id: uuid.UUID


@dataclass
class UpdateMesocycleInput:
    id: uuid.UUID
    actor_role: RoleLabel
    name: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    season_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    objective: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ListMicrocyclesInput:
    organization_id: Optional[uuid.UUID] = None
    mesocycle_id: Optional[uuid.UUID] = None


@dataclass
class GetMicrocycleInput:
    id: uuid.UUID


@dataclass
class UpdateMicrocycleInput:
    id: uuid.UUID
    actor_role: RoleLabel
    week_number: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[int] = None
    notes: Optional[str] = None
