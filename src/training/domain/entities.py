"""
Domain entities — módulo training.
Derivadas de:
  - contracts/schemas/training/training_session.schema.json
  - contracts/schemas/training/session_block.schema.json
  - contracts/schemas/training/execution_record.schema.json
  - contracts/schemas/training/feedback_thread.schema.json
  - contracts/schemas/training/mesocycle.schema.json
  - contracts/schemas/training/microcycle.schema.json
  - docs/hbtrack/modulos/training/INVARIANTS_TRAINING.md
  - docs/hbtrack/modulos/training/DOMAIN_RULES_TRAINING.md
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums canônicos — derivados de DOMAIN_AXIOMS.json e contratos
# ---------------------------------------------------------------------------

class TrainingSessionStatus(StrEnum):
    """FSM canônica ADR-017 — 7 estados (INV-TRAIN-006)."""
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class SessionBlockPhase(StrEnum):
    WARMUP = "WARMUP"
    ACTIVATION = "ACTIVATION"
    TECHNICAL = "TECHNICAL"
    DECISION_MAKING = "DECISION_MAKING"
    TACTICAL = "TACTICAL"
    REDUCED_GAME = "REDUCED_GAME"
    COOLDOWN = "COOLDOWN"


class SessionBlockIntensity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    MAXIMUM = "MAXIMUM"


class AttendanceStatus(StrEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    JUSTIFIED = "JUSTIFIED"
    PRECONFIRMED = "PRECONFIRMED"


class AttendanceSource(StrEnum):
    COACH_INPUT = "coach_input"
    ATHLETE_SELFCHECK = "athlete_selfcheck"
    CORRECTION = "correction"


class ExecutionType(StrEnum):
    SESSION_EXECUTION = "SESSION_EXECUTION"
    BLOCK_EXECUTION = "BLOCK_EXECUTION"
    LIVE_ADJUSTMENT = "LIVE_ADJUSTMENT"
    CONSTRAINT_OVERRIDE = "CONSTRAINT_OVERRIDE"
    ALTERNATE_EXERCISE = "ALTERNATE_EXERCISE"
    LOAD_RECALCULATION = "LOAD_RECALCULATION"


class IndividualizationMode(StrEnum):
    COLLECTIVE_UNIFORM = "COLLECTIVE_UNIFORM"
    COLLECTIVE_WITH_VARIANTS = "COLLECTIVE_WITH_VARIANTS"
    INDIVIDUAL_ONLY = "INDIVIDUAL_ONLY"


class SessionObjectiveOrigin(StrEnum):
    NEED_DETECTED = "NEED_DETECTED"
    COMPETITIVE_FOCUS = "COMPETITIVE_FOCUS"
    DEVELOPMENT_GOAL = "DEVELOPMENT_GOAL"
    MANUAL_COACH_RATIONALE = "MANUAL_COACH_RATIONALE"


class ConversationOutcome(StrEnum):
    REFLECTION_DOCUMENTED = "REFLECTION_DOCUMENTED"
    COMMITMENT_MADE = "COMMITMENT_MADE"
    FOLLOWUP_SCHEDULED = "FOLLOWUP_SCHEDULED"
    DECISION_RECORDED = "DECISION_RECORDED"
    PENDING_FOLLOWUP = "PENDING_FOLLOWUP"


class RecommendationActionType(StrEnum):
    MODIFY_FOCUS = "MODIFY_FOCUS"
    ADD_BLOCK = "ADD_BLOCK"
    REMOVE_BLOCK = "REMOVE_BLOCK"
    ADJUST_DURATION = "ADJUST_DURATION"
    ADD_OBJECTIVE = "ADD_OBJECTIVE"
    ADJUST_LOAD = "ADJUST_LOAD"
    REVIEW_ATHLETE = "REVIEW_ATHLETE"


class RecommendationStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DISMISSED = "DISMISSED"


class RecommendationPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ---------------------------------------------------------------------------
# TrainingSession
# ---------------------------------------------------------------------------

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

    # Focus percentages (INV-TRAIN-001)
    focus_attack_positional_pct: Optional[Decimal] = None
    focus_defense_positional_pct: Optional[Decimal] = None
    focus_transition_offense_pct: Optional[Decimal] = None
    focus_transition_defense_pct: Optional[Decimal] = None
    focus_attack_technical_pct: Optional[Decimal] = None
    focus_defense_technical_pct: Optional[Decimal] = None
    focus_physical_pct: Optional[Decimal] = None

    # Phase focus booleans
    phase_focus_defense: Optional[bool] = None
    phase_focus_attack: Optional[bool] = None
    phase_focus_transition_offense: Optional[bool] = None
    phase_focus_transition_defense: Optional[bool] = None

    # Soft delete (INV-TRAIN-008)
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    # Encerramento explícito da sessão
    closed_by_user_id: Optional[uuid.UUID] = None

    # Desvio de planejamento
    deviation_justification: Optional[str] = None
    planning_deviation_flag: Optional[bool] = None

    # Execução real
    duration_actual_minutes: Optional[int] = None
    execution_outcome: Optional[str] = None
    delay_minutes: Optional[int] = None
    cancellation_reason: Optional[str] = None
    actual_load_recorded: Optional[int] = None

    # Revisão pós-sessão
    post_review_completed_at: Optional[datetime] = None
    post_review_completed_by_user_id: Optional[uuid.UUID] = None
    post_review_deadline_at: Optional[datetime] = None
    post_review_completed: Optional[bool] = None

    # Planejamento capturado e objetivo
    planned_content_snapshot: Optional[str] = None
    objective_origin: Optional[str] = None

    # Continuidade
    continuity_notes: Optional[str] = None

    def validate_invariants(self) -> None:
        """Enforce invariantes de TrainingSession."""
        # INV-TRAIN-001: soma focus_*_pct ≤ 120 após arredondamento RC-2
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

        # INV-TRAIN-008: soft delete consistente
        if (self.deleted_at is None) != (self.deleted_reason is None):
            raise ValueError(
                "INV-TRAIN-008: deletedAt e deletedReason devem ser ambos nulos ou ambos preenchidos"
            )

        # Comprimentos do contrato
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


# ---------------------------------------------------------------------------
# SessionBlock
# ---------------------------------------------------------------------------

@dataclass
class SessionBlock:
    """
    Bloco operacional de sessão.
    Contrato: contracts/schemas/training/session_block.schema.json
    TRAIN-DEC-049. INV-TRAIN-083 (Elastic Sum Rule).
    TRAIN-DEC-047: referencia exercise_id + exercise_version_id.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    phase: SessionBlockPhase
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: SessionBlockIntensity
    is_optional: bool
    created_at: datetime
    updated_at: datetime

    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

    def validate_invariants(self) -> None:
        """TRAIN-DEC-047: exerciseVersionId obrigatório quando exerciseId presente."""
        if self.exercise_id is not None and self.exercise_version_id is None:
            raise ValueError(
                "TRAIN-DEC-047: exerciseVersionId é obrigatório quando exerciseId está presente"
            )
        if not (1 <= self.duration_minutes <= 240):
            raise ValueError("durationMinutes deve estar em [1..240]")
        if len(self.block_objective) < 3 or len(self.block_objective) > 300:
            raise ValueError("blockObjective deve ter entre 3 e 300 caracteres")
        if self.notes and len(self.notes) > 1000:
            raise ValueError("notes excede 1000 caracteres")
        if self.order_index < 0:
            raise ValueError("orderIndex deve ser >= 0")


