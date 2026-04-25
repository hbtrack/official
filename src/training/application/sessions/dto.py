from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ...domain.entities.sessions import TrainingSession
from ...domain.common.enums import TrainingSessionStatus
from ...domain.rules import RoleLabel
from ...application.common.paging import CursorCodec  # noqa: F401 — exposto para uso externo


@dataclass
class ListTrainingSessionsInput:
    actor_role: RoleLabel
    actor_id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    season_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    page_size: int = 20
    page_token: Optional[str] = None


@dataclass
class ListTrainingSessionsOutput:
    items: list[TrainingSession]
    next_page_token: Optional[str] = None


@dataclass
class CreateTrainingSessionInput:
    actor_role: RoleLabel
    actor_id: uuid.UUID
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


@dataclass
class GetTrainingSessionInput:
    id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


@dataclass
class TransitionTrainingSessionInput:
    id: uuid.UUID
    target_status: TrainingSessionStatus
    actor_role: RoleLabel
    actor_id: uuid.UUID


@dataclass
class DeleteTrainingSessionInput:
    id: uuid.UUID
    actor_role: RoleLabel
    deleted_reason: str


@dataclass
class UpdateTrainingSessionInput:
    id: uuid.UUID
    actor_role: RoleLabel
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
    individualization_mode: Optional[str] = None
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
    deviation_justification: Optional[str] = None
    planning_deviation_flag: Optional[bool] = None
