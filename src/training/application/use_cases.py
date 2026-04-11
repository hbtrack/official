"""
Use cases — módulo training.
Um use case por feature canônica do contrato.
Derivados de DOMAIN_RULES_TRAINING.md, PERMISSIONS_TRAINING.md, INVARIANTS_TRAINING.md.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from ..domain.entities import (
    AttentionQueueItem,
    AthleteIneligibilityDeclaration,
    AttendanceRecord,
    AttendanceSource,
    AttendanceStatus,
    ConversationOutcome,
    ExecutionRecord,
    ExecutionType,
    FeedbackThread,
    Mesocycle,
    Microcycle,
    Recommendation,
    RecommendationActionType,
    RecommendationPriority,
    RecommendationStatus,
    SessionBlock,
    SessionBlockIntensity,
    SessionBlockPhase,
    SessionObjective,
    SessionObjectiveOrigin,
    TrainingSession,
    TrainingSessionStatus,
    WellnessPost,
    WellnessPre,
)
from ..domain.rules import (
    AttendanceRecordNotFound,
    AttentionQueueConflict,
    AttentionQueueItemNotFound,
    ExecutionRecordNotFound,
    FeedbackThreadNotFound,
    IneligibilityDeclarationNotFound,
    MesocycleNotFound,
    MUTABLE_STATES,
    MicrocycleNotFound,
    RecommendationConflict,
    RecommendationNotFound,
    RoleLabel,
    WellnessEntryNotFound,
    assert_can_record_attendance,
    assert_can_create_session,
    assert_can_delete_session,
    assert_can_modify_session,
    assert_can_read_session,
    assert_can_view_athlete_record,
    assert_can_submit_wellness,
    assert_elastic_sum_rule,
    assert_session_mutable,
    assert_session_not_historical,
    assert_valid_transition,
    assert_wellness_post_window,
    assert_wellness_pre_window,
    DuplicateWellnessEntry,
    TrainingSessionNotFound,
    SessionBlockNotFound,
    InsufficientPrivilege,
)
from ..infrastructure.repository import (
    AttentionQueueRepository,
    AthleteIneligibilityDeclarationRepository,
    AttendanceRepository,
    ExecutionRecordRepository,
    FeedbackThreadRepository,
    MesocycleRepository,
    MicrocycleRepository,
    RecommendationRepository,
    SessionBlockRepository,
    SessionObjectiveRepository,
    TrainingSessionRepository,
    WellnessPostRepository,
    WellnessPreRepository,
)


# ---------------------------------------------------------------------------
# Training Session use cases
# ---------------------------------------------------------------------------

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


class ListTrainingSessionsUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo

    def execute(self, inp: ListTrainingSessionsInput) -> ListTrainingSessionsOutput:
        # member não acessa sessões — PERMISSIONS_TRAINING.md
        if inp.actor_role == RoleLabel.MEMBER:
            raise InsufficientPrivilege("member não tem acesso a sessões de treino")
        items = self._repo.list(
            organization_id=inp.organization_id,
            team_id=inp.team_id,
            season_id=inp.season_id,
            status=inp.status,
            page_size=inp.page_size,
            page_token=inp.page_token,
        )
        # Athlete: filtra somente sessões com team_id do actor (simplificado)
        # Integração real com identity_access resolverá team_ids por actor
        next_token = str(items[-1].session_at.isoformat()) if len(items) == inp.page_size else None
        return ListTrainingSessionsOutput(items=items, next_page_token=next_token)


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


class CreateTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo

    def execute(self, inp: CreateTrainingSessionInput) -> TrainingSession:
        # DR-TRAIN-001
        assert_can_create_session(inp.actor_role)
        session = TrainingSession(
            id=uuid.uuid4(),
            organization_id=inp.organization_id,
            session_at=inp.session_at,
            session_type=inp.session_type,
            status=TrainingSessionStatus.DRAFT,
            created_by_user_id=inp.actor_id,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
            team_id=inp.team_id,
            season_id=inp.season_id,
            microcycle_id=inp.microcycle_id,
            duration_planned_minutes=inp.duration_planned_minutes,
            location=inp.location,
            main_objective=inp.main_objective,
            secondary_objective=inp.secondary_objective,
            planned_load=inp.planned_load,
            intensity_target=inp.intensity_target,
            session_block=inp.session_block,
            standalone=inp.standalone,
            focus_attack_positional_pct=inp.focus_attack_positional_pct,
            focus_defense_positional_pct=inp.focus_defense_positional_pct,
            focus_transition_offense_pct=inp.focus_transition_offense_pct,
            focus_transition_defense_pct=inp.focus_transition_defense_pct,
            focus_attack_technical_pct=inp.focus_attack_technical_pct,
            focus_defense_technical_pct=inp.focus_defense_technical_pct,
            focus_physical_pct=inp.focus_physical_pct,
            phase_focus_defense=inp.phase_focus_defense,
            phase_focus_attack=inp.phase_focus_attack,
            phase_focus_transition_offense=inp.phase_focus_transition_offense,
            phase_focus_transition_defense=inp.phase_focus_transition_defense,
        )
        session.validate_invariants()
        return self._repo.save(session)


@dataclass
class GetTrainingSessionInput:
    id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    # athlete_ids da sessão viriam do identity_access em integração real
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


class GetTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo

    def execute(self, inp: GetTrainingSessionInput) -> TrainingSession:
        session = self._repo.get_by_id(inp.id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.id} não encontrada")
        assert_can_read_session(inp.actor_role, inp.actor_id, inp.session_athlete_ids)
        return session


@dataclass
class TransitionTrainingSessionInput:
    id: uuid.UUID
    target_status: TrainingSessionStatus
    actor_role: RoleLabel
    actor_id: uuid.UUID


class TransitionTrainingSessionUseCase:
    """Handles start/complete/cancel/publish/unpublish/archive operations."""
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo

    def execute(self, inp: TransitionTrainingSessionInput) -> TrainingSession:
        session = self._repo.get_by_id(inp.id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        if inp.target_status == TrainingSessionStatus.ARCHIVED:
            from ..domain.rules import assert_can_delete_session, CAN_ARCHIVE_SESSION
            if inp.actor_role not in CAN_ARCHIVE_SESSION:
                raise InsufficientPrivilege("Apenas admin/coordinator podem arquivar sessões")
        assert_valid_transition(session.status, inp.target_status)
        session.status = inp.target_status
        session.updated_at = datetime.now(tz=timezone.utc)
        return self._repo.save(session)


@dataclass
class DeleteTrainingSessionInput:
    id: uuid.UUID
    actor_role: RoleLabel
    deleted_reason: str


class DeleteTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo

    def execute(self, inp: DeleteTrainingSessionInput) -> None:
        session = self._repo.get_by_id(inp.id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.id} não encontrada")
        assert_can_delete_session(inp.actor_role)
        # DR-TRAIN-027: sessões IN_PROGRESS não podem ser excluídas fisicamente
        if session.status == TrainingSessionStatus.IN_PROGRESS:
            raise InsufficientPrivilege(
                "DR-TRAIN-027: sessão IN_PROGRESS não pode ser excluída — use cancelamento lógico"
            )
        now = datetime.now(tz=timezone.utc)
        session.deleted_at = now
        session.deleted_reason = inp.deleted_reason
        session.updated_at = now
        self._repo.save(session)


# ---------------------------------------------------------------------------
# Session Block use cases
# ---------------------------------------------------------------------------

@dataclass
class ListSessionBlocksInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


class ListSessionBlocksUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: ListSessionBlocksInput) -> list[SessionBlock]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_read_session(inp.actor_role, inp.actor_id, inp.session_athlete_ids)
        return self._block_repo.list_by_session(inp.session_id)


@dataclass
class AddSessionBlockInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    phase: str
    order_index: int
    duration_minutes: int
    block_objective: str
    intensity: str
    is_optional: bool
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class AddSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: AddSessionBlockInput) -> SessionBlock:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        # INV-TRAIN-083
        current_total = self._block_repo.total_duration_for_session(inp.session_id)
        assert_elastic_sum_rule(session.duration_planned_minutes, current_total, inp.duration_minutes)
        block = SessionBlock(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            phase=SessionBlockPhase(inp.phase),
            order_index=inp.order_index,
            duration_minutes=inp.duration_minutes,
            block_objective=inp.block_objective,
            intensity=SessionBlockIntensity(inp.intensity),
            is_optional=inp.is_optional,
            exercise_id=inp.exercise_id,
            exercise_version_id=inp.exercise_version_id,
            notes=inp.notes,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        block.validate_invariants()
        return self._block_repo.save(block)


@dataclass
class UpdateSessionBlockInput:
    session_id: uuid.UUID
    block_id: uuid.UUID
    actor_role: RoleLabel
    duration_minutes: Optional[int] = None
    block_objective: Optional[str] = None
    intensity: Optional[str] = None
    phase: Optional[str] = None
    is_optional: Optional[bool] = None
    notes: Optional[str] = None
    exercise_id: Optional[uuid.UUID] = None
    exercise_version_id: Optional[uuid.UUID] = None


class UpdateSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: UpdateSessionBlockInput) -> SessionBlock:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        block = self._block_repo.get_by_id(inp.block_id)
        if not block:
            raise SessionBlockNotFound(f"Bloco {inp.block_id} não encontrado")
        if inp.duration_minutes is not None:
            current_total = self._block_repo.total_duration_for_session(inp.session_id, exclude_id=inp.block_id)
            assert_elastic_sum_rule(session.duration_planned_minutes, current_total, inp.duration_minutes)
            block.duration_minutes = inp.duration_minutes
        if inp.block_objective is not None:
            block.block_objective = inp.block_objective
        if inp.intensity is not None:
            block.intensity = SessionBlockIntensity(inp.intensity)
        if inp.phase is not None:
            block.phase = SessionBlockPhase(inp.phase)
        if inp.is_optional is not None:
            block.is_optional = inp.is_optional
        if inp.notes is not None:
            block.notes = inp.notes
        if inp.exercise_id is not None:
            block.exercise_id = inp.exercise_id
        if inp.exercise_version_id is not None:
            block.exercise_version_id = inp.exercise_version_id
        block.updated_at = datetime.now(tz=timezone.utc)
        block.validate_invariants()
        return self._block_repo.save(block)


@dataclass
class DeleteSessionBlockInput:
    session_id: uuid.UUID
    block_id: uuid.UUID
    actor_role: RoleLabel


class DeleteSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: DeleteSessionBlockInput) -> None:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        block = self._block_repo.get_by_id(inp.block_id)
        if not block:
            raise SessionBlockNotFound(f"Bloco {inp.block_id} não encontrado")
        self._block_repo.delete(inp.block_id)


# ---------------------------------------------------------------------------
# Wellness Pre use cases
# ---------------------------------------------------------------------------

@dataclass
class SubmitWellnessPreInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPreUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        wellness_repo: WellnessPreRepository,
    ):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: SubmitWellnessPreInput) -> WellnessPre:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_submit_wellness(inp.actor_role, inp.actor_id, inp.athlete_id)
        # INV-TRAIN-002: janela temporal
        assert_wellness_pre_window(session.session_at)
        # INV-TRAIN-009: unicidade
        existing = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if existing:
            raise DuplicateWellnessEntry("INV-TRAIN-009: já existe wellness_pre ativo para este atleta/sessão")
        now = datetime.now(tz=timezone.utc)
        wellness = WellnessPre(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            readiness=inp.readiness,
            sleep_quality=inp.sleep_quality,
            mood=inp.mood,
            fatigue=inp.fatigue,
            muscle_soreness=inp.muscle_soreness,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)


# ---------------------------------------------------------------------------
# Wellness Post use cases
# ---------------------------------------------------------------------------

@dataclass
class SubmitWellnessPostInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


class SubmitWellnessPostUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        wellness_repo: WellnessPostRepository,
    ):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: SubmitWellnessPostInput) -> WellnessPost:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_submit_wellness(inp.actor_role, inp.actor_id, inp.athlete_id)
        # Requer sessão IN_PROGRESS ou COMPLETED
        if session.status not in (TrainingSessionStatus.IN_PROGRESS, TrainingSessionStatus.COMPLETED):
            raise InsufficientPrivilege("WellnessPost requer sessão IN_PROGRESS ou COMPLETED")
        # INV-TRAIN-010: unicidade
        existing = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if existing:
            raise DuplicateWellnessEntry("INV-TRAIN-010: já existe wellness_post ativo para este atleta/sessão")
        now = datetime.now(tz=timezone.utc)
        wellness = WellnessPost(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            perceived_exertion=inp.perceived_exertion,
            enjoyment=inp.enjoyment,
            technical_learning=inp.technical_learning,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)


# ---------------------------------------------------------------------------
# Execution Record use cases
# ---------------------------------------------------------------------------

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


class CreateExecutionRecordUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._record_repo = record_repo

    def execute(self, inp: CreateExecutionRecordInput) -> ExecutionRecord:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        if session.status != TrainingSessionStatus.IN_PROGRESS:
            raise InsufficientPrivilege("ExecutionRecord requer sessão IN_PROGRESS")
        now = datetime.now(tz=timezone.utc)
        record = ExecutionRecord(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            block_id=inp.block_id,
            execution_type=ExecutionType(inp.execution_type),
            recorded_at=inp.recorded_at,
            planned_value=inp.planned_value,
            actual_value=inp.actual_value,
            planned_unit=inp.planned_unit,
            actual_unit=inp.actual_unit,
            adjustment_reason_type=inp.adjustment_reason_type,
            coach_rationale=inp.coach_rationale,
            notes=inp.notes,
            created_by_user_id=inp.actor_id,
            created_at=now,
            updated_at=now,
        )
        record.validate_invariants()
        return self._record_repo.save(record)


# ---------------------------------------------------------------------------
# Session Objective use cases
# ---------------------------------------------------------------------------

@dataclass
class CreateSessionObjectiveInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    origin: str
    objective_type: str
    description: str
    origin_notes: Optional[str] = None
    priority: Optional[int] = None


class CreateSessionObjectiveUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, obj_repo: SessionObjectiveRepository):
        self._session_repo = session_repo
        self._obj_repo = obj_repo

    def execute(self, inp: CreateSessionObjectiveInput) -> SessionObjective:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        now = datetime.now(tz=timezone.utc)
        obj = SessionObjective(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            origin=SessionObjectiveOrigin(inp.origin),
            objective_type=inp.objective_type,
            description=inp.description,
            origin_notes=inp.origin_notes,
            priority=inp.priority,
            created_at=now,
            updated_at=now,
        )
        obj.validate_invariants()
        return self._obj_repo.save(obj)


# ---------------------------------------------------------------------------
# Mesocycle use cases
# ---------------------------------------------------------------------------

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


class CreateMesocycleUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: CreateMesocycleInput) -> Mesocycle:
        assert_can_modify_session(inp.actor_role)
        now = datetime.now(tz=timezone.utc)
        meso = Mesocycle(
            id=uuid.uuid4(),
            organization_id=inp.organization_id,
            name=inp.name,
            started_at=inp.started_at,
            ended_at=inp.ended_at,
            season_id=inp.season_id,
            team_id=inp.team_id,
            objective=inp.objective,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        meso.validate_invariants()
        return self._repo.save(meso)


# ---------------------------------------------------------------------------
# Microcycle use cases
# ---------------------------------------------------------------------------

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


class CreateMicrocycleUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: CreateMicrocycleInput) -> Microcycle:
        assert_can_modify_session(inp.actor_role)
        now = datetime.now(tz=timezone.utc)
        micro = Microcycle(
            id=uuid.uuid4(),
            organization_id=inp.organization_id,
            mesocycle_id=inp.mesocycle_id,
            week_number=inp.week_number,
            started_at=inp.started_at,
            ended_at=inp.ended_at,
            team_id=inp.team_id,
            name=inp.name,
            objective=inp.objective,
            planned_sessions_count=inp.planned_sessions_count,
            notes=inp.notes,
            created_at=now,
            updated_at=now,
        )
        micro.validate_invariants()
        return self._repo.save(micro)


# ---------------------------------------------------------------------------
# Stubs de use case — B10-001 source graph integrity
# Implementação pendente (known_gaps). raise NotImplementedError até fase futura.
# ---------------------------------------------------------------------------

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


class UpdateTrainingSessionUseCase:
    def __init__(self, repo: TrainingSessionRepository):
        self._repo = repo

    def execute(self, inp: UpdateTrainingSessionInput) -> TrainingSession:
        session = self._repo.get_by_id(inp.id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        assert_session_not_historical(session.session_at)
        if inp.session_at is not None:
            session.session_at = inp.session_at
        if inp.session_type is not None:
            session.session_type = inp.session_type
        if inp.duration_planned_minutes is not None:
            session.duration_planned_minutes = inp.duration_planned_minutes
        if inp.location is not None:
            session.location = inp.location
        if inp.main_objective is not None:
            session.main_objective = inp.main_objective
        if inp.secondary_objective is not None:
            session.secondary_objective = inp.secondary_objective
        if inp.planned_load is not None:
            session.planned_load = inp.planned_load
        if inp.intensity_target is not None:
            session.intensity_target = inp.intensity_target
        if inp.session_block is not None:
            session.session_block = inp.session_block
        if inp.standalone is not None:
            session.standalone = inp.standalone
        if inp.notes is not None:
            session.notes = inp.notes
        if inp.focus_attack_positional_pct is not None:
            session.focus_attack_positional_pct = inp.focus_attack_positional_pct
        if inp.focus_defense_positional_pct is not None:
            session.focus_defense_positional_pct = inp.focus_defense_positional_pct
        if inp.focus_transition_offense_pct is not None:
            session.focus_transition_offense_pct = inp.focus_transition_offense_pct
        if inp.focus_transition_defense_pct is not None:
            session.focus_transition_defense_pct = inp.focus_transition_defense_pct
        if inp.focus_attack_technical_pct is not None:
            session.focus_attack_technical_pct = inp.focus_attack_technical_pct
        if inp.focus_defense_technical_pct is not None:
            session.focus_defense_technical_pct = inp.focus_defense_technical_pct
        if inp.focus_physical_pct is not None:
            session.focus_physical_pct = inp.focus_physical_pct
        if inp.phase_focus_defense is not None:
            session.phase_focus_defense = inp.phase_focus_defense
        if inp.phase_focus_attack is not None:
            session.phase_focus_attack = inp.phase_focus_attack
        if inp.phase_focus_transition_offense is not None:
            session.phase_focus_transition_offense = inp.phase_focus_transition_offense
        if inp.phase_focus_transition_defense is not None:
            session.phase_focus_transition_defense = inp.phase_focus_transition_defense
        session.updated_at = datetime.now(tz=timezone.utc)
        session.validate_invariants()
        return self._repo.save(session)


@dataclass
class GetSessionBlockInput:
    session_id: uuid.UUID
    block_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


class GetSessionBlockUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: GetSessionBlockInput) -> SessionBlock:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_read_session(inp.actor_role, inp.actor_id, inp.session_athlete_ids)
        block = self._block_repo.get_by_id(inp.block_id)
        if not block or block.session_id != inp.session_id:
            raise SessionBlockNotFound(f"Bloco {inp.block_id} não encontrado")
        return block


@dataclass
class ReorderSessionBlocksInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    block_ids: list[uuid.UUID]


class ReorderSessionBlocksUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, block_repo: SessionBlockRepository):
        self._session_repo = session_repo
        self._block_repo = block_repo

    def execute(self, inp: ReorderSessionBlocksInput) -> list[SessionBlock]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        assert_session_mutable(session.status)
        existing = self._block_repo.list_by_session(inp.session_id)
        existing_ids = {b.id for b in existing}
        if set(inp.block_ids) != existing_ids:
            raise ValueError(
                "blockIds deve conter exatamente todos os IDs dos blocos da sessão"
            )
        block_map = {b.id: b for b in existing}
        result = []
        now = datetime.now(tz=timezone.utc)
        for order_index, block_id in enumerate(inp.block_ids):
            block = block_map[block_id]
            block.order_index = order_index
            block.updated_at = now
            result.append(self._block_repo.save(block))
        return result


@dataclass
class ListSessionAttendanceInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID


class ListSessionAttendanceUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, attendance_repo: AttendanceRepository):
        self._session_repo = session_repo
        self._attendance_repo = attendance_repo

    def execute(self, inp: ListSessionAttendanceInput) -> list[AttendanceRecord]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        if inp.actor_role == RoleLabel.MEMBER:
            raise InsufficientPrivilege("member não tem acesso à presença da sessão")
        records = self._attendance_repo.list_by_session(inp.session_id)
        if inp.actor_role == RoleLabel.ATHLETE:
            return [record for record in records if record.athlete_id == inp.actor_id]
        return records


@dataclass
class RecordSessionAttendanceInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    status: str
    actor_role: RoleLabel
    actor_id: uuid.UUID
    source: str = "coach_input"
    correction_by_user_id: Optional[uuid.UUID] = None
    correction_at: Optional[datetime] = None
    justification_reason: Optional[str] = None
    observed_at: Optional[datetime] = None


class RecordSessionAttendanceUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, attendance_repo: AttendanceRepository):
        self._session_repo = session_repo
        self._attendance_repo = attendance_repo

    def execute(self, inp: RecordSessionAttendanceInput) -> AttendanceRecord:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        status = AttendanceStatus(inp.status)
        source = AttendanceSource(inp.source)
        assert_can_record_attendance(inp.actor_role, inp.actor_id, inp.athlete_id, status, source)
        if inp.actor_role == RoleLabel.ATHLETE and datetime.now(tz=timezone.utc) >= session.session_at:
            raise InsufficientPrivilege(
                "INV-TRAIN-063: athlete só pode PRECONFIRM antes do início da sessão"
            )
        now = datetime.now(tz=timezone.utc)
        record = AttendanceRecord(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            status=status,
            source=source,
            recorded_at=inp.observed_at or now,
            created_at=now,
            updated_at=now,
            correction_by_user_id=inp.correction_by_user_id,
            correction_at=inp.correction_at,
            justification_reason=inp.justification_reason,
        )
        record.validate_invariants()
        return self._attendance_repo.save(record)


@dataclass
class GetWellnessPreInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID


class GetWellnessPreUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPreRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: GetWellnessPreInput) -> WellnessPre:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_pre não encontrado para este atleta/sessão")
        return wellness


@dataclass
class UpdateWellnessPreInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    readiness: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood: Optional[int] = None
    fatigue: Optional[int] = None
    muscle_soreness: Optional[int] = None
    notes: Optional[str] = None


class UpdateWellnessPreUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPreRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: UpdateWellnessPreInput) -> WellnessPre:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        assert_wellness_pre_window(session.session_at)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_pre não encontrado para este atleta/sessão")
        for field_name in ("readiness", "sleep_quality", "mood", "fatigue", "muscle_soreness", "notes"):
            value = getattr(inp, field_name)
            if value is not None:
                setattr(wellness, field_name, value)
        wellness.updated_at = datetime.now(tz=timezone.utc)
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)


@dataclass
class GetWellnessPostInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID


class GetWellnessPostUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPostRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: GetWellnessPostInput) -> WellnessPost:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_post não encontrado para este atleta/sessão")
        return wellness


@dataclass
class UpdateWellnessPostInput:
    session_id: uuid.UUID
    athlete_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    perceived_exertion: Optional[int] = None
    enjoyment: Optional[int] = None
    technical_learning: Optional[int] = None
    notes: Optional[str] = None


class UpdateWellnessPostUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, wellness_repo: WellnessPostRepository):
        self._session_repo = session_repo
        self._wellness_repo = wellness_repo

    def execute(self, inp: UpdateWellnessPostInput) -> WellnessPost:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, inp.athlete_id)
        wellness = self._wellness_repo.get_active(inp.session_id, inp.athlete_id)
        if not wellness:
            raise WellnessEntryNotFound("wellness_post não encontrado para este atleta/sessão")
        assert_wellness_post_window(wellness.created_at)
        for field_name in ("perceived_exertion", "enjoyment", "technical_learning", "notes"):
            value = getattr(inp, field_name)
            if value is not None:
                setattr(wellness, field_name, value)
        wellness.updated_at = datetime.now(tz=timezone.utc)
        wellness.validate_invariants()
        return self._wellness_repo.save(wellness)

@dataclass
class ListMesocyclesInput:
    organization_id: Optional[uuid.UUID] = None


class ListMesocyclesUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: ListMesocyclesInput) -> list[Mesocycle]:
        return self._repo.list(organization_id=inp.organization_id)


@dataclass
class GetMesocycleInput:
    id: uuid.UUID


class GetMesocycleUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: GetMesocycleInput) -> Mesocycle:
        meso = self._repo.get_by_id(inp.id)
        if not meso:
            raise MesocycleNotFound(f"Mesociclo {inp.id} não encontrado")
        return meso


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


class UpdateMesocycleUseCase:
    def __init__(self, repo: MesocycleRepository):
        self._repo = repo

    def execute(self, inp: UpdateMesocycleInput) -> Mesocycle:
        meso = self._repo.get_by_id(inp.id)
        if not meso:
            raise MesocycleNotFound(f"Mesociclo {inp.id} não encontrado")
        assert_can_modify_session(inp.actor_role)
        if inp.name is not None:
            meso.name = inp.name
        if inp.started_at is not None:
            meso.started_at = inp.started_at
        if inp.ended_at is not None:
            meso.ended_at = inp.ended_at
        if inp.season_id is not None:
            meso.season_id = inp.season_id
        if inp.team_id is not None:
            meso.team_id = inp.team_id
        if inp.objective is not None:
            meso.objective = inp.objective
        if inp.notes is not None:
            meso.notes = inp.notes
        meso.updated_at = datetime.now(tz=timezone.utc)
        meso.validate_invariants()
        return self._repo.save(meso)


@dataclass
class ListMicrocyclesInput:
    organization_id: Optional[uuid.UUID] = None
    mesocycle_id: Optional[uuid.UUID] = None


class ListMicrocyclesUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: ListMicrocyclesInput) -> list[Microcycle]:
        return self._repo.list(
            organization_id=inp.organization_id,
            mesocycle_id=inp.mesocycle_id,
        )


@dataclass
class GetMicrocycleInput:
    id: uuid.UUID


class GetMicrocycleUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: GetMicrocycleInput) -> Microcycle:
        micro = self._repo.get_by_id(inp.id)
        if not micro:
            raise MicrocycleNotFound(f"Microciclo {inp.id} não encontrado")
        return micro


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


class UpdateMicrocycleUseCase:
    def __init__(self, repo: MicrocycleRepository):
        self._repo = repo

    def execute(self, inp: UpdateMicrocycleInput) -> Microcycle:
        micro = self._repo.get_by_id(inp.id)
        if not micro:
            raise MicrocycleNotFound(f"Microciclo {inp.id} não encontrado")
        assert_can_modify_session(inp.actor_role)
        if inp.week_number is not None:
            micro.week_number = inp.week_number
        if inp.started_at is not None:
            micro.started_at = inp.started_at
        if inp.ended_at is not None:
            micro.ended_at = inp.ended_at
        if inp.team_id is not None:
            micro.team_id = inp.team_id
        if inp.name is not None:
            micro.name = inp.name
        if inp.objective is not None:
            micro.objective = inp.objective
        if inp.planned_sessions_count is not None:
            micro.planned_sessions_count = inp.planned_sessions_count
        if inp.notes is not None:
            micro.notes = inp.notes
        micro.updated_at = datetime.now(tz=timezone.utc)
        micro.validate_invariants()
        return self._repo.save(micro)


@dataclass
class ListExecutionRecordsInput:
    session_id: uuid.UUID


class ListExecutionRecordsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._record_repo = record_repo

    def execute(self, inp: ListExecutionRecordsInput) -> list[ExecutionRecord]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        return self._record_repo.list_by_session(inp.session_id)


@dataclass
class GetExecutionRecordInput:
    session_id: uuid.UUID
    record_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    session_athlete_ids: list[uuid.UUID] = field(default_factory=list)


class GetExecutionRecordUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._record_repo = record_repo

    def execute(self, inp: GetExecutionRecordInput) -> ExecutionRecord:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_read_session(inp.actor_role, inp.actor_id, inp.session_athlete_ids)
        record = self._record_repo.get_by_id(inp.record_id)
        if not record or record.session_id != inp.session_id:
            raise ExecutionRecordNotFound(
                f"Registro de execução {inp.record_id} não encontrado para a sessão {inp.session_id}"
            )
        return record

@dataclass
class ListFeedbackThreadsInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    context_type: Optional[str] = None
    athlete_id: Optional[uuid.UUID] = None


@dataclass
class CreateFeedbackThreadInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    context_type: str
    context_ref_id: uuid.UUID
    conversation_outcome: str
    athlete_id: Optional[uuid.UUID] = None
    content: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    commitment_text: Optional[str] = None
    decision_text: Optional[str] = None


@dataclass
class CloseFeedbackThreadInput:
    session_id: uuid.UUID
    thread_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    resolution_summary: str


def _feedback_context_type(thread: FeedbackThread) -> str:
    if thread.subject in {"SESSION", "BLOCK", "OBJECTIVE", "ATHLETE", "EVIDENCE", "GROUP"}:
        return thread.subject
    if thread.block_id is not None:
        return "BLOCK"
    if thread.objective_id is not None:
        return "OBJECTIVE"
    if thread.athlete_id is not None:
        return "ATHLETE"
    return "SESSION"


def _feedback_context_ref_id(thread: FeedbackThread) -> uuid.UUID:
    context_type = _feedback_context_type(thread)
    if context_type == "BLOCK" and thread.block_id is not None:
        return thread.block_id
    if context_type == "OBJECTIVE" and thread.objective_id is not None:
        return thread.objective_id
    if context_type == "ATHLETE" and thread.athlete_id is not None:
        return thread.athlete_id
    return thread.session_id


class ListFeedbackThreadsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._thread_repo = thread_repo

    def execute(self, inp: ListFeedbackThreadsInput) -> list[FeedbackThread]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        items = self._thread_repo.list_by_session(inp.session_id)
        if inp.context_type:
            items = [item for item in items if _feedback_context_type(item) == inp.context_type]
        if inp.athlete_id:
            items = [item for item in items if item.athlete_id == inp.athlete_id]
        return items


class CreateFeedbackThreadUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._thread_repo = thread_repo

    def execute(self, inp: CreateFeedbackThreadInput) -> FeedbackThread:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)

        context_type = inp.context_type
        athlete_id = inp.athlete_id
        block_id = None
        objective_id = None
        if context_type == "SESSION":
            if inp.context_ref_id != inp.session_id:
                raise ValueError("contextRefId deve apontar para a própria sessão quando contextType=SESSION")
        elif context_type == "BLOCK":
            block_id = inp.context_ref_id
        elif context_type == "OBJECTIVE":
            objective_id = inp.context_ref_id
        elif context_type == "ATHLETE":
            athlete_id = athlete_id or inp.context_ref_id
        elif context_type not in {"EVIDENCE", "GROUP"}:
            raise ValueError(f"contextType inválido: {context_type}")

        now = datetime.now(tz=timezone.utc)
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            block_id=block_id,
            athlete_id=athlete_id,
            objective_id=objective_id,
            created_by_user_id=inp.actor_id,
            subject=context_type,
            body=inp.content,
            conversation_outcome=ConversationOutcome(inp.conversation_outcome),
            follow_up_at=inp.follow_up_at,
            commitment_text=inp.commitment_text,
            decision_text=inp.decision_text,
            created_at=now,
            updated_at=now,
        )
        thread.validate_invariants()
        return self._thread_repo.save(thread)


class CloseFeedbackThreadUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._thread_repo = thread_repo

    def execute(self, inp: CloseFeedbackThreadInput) -> FeedbackThread:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        thread = self._thread_repo.get_by_id(inp.thread_id)
        if not thread or thread.session_id != inp.session_id:
            raise FeedbackThreadNotFound(
                f"Feedback thread {inp.thread_id} não encontrada para a sessão {inp.session_id}"
            )
        if thread.closed_at is not None:
            raise ValueError("Feedback thread já está fechada")
        if inp.actor_id != thread.created_by_user_id and inp.actor_role not in {
            RoleLabel.ADMIN,
            RoleLabel.COORDINATOR,
        }:
            raise InsufficientPrivilege(
                "Somente o criador da thread ou admin/coordinator pode fechá-la"
            )
        thread.closed_at = datetime.now(tz=timezone.utc)
        thread.updated_at = thread.closed_at
        thread.decision_text = inp.resolution_summary
        return self._thread_repo.save(thread)

@dataclass
class ListSessionObjectivesInput:
    session_id: uuid.UUID


class ListSessionObjectivesUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, obj_repo: SessionObjectiveRepository):
        self._session_repo = session_repo
        self._obj_repo = obj_repo

    def execute(self, inp: ListSessionObjectivesInput) -> list[SessionObjective]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        return self._obj_repo.list_by_session(inp.session_id)

@dataclass
class ListAttentionQueueItemsInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    severity: Optional[str] = None
    resolved: bool = False


@dataclass
class ResolveAttentionQueueItemInput:
    session_id: uuid.UUID
    item_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    resolution_evidence: str


@dataclass
class DismissAttentionQueueItemInput:
    session_id: uuid.UUID
    item_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    dismissal_reason: str


@dataclass
class EscalateAttentionQueueItemInput:
    session_id: uuid.UUID
    item_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    escalation_target: str
    escalation_note: str


def _append_note(existing: Optional[str], prefix: str, detail: str) -> str:
    parts = [existing.strip()] if existing and existing.strip() else []
    parts.append(f"{prefix}: {detail}")
    return "\n".join(parts)


class ListAttentionQueueItemsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: ListAttentionQueueItemsInput) -> list[AttentionQueueItem]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        return self._queue_repo.list_by_session(
            session_id=inp.session_id,
            resolved=inp.resolved,
            severity=inp.severity,
        )


class ResolveAttentionQueueItemUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: ResolveAttentionQueueItemInput) -> AttentionQueueItem:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        item = self._queue_repo.get_by_id(inp.item_id)
        if not item or item.session_id != inp.session_id:
            raise AttentionQueueItemNotFound(
                f"Attention queue item {inp.item_id} não encontrado para a sessão {inp.session_id}"
            )
        if item.resolved_at or item.dismissed_at or item.escalated_at:
            raise AttentionQueueConflict("Attention queue item já foi actionado")
        now = datetime.now(tz=timezone.utc)
        item.resolved_at = now
        item.resolved_by = inp.actor_id
        item.updated_at = now
        item.notes = _append_note(item.notes, "RESOLUTION", inp.resolution_evidence)
        return self._queue_repo.save(item)


class DismissAttentionQueueItemUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: DismissAttentionQueueItemInput) -> AttentionQueueItem:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        item = self._queue_repo.get_by_id(inp.item_id)
        if not item or item.session_id != inp.session_id:
            raise AttentionQueueItemNotFound(
                f"Attention queue item {inp.item_id} não encontrado para a sessão {inp.session_id}"
            )
        if item.resolved_at or item.dismissed_at or item.escalated_at:
            raise AttentionQueueConflict("Attention queue item já foi actionado")
        now = datetime.now(tz=timezone.utc)
        item.dismissed_at = now
        item.resolved_by = inp.actor_id
        item.updated_at = now
        item.notes = _append_note(item.notes, "DISMISSAL", inp.dismissal_reason)
        return self._queue_repo.save(item)


class EscalateAttentionQueueItemUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, queue_repo: AttentionQueueRepository):
        self._session_repo = session_repo
        self._queue_repo = queue_repo

    def execute(self, inp: EscalateAttentionQueueItemInput) -> AttentionQueueItem:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        if inp.escalation_target not in {"MEDICAL", "COORDINATOR", "HEAD_COACH"}:
            raise ValueError("escalationTarget inválido")
        item = self._queue_repo.get_by_id(inp.item_id)
        if not item or item.session_id != inp.session_id:
            raise AttentionQueueItemNotFound(
                f"Attention queue item {inp.item_id} não encontrado para a sessão {inp.session_id}"
            )
        if item.resolved_at or item.dismissed_at or item.escalated_at:
            raise AttentionQueueConflict("Attention queue item já foi actionado")
        now = datetime.now(tz=timezone.utc)
        item.escalated_at = now
        item.resolved_by = inp.actor_id
        item.updated_at = now
        item.notes = _append_note(
            item.notes,
            f"ESCALATED[{inp.escalation_target}]",
            inp.escalation_note,
        )
        return self._queue_repo.save(item)


@dataclass
class ListRecommendationsInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    status: Optional[str] = None


@dataclass
class AcceptRecommendationInput:
    session_id: uuid.UUID
    recommendation_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    coach_note: Optional[str] = None


@dataclass
class DismissRecommendationInput:
    session_id: uuid.UUID
    recommendation_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    dismissal_reason: str


class ListRecommendationsUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, recommendation_repo: RecommendationRepository):
        self._session_repo = session_repo
        self._recommendation_repo = recommendation_repo

    def execute(self, inp: ListRecommendationsInput) -> list[Recommendation]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        return self._recommendation_repo.list_by_session(inp.session_id, status=inp.status)


class AcceptRecommendationUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, recommendation_repo: RecommendationRepository):
        self._session_repo = session_repo
        self._recommendation_repo = recommendation_repo

    def execute(self, inp: AcceptRecommendationInput) -> Recommendation:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        recommendation = self._recommendation_repo.get_by_id(inp.recommendation_id)
        if not recommendation or recommendation.session_id != inp.session_id:
            raise RecommendationNotFound(
                f"Recommendation {inp.recommendation_id} não encontrada para a sessão {inp.session_id}"
            )
        if recommendation.status != RecommendationStatus.PENDING:
            raise RecommendationConflict("Recommendation não está em status PENDING")
        now = datetime.now(tz=timezone.utc)
        recommendation.status = RecommendationStatus.ACCEPTED
        recommendation.coach_note = inp.coach_note
        recommendation.dismissal_reason = None
        recommendation.resolved_at = now
        recommendation.resolved_by_user_id = inp.actor_id
        recommendation.updated_at = now
        recommendation.validate_invariants()
        return self._recommendation_repo.save(recommendation)


class DismissRecommendationUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, recommendation_repo: RecommendationRepository):
        self._session_repo = session_repo
        self._recommendation_repo = recommendation_repo

    def execute(self, inp: DismissRecommendationInput) -> Recommendation:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        recommendation = self._recommendation_repo.get_by_id(inp.recommendation_id)
        if not recommendation or recommendation.session_id != inp.session_id:
            raise RecommendationNotFound(
                f"Recommendation {inp.recommendation_id} não encontrada para a sessão {inp.session_id}"
            )
        if recommendation.status != RecommendationStatus.PENDING:
            raise RecommendationConflict("Recommendation não está em status PENDING")
        now = datetime.now(tz=timezone.utc)
        recommendation.status = RecommendationStatus.DISMISSED
        recommendation.dismissal_reason = inp.dismissal_reason
        recommendation.coach_note = None
        recommendation.resolved_at = now
        recommendation.resolved_by_user_id = inp.actor_id
        recommendation.updated_at = now
        recommendation.validate_invariants()
        return self._recommendation_repo.save(recommendation)


@dataclass
class GetIneligibilityStatusInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    athlete_id: Optional[uuid.UUID] = None


@dataclass
class SubmitIneligibilityDeclarationInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    athlete_id: uuid.UUID
    reason_flags: list[str]
    reason_other: Optional[str] = None


class GetIneligibilityStatusUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        ineligibility_repo: AthleteIneligibilityDeclarationRepository,
    ):
        self._session_repo = session_repo
        self._ineligibility_repo = ineligibility_repo

    def execute(self, inp: GetIneligibilityStatusInput) -> AthleteIneligibilityDeclaration:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        target_athlete_id = inp.athlete_id or inp.actor_id
        assert_can_view_athlete_record(inp.actor_role, inp.actor_id, target_athlete_id)
        declaration = self._ineligibility_repo.get_by_session_athlete(inp.session_id, target_athlete_id)
        if not declaration:
            raise IneligibilityDeclarationNotFound(
                f"Declaração de indisponibilidade não encontrada para atleta {target_athlete_id}"
            )
        return declaration


class SubmitIneligibilityDeclarationUseCase:
    def __init__(
        self,
        session_repo: TrainingSessionRepository,
        ineligibility_repo: AthleteIneligibilityDeclarationRepository,
    ):
        self._session_repo = session_repo
        self._ineligibility_repo = ineligibility_repo

    def execute(self, inp: SubmitIneligibilityDeclarationInput) -> AthleteIneligibilityDeclaration:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        if session.status not in {TrainingSessionStatus.PUBLISHED, TrainingSessionStatus.IN_PROGRESS}:
            raise ValueError("Declaração de indisponibilidade só é permitida com sessão PUBLISHED ou IN_PROGRESS")
        if inp.actor_role != RoleLabel.ATHLETE or inp.actor_id != inp.athlete_id:
            raise InsufficientPrivilege("Athlete só pode declarar indisponibilidade para si mesmo")
        now = datetime.now(tz=timezone.utc)
        existing = self._ineligibility_repo.get_by_session_athlete(inp.session_id, inp.athlete_id)
        declaration = AthleteIneligibilityDeclaration(
            id=existing.id if existing else uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            reason_flags=inp.reason_flags,
            reason_other=inp.reason_other,
            acknowledged_by_coach=False,  # Reset coach acknowledgment on resubmission
            coach_note=None,  # Clear coach notes when athlete updates declaration
            declared_at=now,
            created_at=existing.created_at if existing else now,
        )
        declaration.validate_invariants()
        return self._ineligibility_repo.save(declaration)


# ---------------------------------------------------------------------------
# Onda E — Analytics e comunicação
# ---------------------------------------------------------------------------

@dataclass
class GetLoadChartInput:
    session_id: uuid.UUID
    actor_role: RoleLabel


@dataclass
class GetLoadChartResult:
    session: TrainingSession
    load_entries: list[ExecutionRecord]


@dataclass
class ListChatMessagesInput:
    session_id: uuid.UUID
    actor_role: RoleLabel


@dataclass
class SubmitTrainingSuggestionInput:
    session_id: uuid.UUID
    actor_role: RoleLabel
    actor_id: uuid.UUID
    athlete_id: uuid.UUID
    subject: str
    body: str


class GetLoadChartUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, execution_record_repo: ExecutionRecordRepository):
        self._session_repo = session_repo
        self._execution_record_repo = execution_record_repo

    def execute(self, inp: "GetLoadChartInput") -> "GetLoadChartResult":
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        records = self._execution_record_repo.list_by_session(inp.session_id)
        load_entries = [r for r in records if r.execution_type == ExecutionType.LOAD_RECALCULATION]
        return GetLoadChartResult(session=session, load_entries=load_entries)


class ListChatMessagesUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, feedback_thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._feedback_thread_repo = feedback_thread_repo

    def execute(self, inp: "ListChatMessagesInput") -> list[FeedbackThread]:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        assert_can_modify_session(inp.actor_role)
        return self._feedback_thread_repo.list_by_session(inp.session_id)


class SubmitTrainingSuggestionUseCase:
    def __init__(self, session_repo: TrainingSessionRepository, feedback_thread_repo: FeedbackThreadRepository):
        self._session_repo = session_repo
        self._feedback_thread_repo = feedback_thread_repo

    def execute(self, inp: "SubmitTrainingSuggestionInput") -> FeedbackThread:
        session = self._session_repo.get_by_id(inp.session_id)
        if not session:
            raise TrainingSessionNotFound(f"Sessão {inp.session_id} não encontrada")
        if session.status not in {TrainingSessionStatus.PUBLISHED, TrainingSessionStatus.IN_PROGRESS}:
            raise ValueError("Sugestão só pode ser submetida em sessões PUBLISHED ou IN_PROGRESS")
        if inp.actor_role != RoleLabel.ATHLETE or inp.actor_id != inp.athlete_id:
            raise InsufficientPrivilege("Athlete só pode submeter sugestão para si mesmo")
        now = datetime.now(tz=timezone.utc)
        thread = FeedbackThread(
            id=uuid.uuid4(),
            session_id=inp.session_id,
            athlete_id=inp.athlete_id,
            created_by_user_id=inp.actor_id,
            subject=inp.subject,
            body=inp.body,
            conversation_outcome=ConversationOutcome.PENDING_FOLLOWUP,
            created_at=now,
            updated_at=now,
        )
        thread.validate_invariants()
        return self._feedback_thread_repo.save(thread)