# ---------------------------------------------------------------------------
# AttendanceRecord
# ---------------------------------------------------------------------------

@dataclass
class AttendanceRecord:
    """Fato append-only de presença por atleta em uma sessão."""

    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    status: AttendanceStatus
    source: AttendanceSource
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.source == AttendanceSource.CORRECTION:
            if self.correction_by_user_id is None or self.correction_at is None:
                raise ValueError(
                    "INV-TRAIN-030: correction exige correctionByUserId e correctionAt"
                )
        elif self.correction_by_user_id is not None or self.correction_at is not None:
            raise ValueError(
                "INV-TRAIN-030: campos de correção só são permitidos quando source=correction"
            )

        if self.source == AttendanceSource.ATHLETE_SELFCHECK and self.status != AttendanceStatus.PRECONFIRMED:
            raise ValueError(
                "INV-TRAIN-063: athlete_selfcheck só pode registrar status PRECONFIRMED"
            )

        if self.status == AttendanceStatus.JUSTIFIED:
            if not self.justification_reason:
                raise ValueError(
                    "attendance.justificationReason é obrigatório quando status=JUSTIFIED"
                )
        elif self.justification_reason:
            raise ValueError(
                "attendance.justificationReason só é permitido quando status=JUSTIFIED"
            )

        if self.justification_reason and len(self.justification_reason) > 255:
            raise ValueError("attendance.justificationReason excede 255 caracteres")


