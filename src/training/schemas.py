from __future__ import annotations

# CODEGEN CUTOVER — generated layer linked
from .generated import schemas as _gen_schemas  # noqa: F401


"""
Schemas de entrada/saída — módulo training.
Alinhados com contratos OpenAPI e JSON Schemas.
"""

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
# Attendance schemas
# ---------------------------------------------------------------------------

class AttendanceRecordOut(Schema):
    athlete_id: uuid.UUID
    status: str
    recorded_at: datetime
    source: str
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None


class AttendanceListOut(Schema):
    items: List[AttendanceRecordOut]


class RecordSessionAttendanceIn(Schema):
    athlete_id: uuid.UUID
    status: str
    source: str = "coach_input"
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None
    observed_at: Optional[datetime] = None


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


class UpdateWellnessPreIn(Schema):
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


class UpdateWellnessPostIn(Schema):
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


class UpdateMesocycleIn(Schema):
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


class UpdateMicrocycleIn(Schema):
    week_number: Optional[_WeekNumber] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[_PlannedCount] = None
    notes: Optional[str] = None

# ---------------------------------------------------------------------------
# Feedback Threads schemas
# ---------------------------------------------------------------------------

class FeedbackThreadOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    context_type: str
    context_ref_id: uuid.UUID
    conversation_outcome: str
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    athlete_id: Optional[uuid.UUID] = None
    content: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None


class FeedbackThreadListOut(Schema):
    data: List[FeedbackThreadOut]


class CreateFeedbackThreadIn(Schema):
    context_type: str
    context_ref_id: uuid.UUID
    conversation_outcome: str
    athlete_id: Optional[uuid.UUID] = None
    content: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None


class CloseFeedbackThreadIn(Schema):
    resolution_summary: str


# ---------------------------------------------------------------------------
# Attention Queue schemas
# ---------------------------------------------------------------------------

class AttentionQueueItemOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    severity: str
    reason_code: str
    target_entity_type: str
    target_entity_id: uuid.UUID
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[uuid.UUID] = None


class AttentionQueueListOut(Schema):
    data: List[AttentionQueueItemOut]


class ResolveAttentionQueueItemIn(Schema):
    resolution_evidence: str


class DismissAttentionQueueItemIn(Schema):
    dismissal_reason: str


class EscalateAttentionQueueItemIn(Schema):
    escalation_target: str
    escalation_note: str


# ---------------------------------------------------------------------------
# Recommendation schemas
# ---------------------------------------------------------------------------

class RecommendationOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    generated_by_rule: str
    action_type: str
    description: str
    status: str
    generated_by_module: str
    created_at: datetime
    updated_at: datetime
    priority: Optional[str] = None
    coach_note: Optional[str] = None
    dismissal_reason: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[uuid.UUID] = None


class RecommendationListOut(Schema):
    data: List[RecommendationOut]


class AcceptRecommendationIn(Schema):
    coach_note: Optional[str] = None


class DismissRecommendationIn(Schema):
    dismissal_reason: str


# ---------------------------------------------------------------------------
# Ineligibility schemas
# ---------------------------------------------------------------------------

class AthleteIneligibilityDeclarationOut(Schema):
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    reason_flags: List[str]
    declared_at: datetime
    created_at: datetime
    reason_other: Optional[str] = None
    acknowledged_by_coach: bool = False
    coach_note: Optional[str] = None


class SubmitIneligibilityDeclarationIn(Schema):
    athlete_id: uuid.UUID
    reason_flags: List[str]
    reason_other: Optional[str] = None

# ---------------------------------------------------------------------------
# Transition (state actions) schemas
# ---------------------------------------------------------------------------

class UpdateTrainingSessionIn(Schema):
    session_at: Optional[datetime] = None
    session_type: Optional[str] = None
    duration_planned_minutes: Optional[int] = None
    location: Optional[str] = None
    main_objective: Optional[str] = None
    secondary_objective: Optional[str] = None
    planned_load: Optional[int] = None
    intensity_target: Optional[int] = None
    session_block: Optional[str] = None
    standalone: Optional[bool] = None
    notes: Optional[str] = None
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


class ReorderSessionBlocksIn(Schema):
    block_ids: List[uuid.UUID]


class TransitionOut(Schema):
    id: uuid.UUID
    status: str
    updated_at: datetime

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


# ---------------------------------------------------------------------------
# Training Suggestion schemas (Onda E)
# ---------------------------------------------------------------------------

class SubmitTrainingSuggestionIn(Schema):
    athlete_id: uuid.UUID
    subject: str
    body: str


class ErrorOut(Schema):
    detail: str
