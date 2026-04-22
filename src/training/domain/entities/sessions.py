"""
Agregado: TrainingSession (raiz) + SessionObjective.

Contratos:
- contracts/schemas/training/training_session.schema.json
- contracts/schemas/training/session_objective.schema.json (implícito)
Invariantes: INV-TRAIN-001, INV-TRAIN-006, INV-TRAIN-008.
Regras de domínio: DR-TRAIN-001, DR-TRAIN-011/012/013, DR-TRAIN-030.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..common.enums import SessionObjectiveOrigin, TrainingSessionStatus


@dataclass
class TrainingSession:
    """
    Sessão de treino — entidade central do módulo training.
    Contrato: contracts/schemas/training/training_session.schema.json
    INV-TRAIN-001: soma focus_*_pct ≤ 120.
    INV-TRAIN-006: status segue FSM fechada de 7 estados.
    DR-TRAIN-001: criação exige coach ou coordinator.
    DR-TRAIN-030: individualizationMode obrigatório.
    """
    id: uuid.UUID
    organization_id: uuid.UUID
    session_at: datetime
    session_type: str
    status: TrainingSessionStatus
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
    group_climate: Optional[int] = None
    notes: Optional[str] = None
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

    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    closed_at: Optional[datetime] = None
    closed_by_user_id: Optional[uuid.UUID] = None

    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    deviation_justification: Optional[str] = None
    planning_deviation_flag: Optional[bool] = None

    duration_actual_minutes: Optional[int] = None
    execution_outcome: Optional[str] = None
    delay_minutes: Optional[int] = None
    cancellation_reason: Optional[str] = None
    actual_load_recorded: Optional[int] = None

    post_review_completed_at: Optional[datetime] = None
    post_review_completed_by_user_id: Optional[uuid.UUID] = None
    post_review_deadline_at: Optional[datetime] = None
    post_review_completed: Optional[bool] = None

    planned_content_snapshot: Optional[str] = None
    objective_origin: Optional[str] = None

    continuity_notes: Optional[str] = None

    def validate_invariants(self) -> None:
        """Enforce invariantes de TrainingSession."""
        focus_fields = [
            self.focus_attack_positional_pct,
            self.focus_defense_positional_pct,
            self.focus_transition_offense_pct,
            self.focus_transition_defense_pct,
            self.focus_attack_technical_pct,
            self.focus_defense_technical_pct,
            self.focus_physical_pct,
        ]
        total = sum(
            round(Decimal(str(f)), 2) for f in focus_fields if f is not None
        )
        if total > Decimal("120.00"):
            raise ValueError(
                f"INV-TRAIN-001: soma de focus_*_pct={total} excede 120.00"
            )
        for f in focus_fields:
            if f is not None and (Decimal(str(f)) < 0 or Decimal(str(f)) > 100):
                raise ValueError(
                    "INV-TRAIN-001: valores individuais de foco devem estar em [0..100]"
                )

        if (self.deleted_at is None) != (self.deleted_reason is None):
            raise ValueError(
                "INV-TRAIN-008: deletedAt e deletedReason devem ser ambos nulos ou ambos preenchidos"
            )

        if self.session_type and len(self.session_type) > 32:
            raise ValueError("sessionType excede 32 caracteres")
        if self.location and len(self.location) > 120:
            raise ValueError("location excede 120 caracteres")
        if self.main_objective and len(self.main_objective) > 255:
            raise ValueError("mainObjective excede 255 caracteres")
        if self.duration_planned_minutes is not None and not (
            1 <= self.duration_planned_minutes <= 1440
        ):
            raise ValueError("durationPlannedMinutes deve estar em [1..1440]")
        if self.intensity_target is not None and not (
            1 <= self.intensity_target <= 5
        ):
            raise ValueError("intensityTarget deve estar em [1..5]")


@dataclass
class SessionObjective:
    """
    Objetivo operacional de sessão.
    TRAIN-DEC-004/005. DR-TRAIN-011/012/013.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    origin: SessionObjectiveOrigin
    objective_type: str
    description: str
    created_at: datetime
    updated_at: datetime

    origin_notes: Optional[str] = None
    priority: Optional[int] = None

    def validate_invariants(self) -> None:
        if self.origin == SessionObjectiveOrigin.MANUAL_COACH_RATIONALE:
            if not self.origin_notes or len(self.origin_notes) < 10:
                raise ValueError(
                    "DR-TRAIN-013: originNotes obrigatório (mínimo 10 chars) "
                    "quando origin=MANUAL_COACH_RATIONALE"
                )


__all__ = ["TrainingSession", "SessionObjective"]