# ---------------------------------------------------------------------------
# WellnessPre
# ---------------------------------------------------------------------------

@dataclass
class WellnessPre:
    """
    Wellness pré-treino por atleta.
    Contrato: contracts/openapi/components/schemas/training/wellness_pre.yaml
    INV-TRAIN-002: janela temporal de submissão (session_at - 2h).
    INV-TRAIN-009: máximo 1 ativo por (session_id, athlete_id).
    """
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    readiness: Optional[int] = None   # 1-5
    sleep_quality: Optional[int] = None  # 1-5
    mood: Optional[int] = None  # 1-5
    fatigue: Optional[int] = None  # 1-5
    muscle_soreness: Optional[int] = None  # 1-5
    notes: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    def validate_invariants(self) -> None:
        for name, val in [
            ("readiness", self.readiness),
            ("sleepQuality", self.sleep_quality),
            ("mood", self.mood),
            ("fatigue", self.fatigue),
            ("muscleSoreness", self.muscle_soreness),
        ]:
            if val is not None and not (1 <= val <= 5):
                raise ValueError(f"{name} deve estar em [1..5]")


# ---------------------------------------------------------------------------
# WellnessPost
# ---------------------------------------------------------------------------

@dataclass
class WellnessPost:
    """
    Wellness pós-treino por atleta.
    INV-TRAIN-003: janela de edição de 24h após criação.
    INV-TRAIN-010: máximo 1 ativo por (session_id, athlete_id).
    """
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    perceived_exertion: Optional[int] = None   # 1-10 RPE
    enjoyment: Optional[int] = None  # 1-5
    technical_learning: Optional[int] = None  # 1-5
    notes: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.perceived_exertion is not None and not (1 <= self.perceived_exertion <= 10):
            raise ValueError("perceivedExertion deve estar em [1..10]")
        for name, val in [
            ("enjoyment", self.enjoyment),
            ("technicalLearning", self.technical_learning),
        ]:
            if val is not None and not (1 <= val <= 5):
                raise ValueError(f"{name} deve estar em [1..5]")


# ---------------------------------------------------------------------------
# ExecutionRecord
# ---------------------------------------------------------------------------

