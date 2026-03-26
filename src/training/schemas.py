"""
Schemas de entrada/saída — módulo training.
Alinhados com contratos OpenAPI e JSON Schemas.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Optional

from ninja import Schema
from pydantic import Field


# ---------------------------------------------------------------------------
# TrainingSession schemas
# ---------------------------------------------------------------------------

class TrainingSessionOut(Schema):
    id: uuid.UUID
    organization_id: uuid.UUID
    session_at: datetime
    session_type: str
    status: str
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    team_id: Optional[uuid.UUID] = None
    season_id: Optional[uuid.UUID] = None
    microcycle_id: Optional[uuid.UUID] = None
    duration_planned_minutes: Optional[int] = None
    location: Optional[str] = None
    main_objective: Optional[str] = None
    secondary_objective: Optional[str] = None
    planned_load: Optional[int] = None
    intensity_target: Optional[int] = None
    session_block: Optional[str] = None
    notes: Optional[str] = None
    group_climate: Optional[int] = None
    standalone: Optional[bool] = None
    individualization_mode: Optional[str] = None
    focus_attack_positional_pct: Optional[Decimal] = None
    focus_defense_positional_pct: Optional[Decimal] = None
    focus_transition_offense_pct: Optional[Decimal] = None
    focus_transition_defense_pct: Optional[Decimal] = None
    focus_attack_technical_pct: Optional[Decimal] = None
    focus_defense_technical_pct: Optional[Decimal] = None
    focus_physical_pct: Optional[Decimal] = None
    phase_focus_defense: Optional[bool] = None
    phase_focus_attack: Optional[bool] = None
    phase_focus_transition_offense: Optional[bool] = None
    phase_focus_transition_defense: Optional[bool] = None


class TrainingSessionListOut(Schema):
    items: List[TrainingSessionOut]
    next_page_token: Optional[str] = None


class CreateTrainingSessionIn(Schema):
    organization_id: uuid.UUID
    session_at: datetime
    session_type: str
    team_id: Optional[uuid.UUID] = None
    season_id: Optional[uuid.UUID] = None
    microcycle_id: Optional[uuid.UUID] = None
    duration_planned_minutes: Optional[int] = None
    location: Optional[str] = None
    main_objective: Optional[str] = None
    secondary_objective: Optional[str] = None
    planned_load: Optional[int] = None
    intensity_target: Optional[int] = None
    session_block: Optional[str] = None
    standalone: Optional[bool] = None
    focus_attack_positional_pct: Optional[Decimal] = None
    focus_defense_positional_pct: Optional[Decimal] = None
    focus_transition_offense_pct: Optional[Decimal] = None
    focus_transition_defense_pct: Optional[Decimal] = None
    focus_attack_technical_pct: Optional[Decimal] = None
    focus_defense_technical_pct: Optional[Decimal] = None
    focus_physical_pct: Optional[Decimal] = None
    phase_focus_defense: Optional[bool] = None
    phase_focus_attack: Optional[bool] = None
    phase_focus_transition_offense: Optional[bool] = None
    phase_focus_transition_defense: Optional[bool] = None


# ---------------------------------------------------------------------------
# SessionBlock schemas
# ---------------------------------------------------------------------------

class SessionBlockOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    phase: str
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: str
    is_optional: bool
    created_at: datetime
    updated_at: datetime
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class SessionBlockListOut(Schema):
    data: List[SessionBlockOut]


class AddSessionBlockIn(Schema):
    phase: str
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: str
    is_optional: bool
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class UpdateSessionBlockIn(Schema):
    phase: Optional[str] = None
    duration_minutes: Optional[int] = None
    block_objective: Optional[str] = None
    intensity: Optional[str] = None
    is_optional: Optional[bool] = None
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Wellness schemas
# ---------------------------------------------------------------------------

class WellnessPreOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPreIn(Schema):
    athlete_id: uuid.UUID
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class WellnessPostOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPostIn(Schema):
    athlete_id: uuid.UUID
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


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
# Mesocycle schemas
# ---------------------------------------------------------------------------

class MesocycleOut(Schema):
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
    items: List[MesocycleOut]


class CreateMesocycleIn(Schema):
    organization_id: uuid.UUID
    name: str
    started_at: datetime
    ended_at: datetime
    season_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    objective: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Microcycle schemas
# ---------------------------------------------------------------------------

# SmallIntegerField range; domain rule: >= 1
_WeekNumber = Annotated[int, Field(ge=1, le=32767)]
# SmallIntegerField range for planned_sessions_count (nullable)
_PlannedCount = Annotated[int, Field(ge=0, le=32767)]


class MicrocycleOut(Schema):
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
    items: List[MicrocycleOut]


class CreateMicrocycleIn(Schema):
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


# ---------------------------------------------------------------------------
# Transition (state actions) schemas
# ---------------------------------------------------------------------------

class TransitionOut(Schema):
    id: uuid.UUID
    status: str
    updated_at: datetime


class ErrorOut(Schema):
    detail: str
