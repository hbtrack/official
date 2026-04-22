from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ...domain.rules import RoleLabel


@dataclass
class CreateExecutionRecordInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    execution_type: str
    recorded_at: datetime
    block_id: Optional[uuid.UUID] = None
    planned_value: Optional[float] = None
    actual_value: Optional[float] = None
    planned_unit: Optional[str] = None
    actual_unit: Optional[str] = None
    adjustment_reason_type: Optional[str] = None
    coach_rationale: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class CreateSessionObjectiveInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    origin: str
    objective_type: str
    description: str
    origin_notes: Optional[str] = None
    priority: Optional[int] = None


@dataclass
class ListExecutionRecordsInput:
    session_id: uuid.UUID


@dataclass
class GetExecutionRecordInput:
    session_id: uuid.UUID
    record_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


@dataclass
class ListSessionObjectivesInput:
    session_id: uuid.UUID