@dataclass
class ExecutionRecord:
    """
    Registro de execução — append-only.
    TRAIN-DEC-007/008/009. INV-TRAIN-087.
    DR-TRAIN-015: sempre vinculado a sessionId.
    DR-TRAIN-017: plannedContent e actualContent separados.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    execution_type: ExecutionType
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

    def validate_invariants(self) -> None:
        # DR-TRAIN-019: LIVE_ADJUSTMENT e CONSTRAINT_OVERRIDE exigem coachRationale
        if self.execution_type in (
            ExecutionType.LIVE_ADJUSTMENT, ExecutionType.CONSTRAINT_OVERRIDE
        ):
            if not self.coach_rationale or len(self.coach_rationale) < 5:
                raise ValueError(
                    "DR-TRAIN-019: coachRationale obrigatório (mínimo 5 chars) para "
                    f"executionType={self.execution_type}"
                )
        if self.planned_unit and len(self.planned_unit) > 32:
            raise ValueError("plannedUnit excede 32 caracteres")
        if self.actual_unit and len(self.actual_unit) > 32:
            raise ValueError("actualUnit excede 32 caracteres")


# ---------------------------------------------------------------------------
# SessionObjective
# ---------------------------------------------------------------------------

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
        # DR-TRAIN-013: MANUAL_COACH_RATIONALE exige originNotes mínimo 10 chars
        if self.origin == SessionObjectiveOrigin.MANUAL_COACH_RATIONALE:
            if not self.origin_notes or len(self.origin_notes) < 10:
                raise ValueError(
                    "DR-TRAIN-013: originNotes obrigatório (mínimo 10 chars) "
                    "quando origin=MANUAL_COACH_RATIONALE"
                )


# ---------------------------------------------------------------------------
# FeedbackThread
# ---------------------------------------------------------------------------

@dataclass
class FeedbackThread:
    """
    Thread de feedback técnico.
    TRAIN-DEC-010/015. DR-TRAIN-020/021/022.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    created_by_user_id: uuid.UUID
    conversation_outcome: ConversationOutcome
    created_at: datetime
    updated_at: datetime

    block_id: Optional[uuid.UUID] = None
    athlete_id: Optional[uuid.UUID] = None
    objective_id: Optional[uuid.UUID] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None
    closed_at: Optional[datetime] = None

    def validate_invariants(self) -> None:
        # DR-TRAIN-022
        if self.conversation_outcome == ConversationOutcome.FOLLOWUP_SCHEDULED:
            if self.follow_up_at is None:
                raise ValueError(
                    "DR-TRAIN-022: followUpAt obrigatório quando outcome=FOLLOWUP_SCHEDULED"
                )
        if self.conversation_outcome == ConversationOutcome.COMMITMENT_MADE:
            if not self.commitment_text:
                raise ValueError(
                    "DR-TRAIN-022: commitmentText obrigatório quando outcome=COMMITMENT_MADE"
                )
        if self.conversation_outcome == ConversationOutcome.DECISION_RECORDED:
            if not self.decision_text:
                raise ValueError(
                    "DR-TRAIN-022: decisionText obrigatório quando outcome=DECISION_RECORDED"
                )


# ---------------------------------------------------------------------------
# AttentionQueueItem
# ---------------------------------------------------------------------------

