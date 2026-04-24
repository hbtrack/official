from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

_CAMEL = ConfigDict(alias_generator=to_camel, populate_by_name=True)


# ---------------------------------------------------------------------------
# TrainingSession schemas
# ---------------------------------------------------------------------------

class TrainingSessionOut(Schema):
    model_config = _CAMEL
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
    model_config = _CAMEL
    items: List[TrainingSessionOut]
    next_page_token: Optional[str] = None


class CreateTrainingSessionIn(Schema):
    model_config = _CAMEL
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


class UpdateTrainingSessionIn(Schema):
    model_config = _CAMEL
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


class TransitionOut(Schema):
    model_config = _CAMEL
    id: uuid.UUID
    status: str
    updated_at: datetime


# ---------------------------------------------------------------------------
# General error schema (legacy — mantido para compatibilidade retroativa)
# ---------------------------------------------------------------------------

class ErrorOut(Schema):
    model_config = _CAMEL
    detail: str


# ---------------------------------------------------------------------------
# RFC 9457 Problem Details schema — application/problem+json
# Produzido pelo _problem_response() em config/urls.py via handlers globais.
# Usado nos response dicts dos handlers para documentar o OpenAPI corretamente.
# ---------------------------------------------------------------------------

class ProblemOut(Schema):
    model_config = _CAMEL
    type: str
    title: str
    status: int
    traceId: str
    detail: str
