from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema


# ---------------------------------------------------------------------------
# Execution Record schemas
# ---------------------------------------------------------------------------

class ExecutionRecordOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    execution_type: str
    recorded_at: datetime
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    block_id: Optional[uuid.UUID] = None
    planned_value: Optional[float] = None
    actual_value: Optional[float] = None
    planned_unit: Optional[str] = None
    actual_unit: Optional[str] = None
    adjustment_reason_type: Optional[str] = None
    coach_rationale: Optional[str] = None
    notes: Optional[str] = None


class ExecutionRecordListOut(Schema):
    data: List[ExecutionRecordOut]


class CreateExecutionRecordIn(Schema):
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


# ---------------------------------------------------------------------------
# Session Objective schemas
# ---------------------------------------------------------------------------

class SessionObjectiveOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    origin: str
    objective_type: str
    description: str
    created_at: datetime
    updated_at: datetime
    origin_notes: Optional[str] = None
    priority: Optional[int] = None


class SessionObjectiveListOut(Schema):
    data: List[SessionObjectiveOut]


class CreateSessionObjectiveIn(Schema):
    origin: str
    objective_type: str
    description: str
    origin_notes: Optional[str] = None
    priority: Optional[int] = None


# ---------------------------------------------------------------------------
# Load Chart schemas (Onda E)
# ---------------------------------------------------------------------------

class LoadChartEntryOut(Schema):
    id: uuid.UUID
    recorded_at: datetime
    planned_value: Optional[float] = None
    actual_value: Optional[float] = None
    planned_unit: Optional[str] = None
    actual_unit: Optional[str] = None
    notes: Optional[str] = None


class LoadChartOut(Schema):
    session_id: uuid.UUID
    planned_load: Optional[int] = None
    actual_load_recorded: Optional[int] = None
    entries: List[LoadChartEntryOut] = []