@dataclass
class AttentionQueueItem:
    """Item da fila de atenção técnica do treinador."""
    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    reason: str
    severity: str
    created_at: datetime
    updated_at: datetime

    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None
    dismissed_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class Recommendation:
    """Recomendação analítica pendente de decisão explícita do coach."""

    id: uuid.UUID
    session_id: uuid.UUID
    generated_by_rule: str
    action_type: RecommendationActionType
    description: str
    status: RecommendationStatus
    generated_by_module: str
    created_at: datetime
    updated_at: datetime

    priority: Optional[RecommendationPriority] = None
    coach_note: Optional[str] = None
    dismissal_reason: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[uuid.UUID] = None

    def validate_invariants(self) -> None:
        if not self.generated_by_rule or len(self.generated_by_rule) > 128:
            raise ValueError("generatedByRule é obrigatório e deve ter <= 128 caracteres")
        if not self.generated_by_rule.replace("_", "").isalnum() or self.generated_by_rule.upper() != self.generated_by_rule:
            raise ValueError("generatedByRule deve estar em UPPER_SNAKE_CASE")
        if not self.description or len(self.description) > 1000:
            raise ValueError("description é obrigatória e deve ter <= 1000 caracteres")
        if not self.generated_by_module or len(self.generated_by_module) > 64:
            raise ValueError("generatedByModule é obrigatório e deve ter <= 64 caracteres")
        if self.status == RecommendationStatus.DISMISSED and not self.dismissal_reason:
            raise ValueError("dismissalReason é obrigatório quando status=DISMISSED")
        if self.status == RecommendationStatus.PENDING:
            if self.dismissal_reason or self.coach_note or self.resolved_at or self.resolved_by_user_id:
                raise ValueError("Recommendation pendente não pode ter campos de resolução preenchidos")
        else:
            if self.resolved_at is None or self.resolved_by_user_id is None:
                raise ValueError("Recommendation resolvida exige resolvedAt e resolvedByUserId")
        if self.coach_note and len(self.coach_note) > 500:
            raise ValueError("coachNote deve ter <= 500 caracteres")
        if self.dismissal_reason and len(self.dismissal_reason) > 500:
            raise ValueError("dismissalReason deve ter <= 500 caracteres")


@dataclass
class AthleteIneligibilityDeclaration:
    """Declaração self-service de indisponibilidade do atleta para uma sessão."""

    id: uuid.UUID
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    declared_at: datetime
    created_at: datetime

    reason_flags: list[str] = field(default_factory=list)
    reason_other: Optional[str] = None
    acknowledged_by_coach: bool = False
    coach_note: Optional[str] = None

    def validate_invariants(self) -> None:
        if not self.reason_flags:
            raise ValueError("reasonFlags deve conter pelo menos um motivo")
        allowed_flags = {
            "MEDICAL_APPOINTMENT",
            "INJURY_PAIN",
            "ACTIVE_RECOVERY_ONLY",
            "TESTING_ANTI_DOPING",
            "OTHER",
        }
        invalid = [flag for flag in self.reason_flags if flag not in allowed_flags]
        if invalid:
            raise ValueError(f"reasonFlags contém valores inválidos: {invalid}")
        if "OTHER" in self.reason_flags and not self.reason_other:
            raise ValueError("reasonOther é obrigatório quando OTHER está presente em reasonFlags")
        if "OTHER" not in self.reason_flags and self.reason_other:
            raise ValueError("reasonOther só é permitido quando OTHER está presente em reasonFlags")
        if self.reason_other and len(self.reason_other) > 500:
            raise ValueError("reasonOther deve ter <= 500 caracteres")
        if self.coach_note and len(self.coach_note) > 500:
            raise ValueError("coachNote deve ter <= 500 caracteres")


# ---------------------------------------------------------------------------
# Mesocycle
# ---------------------------------------------------------------------------

@dataclass
class Mesocycle:
    """
    Bloco de periodização médio (4-6 semanas).
    TRAIN-DEC-H04.
    """
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

    def validate_invariants(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("name é obrigatório para Mesocycle")
        if self.started_at >= self.ended_at:
            raise ValueError("startedAt deve ser anterior a endedAt")


# ---------------------------------------------------------------------------
# Microcycle
# ---------------------------------------------------------------------------

@dataclass
class Microcycle:
    """
    Unidade semanal de periodização.
    TRAIN-DEC-H04.
    """
    id: uuid.UUID
    organization_id: uuid.UUID
    mesocycle_id: uuid.UUID
    week_number: int
    started_at: datetime
    ended_at: datetime
    created_at: datetime
    updated_at: datetime

    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    planned_sessions_count: Optional[int] = None
    notes: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.started_at >= self.ended_at:
            raise ValueError("startedAt deve ser anterior a endedAt")
        if self.week_number < 1:
            raise ValueError("weekNumber deve ser >= 1")
        if self.week_number > 32767:
            raise ValueError("weekNumber deve ser <= 32767 (SmallIntegerField)")
