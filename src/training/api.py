from __future__ import annotations

# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases  # noqa: F401
from .generated.infrastructure import repository as _gen_repository  # noqa: F401


"""
Router django-ninja — módulo training.
Implementa endpoints do contrato contracts/openapi/paths/training.yaml.
ADR-007 (JWT), ADR-008 (RBAC), ADR-031 (Django).
OWASP API1/2/3/5 enforcement via domain rules.
"""

import uuid
from datetime import datetime
from typing import Optional

from django.db import DataError, IntegrityError
from ninja import Router
from ninja.errors import HttpError

from .application.use_cases import (
    AddSessionBlockUseCase,
    AddSessionBlockInput,
    AcceptRecommendationInput,
    AcceptRecommendationUseCase,
    CreateExecutionRecordUseCase,
    CreateExecutionRecordInput,
    CreateFeedbackThreadInput,
    CreateFeedbackThreadUseCase,
    CreateMesocycleUseCase,
    CreateMesocycleInput,
    CreateMicrocycleUseCase,
    CreateMicrocycleInput,
    CreateSessionObjectiveUseCase,
    CreateSessionObjectiveInput,
    CreateTrainingSessionUseCase,
    CreateTrainingSessionInput,
    DeleteSessionBlockUseCase,
    DeleteSessionBlockInput,
    DeleteTrainingSessionUseCase,
    DeleteTrainingSessionInput,
    DismissAttentionQueueItemInput,
    DismissAttentionQueueItemUseCase,
    DismissRecommendationInput,
    DismissRecommendationUseCase,
    EscalateAttentionQueueItemInput,
    EscalateAttentionQueueItemUseCase,
    GetIneligibilityStatusInput,
    GetIneligibilityStatusUseCase,
    GetExecutionRecordInput,
    GetExecutionRecordUseCase,
    GetMesocycleInput,
    GetMesocycleUseCase,
    GetMicrocycleInput,
    GetMicrocycleUseCase,
    GetWellnessPostInput,
    GetWellnessPostUseCase,
    GetWellnessPreInput,
    GetWellnessPreUseCase,
    GetSessionBlockUseCase,
    GetSessionBlockInput,
    GetTrainingSessionUseCase,
    GetTrainingSessionInput,
    ListAttentionQueueItemsInput,
    ListAttentionQueueItemsUseCase,
    ListExecutionRecordsInput,
    ListExecutionRecordsUseCase,
    ListFeedbackThreadsInput,
    ListFeedbackThreadsUseCase,
    ListMesocyclesInput,
    ListMesocyclesUseCase,
    ListMicrocyclesInput,
    ListMicrocyclesUseCase,
    ListRecommendationsInput,
    ListRecommendationsUseCase,
    ListSessionAttendanceInput,
    ListSessionAttendanceUseCase,
    ListSessionBlocksUseCase,
    ListSessionBlocksInput,
    ListSessionObjectivesInput,
    ListSessionObjectivesUseCase,
    ListTrainingSessionsUseCase,
    ListTrainingSessionsInput,
    ResolveAttentionQueueItemInput,
    ResolveAttentionQueueItemUseCase,
    RecordSessionAttendanceInput,
    RecordSessionAttendanceUseCase,
    ReorderSessionBlocksUseCase,
    ReorderSessionBlocksInput,
    CloseFeedbackThreadInput,
    CloseFeedbackThreadUseCase,
    GetLoadChartInput,
    GetLoadChartUseCase,
    ListChatMessagesInput,
    ListChatMessagesUseCase,
    SubmitIneligibilityDeclarationInput,
    SubmitIneligibilityDeclarationUseCase,
    SubmitTrainingSuggestionInput,
    SubmitTrainingSuggestionUseCase,
    SubmitWellnessPostUseCase,
    SubmitWellnessPostInput,
    SubmitWellnessPreUseCase,
    SubmitWellnessPreInput,
    TransitionTrainingSessionUseCase,
    TransitionTrainingSessionInput,
    UpdateMesocycleInput,
    UpdateMesocycleUseCase,
    UpdateMicrocycleInput,
    UpdateMicrocycleUseCase,
    UpdateWellnessPostInput,
    UpdateWellnessPostUseCase,
    UpdateWellnessPreInput,
    UpdateWellnessPreUseCase,
    UpdateSessionBlockUseCase,
    UpdateSessionBlockInput,
    UpdateTrainingSessionUseCase,
    UpdateTrainingSessionInput,
)
from .domain.entities import TrainingSessionStatus
from .domain.rules import (
    AttentionQueueConflict,
    AttentionQueueItemNotFound,
    DuplicateWellnessEntry,
    ElasticSumRuleViolation,
    ExecutionRecordNotFound,
    FeedbackThreadNotFound,
    IneligibilityDeclarationNotFound,
    InsufficientPrivilege,
    InvalidStatusTransition,
    MesocycleNotFound,
    MicrocycleNotFound,
    RecommendationConflict,
    RecommendationNotFound,
    RoleLabel,
    SessionBlockNotFound,
    SessionNotMutable,
    TrainingSessionNotFound,
    WellnessEntryNotFound,
    WellnessWindowClosed,
)
from .infrastructure.repository import (
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
from .schemas import (
    AddSessionBlockIn,
    AcceptRecommendationIn,
    AttendanceListOut,
    AttendanceRecordOut,
    AttentionQueueItemOut,
    AttentionQueueListOut,
    AthleteIneligibilityDeclarationOut,
    CloseFeedbackThreadIn,
    CreateExecutionRecordIn,
    CreateFeedbackThreadIn,
    CreateMesocycleIn,
    CreateMicrocycleIn,
    CreateSessionObjectiveIn,
    CreateTrainingSessionIn,
    DismissAttentionQueueItemIn,
    DismissRecommendationIn,
    EscalateAttentionQueueItemIn,
    ErrorOut,
    ExecutionRecordListOut,
    ExecutionRecordOut,
    FeedbackThreadListOut,
    FeedbackThreadOut,
    LoadChartOut,
    LoadChartEntryOut,
    MesocycleListOut,
    MesocycleOut,
    MicrocycleListOut,
    MicrocycleOut,
    ReorderSessionBlocksIn,
    RecordSessionAttendanceIn,
    RecommendationListOut,
    RecommendationOut,
    ResolveAttentionQueueItemIn,
    SessionBlockListOut,
    SessionBlockOut,
    SessionObjectiveListOut,
    SessionObjectiveOut,
    SubmitIneligibilityDeclarationIn,
    SubmitTrainingSuggestionIn,
    SubmitWellnessPostIn,
    SubmitWellnessPreIn,
    TransitionOut,
    TrainingSessionListOut,
    TrainingSessionOut,
    UpdateMesocycleIn,
    UpdateMicrocycleIn,
    UpdateWellnessPostIn,
    UpdateWellnessPreIn,
    UpdateSessionBlockIn,
    UpdateTrainingSessionIn,
    WellnessPostOut,
    WellnessPreOut,
)

router = Router(tags=["training"])

# ---------------------------------------------------------------------------
# Auth stubs — substituir por integração real com identity_access
# ---------------------------------------------------------------------------

def _get_actor_role(request) -> RoleLabel:
    """Extrai RoleLabel do JWT validado."""
    role = getattr(request, "_actor_role", None)
    if role:
        try:
            return RoleLabel(role)
        except ValueError:
            return RoleLabel.MEMBER
    raise HttpError(401, "Unauthenticated")

def _get_actor_id(request) -> uuid.UUID:
    actor_id = getattr(request, "_actor_id", None)
    if actor_id:
        return uuid.UUID(str(actor_id))
    raise HttpError(401, "Unauthenticated")

# ---------------------------------------------------------------------------
# Helpers de conversão
# ---------------------------------------------------------------------------

def _session_to_out(s) -> TrainingSessionOut:
    return TrainingSessionOut(
        id=s.id,
        organization_id=s.organization_id,
        session_at=s.session_at,
        session_type=s.session_type,
        status=s.status.value,
        created_by_user_id=s.created_by_user_id,
        created_at=s.created_at,
        updated_at=s.updated_at,
        team_id=s.team_id,
        season_id=s.season_id,
        microcycle_id=s.microcycle_id,
        duration_planned_minutes=s.duration_planned_minutes,
        location=s.location,
        main_objective=s.main_objective,
        secondary_objective=s.secondary_objective,
        planned_load=s.planned_load,
        intensity_target=s.intensity_target,
        session_block=s.session_block,
        notes=s.notes,
        group_climate=s.group_climate,
        standalone=s.standalone,
        individualization_mode=s.individualization_mode,
        focus_attack_positional_pct=s.focus_attack_positional_pct,
        focus_defense_positional_pct=s.focus_defense_positional_pct,
        focus_transition_offense_pct=s.focus_transition_offense_pct,
        focus_transition_defense_pct=s.focus_transition_defense_pct,
        focus_attack_technical_pct=s.focus_attack_technical_pct,
        focus_defense_technical_pct=s.focus_defense_technical_pct,
        focus_physical_pct=s.focus_physical_pct,
        phase_focus_defense=s.phase_focus_defense,
        phase_focus_attack=s.phase_focus_attack,
        phase_focus_transition_offense=s.phase_focus_transition_offense,
        phase_focus_transition_defense=s.phase_focus_transition_defense,
    )

def _block_to_out(b) -> SessionBlockOut:
    return SessionBlockOut(
        id=b.id,
        session_id=b.session_id,
        phase=b.phase.value,
        order_index=b.order_index,
        duration_minutes=b.duration_minutes,
        block_objective=b.block_objective,
        intensity=b.intensity.value,
        is_optional=b.is_optional,
        exercise_id=b.exercise_id,
        exercise_version_id=b.exercise_version_id,
        notes=b.notes,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


def _attendance_to_out(attendance) -> AttendanceRecordOut:
    return AttendanceRecordOut(
        athlete_id=attendance.athlete_id,
        status=attendance.status.value,
        recorded_at=attendance.recorded_at,
        source=attendance.source.value,
        correction_by_user_id=attendance.correction_by_user_id,
        correction_at=attendance.correction_at,
        justification_reason=attendance.justification_reason,
    )


def _wellness_pre_to_out(wellness) -> WellnessPreOut:
    return WellnessPreOut(
        id=wellness.id,
        session_id=wellness.session_id,
        athlete_id=wellness.athlete_id,
        readiness=wellness.readiness,
        sleep_quality=wellness.sleep_quality,
        mood=wellness.mood,
        fatigue=wellness.fatigue,
        muscle_soreness=wellness.muscle_soreness,
        notes=wellness.notes,
        created_at=wellness.created_at,
        updated_at=wellness.updated_at,
    )


def _wellness_post_to_out(wellness) -> WellnessPostOut:
    return WellnessPostOut(
        id=wellness.id,
        session_id=wellness.session_id,
        athlete_id=wellness.athlete_id,
        perceived_exertion=wellness.perceived_exertion,
        enjoyment=wellness.enjoyment,
        technical_learning=wellness.technical_learning,
        notes=wellness.notes,
        created_at=wellness.created_at,
        updated_at=wellness.updated_at,
    )


def _execution_record_to_out(record) -> ExecutionRecordOut:
    return ExecutionRecordOut(
        id=record.id,
        session_id=record.session_id,
        execution_type=record.execution_type.value,
        recorded_at=record.recorded_at,
        created_by_user_id=record.created_by_user_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        block_id=record.block_id,
        planned_value=record.planned_value,
        actual_value=record.actual_value,
        planned_unit=record.planned_unit,
        actual_unit=record.actual_unit,
        adjustment_reason_type=record.adjustment_reason_type,
        coach_rationale=record.coach_rationale,
        notes=record.notes,
    )


def _session_objective_to_out(obj) -> SessionObjectiveOut:
    return SessionObjectiveOut(
        id=obj.id,
        session_id=obj.session_id,
        origin=obj.origin.value,
        objective_type=obj.objective_type,
        description=obj.description,
        origin_notes=obj.origin_notes,
        priority=obj.priority,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def _mesocycle_to_out(meso) -> MesocycleOut:
    return MesocycleOut(
        id=meso.id,
        organization_id=meso.organization_id,
        name=meso.name,
        started_at=meso.started_at,
        ended_at=meso.ended_at,
        created_at=meso.created_at,
        updated_at=meso.updated_at,
        season_id=meso.season_id,
        team_id=meso.team_id,
        objective=meso.objective,
        notes=meso.notes,
    )


def _microcycle_to_out(micro) -> MicrocycleOut:
    return MicrocycleOut(
        id=micro.id,
        organization_id=micro.organization_id,
        mesocycle_id=micro.mesocycle_id,
        week_number=micro.week_number,
        started_at=micro.started_at,
        ended_at=micro.ended_at,
        created_at=micro.created_at,
        updated_at=micro.updated_at,
        team_id=micro.team_id,
        name=micro.name,
        objective=micro.objective,
        planned_sessions_count=micro.planned_sessions_count,
        notes=micro.notes,
    )


def _feedback_context_type(thread) -> str:
    if thread.subject in {"SESSION", "BLOCK", "OBJECTIVE", "ATHLETE", "EVIDENCE", "GROUP"}:
        return thread.subject
    if thread.block_id is not None:
        return "BLOCK"
    if thread.objective_id is not None:
        return "OBJECTIVE"
    if thread.athlete_id is not None:
        return "ATHLETE"
    return "SESSION"


def _feedback_context_ref_id(thread) -> uuid.UUID:
    context_type = _feedback_context_type(thread)
    if context_type == "BLOCK" and thread.block_id is not None:
        return thread.block_id
    if context_type == "OBJECTIVE" and thread.objective_id is not None:
        return thread.objective_id
    if context_type == "ATHLETE" and thread.athlete_id is not None:
        return thread.athlete_id
    return thread.session_id


def _feedback_thread_to_out(thread) -> FeedbackThreadOut:
    return FeedbackThreadOut(
        id=thread.id,
        session_id=thread.session_id,
        context_type=_feedback_context_type(thread),
        context_ref_id=_feedback_context_ref_id(thread),
        conversation_outcome=thread.conversation_outcome.value,
        created_by_user_id=thread.created_by_user_id,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        athlete_id=thread.athlete_id,
        content=thread.body,
        follow_up_at=thread.follow_up_at,
        commitment_text=thread.commitment_text,
        decision_text=thread.decision_text,
    )


def _attention_queue_item_to_out(item) -> AttentionQueueItemOut:
    resolved_at = item.resolved_at or item.dismissed_at or item.escalated_at
    return AttentionQueueItemOut(
        id=item.id,
        session_id=item.session_id,
        severity=item.severity,
        reason_code=item.reason,
        target_entity_type="athlete",
        target_entity_id=item.athlete_id,
        message=item.notes or item.reason,
        created_at=item.created_at,
        resolved_at=resolved_at,
        resolved_by_user_id=item.resolved_by,
    )


def _recommendation_to_out(recommendation) -> RecommendationOut:
    return RecommendationOut(
        id=recommendation.id,
        session_id=recommendation.session_id,
        generated_by_rule=recommendation.generated_by_rule,
        action_type=recommendation.action_type.value,
        description=recommendation.description,
        status=recommendation.status.value,
        generated_by_module=recommendation.generated_by_module,
        created_at=recommendation.created_at,
        updated_at=recommendation.updated_at,
        priority=recommendation.priority.value if recommendation.priority else None,
        coach_note=recommendation.coach_note,
        dismissal_reason=recommendation.dismissal_reason,
        resolved_at=recommendation.resolved_at,
        resolved_by_user_id=recommendation.resolved_by_user_id,
    )


def _ineligibility_to_out(declaration) -> AthleteIneligibilityDeclarationOut:
    return AthleteIneligibilityDeclarationOut(
        id=declaration.id,
        session_id=declaration.session_id,
        athlete_id=declaration.athlete_id,
        reason_flags=declaration.reason_flags,
        reason_other=declaration.reason_other,
        acknowledged_by_coach=declaration.acknowledged_by_coach,
        coach_note=declaration.coach_note,
        declared_at=declaration.declared_at,
        created_at=declaration.created_at,
    )

# ---------------------------------------------------------------------------
# GET /training-sessions — listTrainingSessions
# ---------------------------------------------------------------------------

@router.get("/training-sessions", response={200: TrainingSessionListOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut})
def list_training_sessions(
    request,
    organization_id: Optional[uuid.UUID] = None,
    team_id: Optional[uuid.UUID] = None,
    season_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    page_size: int = 20,
    page_token: Optional[str] = None,
):
    repo = TrainingSessionRepository()
    actor_role = _get_actor_role(request)
    actor_id = _get_actor_id(request)
    try:
        result = ListTrainingSessionsUseCase(repo).execute(
            ListTrainingSessionsInput(
                actor_role=actor_role,
                actor_id=actor_id,
                organization_id=organization_id,
                team_id=team_id,
                season_id=season_id,
                status=status,
                page_size=min(max(page_size, 1), 100),
                page_token=page_token,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, TrainingSessionListOut(
        items=[_session_to_out(s) for s in result.items],
        next_page_token=result.next_page_token,
    )

# ---------------------------------------------------------------------------
# POST /training-sessions — createTrainingSession
# ---------------------------------------------------------------------------

@router.post(
    "/training-sessions",
    response={201: TrainingSessionOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 422: ErrorOut},
)
def create_training_session(request, body: CreateTrainingSessionIn):
    repo = TrainingSessionRepository()
    actor_role = _get_actor_role(request)
    actor_id = _get_actor_id(request)
    try:
        session = CreateTrainingSessionUseCase(repo).execute(
            CreateTrainingSessionInput(
                actor_role=actor_role,
                actor_id=actor_id,
                organization_id=body.organization_id,
                session_at=body.session_at,
                session_type=body.session_type,
                team_id=body.team_id,
                season_id=body.season_id,
                microcycle_id=body.microcycle_id,
                duration_planned_minutes=body.duration_planned_minutes,
                location=body.location,
                main_objective=body.main_objective,
                secondary_objective=body.secondary_objective,
                planned_load=body.planned_load,
                intensity_target=body.intensity_target,
                session_block=body.session_block,
                standalone=body.standalone,
                focus_attack_positional_pct=body.focus_attack_positional_pct,
                focus_defense_positional_pct=body.focus_defense_positional_pct,
                focus_transition_offense_pct=body.focus_transition_offense_pct,
                focus_transition_defense_pct=body.focus_transition_defense_pct,
                focus_attack_technical_pct=body.focus_attack_technical_pct,
                focus_defense_technical_pct=body.focus_defense_technical_pct,
                focus_physical_pct=body.focus_physical_pct,
                phase_focus_defense=body.phase_focus_defense,
                phase_focus_attack=body.phase_focus_attack,
                phase_focus_transition_offense=body.phase_focus_transition_offense,
                phase_focus_transition_defense=body.phase_focus_transition_defense,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(422, str(exc))
    except (IntegrityError, DataError) as exc:
        raise HttpError(422, f"Dados inválidos: violação de restrição do banco — {exc}")
    return 201, _session_to_out(session)

# ---------------------------------------------------------------------------
# GET /training-sessions/{id} — getTrainingSessionById
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions/{id}",
    response={200: TrainingSessionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def get_training_session(request, id: uuid.UUID):
    repo = TrainingSessionRepository()
    try:
        session = GetTrainingSessionUseCase(repo).execute(
            GetTrainingSessionInput(
                id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, _session_to_out(session)

# ---------------------------------------------------------------------------
# Session state transitions
# ---------------------------------------------------------------------------

def _do_transition(request, id: uuid.UUID, target_status: TrainingSessionStatus):
    repo = TrainingSessionRepository()
    try:
        session = TransitionTrainingSessionUseCase(repo).execute(
            TransitionTrainingSessionInput(
                id=id,
                target_status=target_status,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except InvalidStatusTransition as exc:
        raise HttpError(422, str(exc))
    return TransitionOut(id=session.id, status=session.status.value, updated_at=session.updated_at)

@router.post("/training-sessions/{id}/publish", response={200: TransitionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def publish_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.PUBLISHED)

@router.post("/training-sessions/{id}/unpublish", response={200: TransitionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def unpublish_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.SCHEDULED)

@router.post("/training-sessions/{id}/start", response={200: TransitionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def start_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.IN_PROGRESS)

@router.post("/training-sessions/{id}/complete", response={200: TransitionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def complete_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.COMPLETED)

@router.post("/training-sessions/{id}/cancel", response={200: TransitionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def cancel_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.CANCELLED)

@router.post("/training-sessions/{id}/archive", response={200: TransitionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def archive_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.ARCHIVED)

# ---------------------------------------------------------------------------
# Session Blocks
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions/{id}/blocks",
    response={200: SessionBlockListOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def list_session_blocks(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    block_repo = SessionBlockRepository()
    try:
        blocks = ListSessionBlocksUseCase(session_repo, block_repo).execute(
            ListSessionBlocksInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, SessionBlockListOut(data=[_block_to_out(b) for b in blocks])

@router.post(
    "/training-sessions/{id}/blocks",
    response={201: SessionBlockOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut, 409: ErrorOut},
)
def add_session_block(request, id: uuid.UUID, body: AddSessionBlockIn):
    session_repo = TrainingSessionRepository()
    block_repo = SessionBlockRepository()
    try:
        block = AddSessionBlockUseCase(session_repo, block_repo).execute(
            AddSessionBlockInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                phase=body.phase,
                order_index=body.order_index,
                duration_minutes=body.duration_minutes,
                block_objective=body.block_objective,
                intensity=body.intensity,
                is_optional=body.is_optional,
                exercise_id=body.exercise_id,
                exercise_version_id=body.exercise_version_id,
                notes=body.notes,
            )
        )
    except (TrainingSessionNotFound,) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ElasticSumRuleViolation as exc:
        raise HttpError(422, str(exc))
    except SessionNotMutable as exc:
        raise HttpError(422, str(exc))
    except ValueError as exc:
        raise HttpError(422, str(exc))
    return 201, _block_to_out(block)

@router.get(
    "/training-sessions/{id}/blocks/{block_id}",
    response={200: SessionBlockOut, 403: ErrorOut, 404: ErrorOut},
)
def get_session_block(request, id: uuid.UUID, block_id: uuid.UUID):
    block_repo = SessionBlockRepository()
    block = block_repo.get_by_id(block_id)
    if not block or block.session_id != id:
        raise HttpError(404, "Bloco não encontrado")
    return 200, _block_to_out(block)

@router.patch(
    "/training-sessions/{id}/blocks/{block_id}",
    response={200: SessionBlockOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
def update_session_block(request, id: uuid.UUID, block_id: uuid.UUID, body: UpdateSessionBlockIn):
    session_repo = TrainingSessionRepository()
    block_repo = SessionBlockRepository()
    try:
        block = UpdateSessionBlockUseCase(session_repo, block_repo).execute(
            UpdateSessionBlockInput(
                session_id=id,
                block_id=block_id,
                actor_role=_get_actor_role(request),
                duration_minutes=body.duration_minutes,
                block_objective=body.block_objective,
                intensity=body.intensity,
                phase=body.phase,
                is_optional=body.is_optional,
                notes=body.notes,
                exercise_id=body.exercise_id,
                exercise_version_id=body.exercise_version_id,
            )
        )
    except (TrainingSessionNotFound, SessionBlockNotFound) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (ElasticSumRuleViolation, SessionNotMutable, ValueError) as exc:
        raise HttpError(422, str(exc))
    return 200, _block_to_out(block)

@router.delete(
    "/training-sessions/{id}/blocks/{block_id}",
    response={204: None, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
def delete_session_block(request, id: uuid.UUID, block_id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    block_repo = SessionBlockRepository()
    try:
        DeleteSessionBlockUseCase(session_repo, block_repo).execute(
            DeleteSessionBlockInput(
                session_id=id,
                block_id=block_id,
                actor_role=_get_actor_role(request),
            )
        )
    except (TrainingSessionNotFound, SessionBlockNotFound) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except SessionNotMutable as exc:
        raise HttpError(422, str(exc))
    return 204, None

# ---------------------------------------------------------------------------
# Wellness Pre
# ---------------------------------------------------------------------------

@router.post(
    "/training-sessions/{id}/wellness-pre",
    response={201: WellnessPreOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def submit_wellness_pre(request, id: uuid.UUID, body: SubmitWellnessPreIn):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPreRepository()
    try:
        wellness = SubmitWellnessPreUseCase(session_repo, wellness_repo).execute(
            SubmitWellnessPreInput(
                session_id=id,
                athlete_id=body.athlete_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                readiness=body.readiness,
                sleep_quality=body.sleep_quality,
                mood=body.mood,
                fatigue=body.fatigue,
                muscle_soreness=body.muscle_soreness,
                notes=body.notes,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except WellnessWindowClosed as exc:
        raise HttpError(400, str(exc))
    except DuplicateWellnessEntry as exc:
        raise HttpError(409, str(exc))
    return 201, WellnessPreOut(
        id=wellness.id,
        session_id=wellness.session_id,
        athlete_id=wellness.athlete_id,
        readiness=wellness.readiness,
        sleep_quality=wellness.sleep_quality,
        mood=wellness.mood,
        fatigue=wellness.fatigue,
        muscle_soreness=wellness.muscle_soreness,
        notes=wellness.notes,
        created_at=wellness.created_at,
        updated_at=wellness.updated_at,
    )

# ---------------------------------------------------------------------------
# Wellness Post
# ---------------------------------------------------------------------------

@router.post(
    "/training-sessions/{id}/wellness-post",
    response={201: WellnessPostOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def submit_wellness_post(request, id: uuid.UUID, body: SubmitWellnessPostIn):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPostRepository()
    try:
        wellness = SubmitWellnessPostUseCase(session_repo, wellness_repo).execute(
            SubmitWellnessPostInput(
                session_id=id,
                athlete_id=body.athlete_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                perceived_exertion=body.perceived_exertion,
                enjoyment=body.enjoyment,
                technical_learning=body.technical_learning,
                notes=body.notes,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (DuplicateWellnessEntry,) as exc:
        raise HttpError(409, str(exc))
    return 201, WellnessPostOut(
        id=wellness.id,
        session_id=wellness.session_id,
        athlete_id=wellness.athlete_id,
        perceived_exertion=wellness.perceived_exertion,
        enjoyment=wellness.enjoyment,
        technical_learning=wellness.technical_learning,
        notes=wellness.notes,
        created_at=wellness.created_at,
        updated_at=wellness.updated_at,
    )

# ---------------------------------------------------------------------------
# Execution Records
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions/{id}/execution-records",
    response={200: ExecutionRecordListOut, 403: ErrorOut, 404: ErrorOut},
)
def list_execution_records(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    record_repo = ExecutionRecordRepository()
    try:
        records = ListExecutionRecordsUseCase(session_repo, record_repo).execute(
            ListExecutionRecordsInput(session_id=id)
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, ExecutionRecordListOut(data=[_execution_record_to_out(r) for r in records])

@router.post(
    "/training-sessions/{id}/execution-records",
    response={201: ExecutionRecordOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
def create_execution_record(request, id: uuid.UUID, body: CreateExecutionRecordIn):
    session_repo = TrainingSessionRepository()
    record_repo = ExecutionRecordRepository()
    try:
        record = CreateExecutionRecordUseCase(session_repo, record_repo).execute(
            CreateExecutionRecordInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                execution_type=body.execution_type,
                recorded_at=body.recorded_at,
                block_id=body.block_id,
                planned_value=body.planned_value,
                actual_value=body.actual_value,
                planned_unit=body.planned_unit,
                actual_unit=body.actual_unit,
                adjustment_reason_type=body.adjustment_reason_type,
                coach_rationale=body.coach_rationale,
                notes=body.notes,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(422, str(exc))
    return 201, ExecutionRecordOut(
        id=record.id,
        session_id=record.session_id,
        execution_type=record.execution_type.value,
        recorded_at=record.recorded_at,
        created_by_user_id=record.created_by_user_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        block_id=record.block_id,
        planned_value=record.planned_value,
        actual_value=record.actual_value,
        planned_unit=record.planned_unit,
        actual_unit=record.actual_unit,
        adjustment_reason_type=record.adjustment_reason_type,
        coach_rationale=record.coach_rationale,
        notes=record.notes,
    )

# ---------------------------------------------------------------------------
# Session Objectives
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions/{id}/objectives",
    response={200: SessionObjectiveListOut, 403: ErrorOut, 404: ErrorOut},
)
def list_session_objectives(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    obj_repo = SessionObjectiveRepository()
    try:
        objs = ListSessionObjectivesUseCase(session_repo, obj_repo).execute(
            ListSessionObjectivesInput(session_id=id)
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, SessionObjectiveListOut(
        data=[_session_objective_to_out(o) for o in objs]
    )

@router.post(
    "/training-sessions/{id}/objectives",
    response={201: SessionObjectiveOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
def create_session_objective(request, id: uuid.UUID, body: CreateSessionObjectiveIn):
    session_repo = TrainingSessionRepository()
    obj_repo = SessionObjectiveRepository()
    try:
        obj = CreateSessionObjectiveUseCase(session_repo, obj_repo).execute(
            CreateSessionObjectiveInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                origin=body.origin,
                objective_type=body.objective_type,
                description=body.description,
                origin_notes=body.origin_notes,
                priority=body.priority,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(422, str(exc))
    return 201, _session_objective_to_out(obj)

# ---------------------------------------------------------------------------
# Mesocycles
# ---------------------------------------------------------------------------

@router.get("/mesocycles", response={200: MesocycleListOut, 403: ErrorOut})
def list_mesocycles(request, organization_id: Optional[uuid.UUID] = None):
    repo = MesocycleRepository()
    items = ListMesocyclesUseCase(repo).execute(
        ListMesocyclesInput(organization_id=organization_id)
    )
    return 200, MesocycleListOut(items=[_mesocycle_to_out(m) for m in items])

@router.post("/mesocycles", response={201: MesocycleOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})
def create_mesocycle(request, body: CreateMesocycleIn):
    repo = MesocycleRepository()
    try:
        meso = CreateMesocycleUseCase(repo).execute(
            CreateMesocycleInput(
                actor_role=_get_actor_role(request),
                organization_id=body.organization_id,
                name=body.name,
                started_at=body.started_at,
                ended_at=body.ended_at,
                season_id=body.season_id,
                team_id=body.team_id,
                objective=body.objective,
                notes=body.notes,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(422, str(exc))
    except (IntegrityError, DataError) as exc:
        raise HttpError(422, f"Dados inválidos: violação de restrição do banco — {exc}")
    return 201, _mesocycle_to_out(meso)

@router.get("/mesocycles/{id}", response={200: MesocycleOut, 404: ErrorOut})
def get_mesocycle(request, id: uuid.UUID):
    repo = MesocycleRepository()
    try:
        meso = GetMesocycleUseCase(repo).execute(GetMesocycleInput(id=id))
    except MesocycleNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, _mesocycle_to_out(meso)

# ---------------------------------------------------------------------------
# Microcycles
# ---------------------------------------------------------------------------

@router.get("/microcycles", response={200: MicrocycleListOut, 403: ErrorOut})
def list_microcycles(
    request,
    organization_id: Optional[uuid.UUID] = None,
    mesocycle_id: Optional[uuid.UUID] = None,
):
    repo = MicrocycleRepository()
    items = ListMicrocyclesUseCase(repo).execute(
        ListMicrocyclesInput(
            organization_id=organization_id,
            mesocycle_id=mesocycle_id,
        )
    )
    return 200, MicrocycleListOut(items=[_microcycle_to_out(m) for m in items])

@router.post("/microcycles", response={201: MicrocycleOut, 401: ErrorOut, 403: ErrorOut, 422: ErrorOut})
def create_microcycle(request, body: CreateMicrocycleIn):
    repo = MicrocycleRepository()
    try:
        micro = CreateMicrocycleUseCase(repo).execute(
            CreateMicrocycleInput(
                actor_role=_get_actor_role(request),
                organization_id=body.organization_id,
                mesocycle_id=body.mesocycle_id,
                week_number=body.week_number,
                started_at=body.started_at,
                ended_at=body.ended_at,
                team_id=body.team_id,
                name=body.name,
                objective=body.objective,
                planned_sessions_count=body.planned_sessions_count,
                notes=body.notes,
            )
        )
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(422, str(exc))
    except IntegrityError as exc:
        raise HttpError(422, f"Dados inválidos: violação de restrição do banco — {exc}")
    except Exception as exc:
        # Captura DataError (smallint out of range) e outros erros de DB não mapeados
        from django.db.utils import DataError
        if isinstance(exc, DataError):
            raise HttpError(422, f"Valor fora do intervalo permitido — {exc}")
        raise
    return 201, _microcycle_to_out(micro)

@router.get("/microcycles/{id}", response={200: MicrocycleOut, 404: ErrorOut})
def get_microcycle(request, id: uuid.UUID):
    repo = MicrocycleRepository()
    try:
        micro = GetMicrocycleUseCase(repo).execute(GetMicrocycleInput(id=id))
    except MicrocycleNotFound as exc:
        raise HttpError(404, str(exc))
    return 200, _microcycle_to_out(micro)

# ---------------------------------------------------------------------------
# Stubs de contrato — B10-001 source graph integrity
# Implementação pendente (known_gaps). raise NotImplementedError até fase de implementação.
# ---------------------------------------------------------------------------

@router.patch(
    "/training-sessions/{id}",
    response={200: TrainingSessionOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
def update_training_session(request, id: uuid.UUID, body: UpdateTrainingSessionIn):
    repo = TrainingSessionRepository()
    try:
        session = UpdateTrainingSessionUseCase(repo).execute(
            UpdateTrainingSessionInput(
                id=id,
                actor_role=_get_actor_role(request),
                session_at=body.session_at,
                session_type=body.session_type,
                duration_planned_minutes=body.duration_planned_minutes,
                location=body.location,
                main_objective=body.main_objective,
                secondary_objective=body.secondary_objective,
                planned_load=body.planned_load,
                intensity_target=body.intensity_target,
                session_block=body.session_block,
                standalone=body.standalone,
                notes=body.notes,
                focus_attack_positional_pct=body.focus_attack_positional_pct,
                focus_defense_positional_pct=body.focus_defense_positional_pct,
                focus_transition_offense_pct=body.focus_transition_offense_pct,
                focus_transition_defense_pct=body.focus_transition_defense_pct,
                focus_attack_technical_pct=body.focus_attack_technical_pct,
                focus_defense_technical_pct=body.focus_defense_technical_pct,
                focus_physical_pct=body.focus_physical_pct,
                phase_focus_defense=body.phase_focus_defense,
                phase_focus_attack=body.phase_focus_attack,
                phase_focus_transition_offense=body.phase_focus_transition_offense,
                phase_focus_transition_defense=body.phase_focus_transition_defense,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (SessionNotMutable, ValueError) as exc:
        raise HttpError(422, str(exc))
    return 200, _session_to_out(session)


@router.delete(
    "/training-sessions/{id}",
    response={204: None, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
def delete_training_session(request, id: uuid.UUID, deleted_reason: str = ""):
    repo = TrainingSessionRepository()
    try:
        DeleteTrainingSessionUseCase(repo).execute(
            DeleteTrainingSessionInput(
                id=id,
                actor_role=_get_actor_role(request),
                deleted_reason=deleted_reason,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 204, None


@router.post(
    "/training-sessions/{id}/blocks/reorder",
    response={200: SessionBlockListOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
def reorder_session_blocks(request, id: uuid.UUID, body: ReorderSessionBlocksIn):
    session_repo = TrainingSessionRepository()
    block_repo = SessionBlockRepository()
    try:
        blocks = ReorderSessionBlocksUseCase(session_repo, block_repo).execute(
            ReorderSessionBlocksInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                block_ids=body.block_ids,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (SessionNotMutable, ValueError) as exc:
        raise HttpError(422, str(exc))
    return 200, SessionBlockListOut(data=[_block_to_out(b) for b in blocks])

@router.get(
    "/training-sessions/{id}/attendance",
    response={200: AttendanceListOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def list_session_attendance(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    attendance_repo = AttendanceRepository()
    try:
        records = ListSessionAttendanceUseCase(session_repo, attendance_repo).execute(
            ListSessionAttendanceInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, AttendanceListOut(items=[_attendance_to_out(record) for record in records])


@router.post(
    "/training-sessions/{id}/attendance",
    response={201: AttendanceRecordOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def record_session_attendance(request, id: uuid.UUID, body: RecordSessionAttendanceIn):
    session_repo = TrainingSessionRepository()
    attendance_repo = AttendanceRepository()
    try:
        record = RecordSessionAttendanceUseCase(session_repo, attendance_repo).execute(
            RecordSessionAttendanceInput(
                session_id=id,
                athlete_id=body.athlete_id,
                status=body.status,
                source=body.source,
                correction_by_user_id=body.correction_by_user_id,
                correction_at=body.correction_at,
                justification_reason=body.justification_reason,
                observed_at=body.observed_at,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return 201, _attendance_to_out(record)


@router.get(
    "/training-sessions/{id}/wellness-pre/{athleteId}",
    response={200: WellnessPreOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def get_wellness_pre(request, id: uuid.UUID, athleteId: uuid.UUID):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPreRepository()
    try:
        wellness = GetWellnessPreUseCase(session_repo, wellness_repo).execute(
            GetWellnessPreInput(
                session_id=id,
                athlete_id=athleteId,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except (TrainingSessionNotFound, WellnessEntryNotFound) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, _wellness_pre_to_out(wellness)


@router.patch(
    "/training-sessions/{id}/wellness-pre/{athleteId}",
    response={200: WellnessPreOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def update_wellness_pre(request, id: uuid.UUID, athleteId: uuid.UUID, body: UpdateWellnessPreIn):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPreRepository()
    try:
        wellness = UpdateWellnessPreUseCase(session_repo, wellness_repo).execute(
            UpdateWellnessPreInput(
                session_id=id,
                athlete_id=athleteId,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                readiness=body.readiness,
                sleep_quality=body.sleep_quality,
                mood=body.mood,
                fatigue=body.fatigue,
                muscle_soreness=body.muscle_soreness,
                notes=body.notes,
            )
        )
    except (TrainingSessionNotFound, WellnessEntryNotFound) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (WellnessWindowClosed, ValueError) as exc:
        raise HttpError(400, str(exc))
    return 200, _wellness_pre_to_out(wellness)


@router.get(
    "/training-sessions/{id}/wellness-post/{athleteId}",
    response={200: WellnessPostOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def get_wellness_post(request, id: uuid.UUID, athleteId: uuid.UUID):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPostRepository()
    try:
        wellness = GetWellnessPostUseCase(session_repo, wellness_repo).execute(
            GetWellnessPostInput(
                session_id=id,
                athlete_id=athleteId,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except (TrainingSessionNotFound, WellnessEntryNotFound) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, _wellness_post_to_out(wellness)


@router.patch(
    "/training-sessions/{id}/wellness-post/{athleteId}",
    response={200: WellnessPostOut, 401: ErrorOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def update_wellness_post(request, id: uuid.UUID, athleteId: uuid.UUID, body: UpdateWellnessPostIn):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPostRepository()
    try:
        wellness = UpdateWellnessPostUseCase(session_repo, wellness_repo).execute(
            UpdateWellnessPostInput(
                session_id=id,
                athlete_id=athleteId,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                perceived_exertion=body.perceived_exertion,
                enjoyment=body.enjoyment,
                technical_learning=body.technical_learning,
                notes=body.notes,
            )
        )
    except (TrainingSessionNotFound, WellnessEntryNotFound) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (WellnessWindowClosed, ValueError) as exc:
        raise HttpError(400, str(exc))
    return 200, _wellness_post_to_out(wellness)

@router.patch("/mesocycles/{id}", response={200: MesocycleOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def update_mesocycle(request, id: uuid.UUID, body: UpdateMesocycleIn):
    repo = MesocycleRepository()
    try:
        meso = UpdateMesocycleUseCase(repo).execute(
            UpdateMesocycleInput(
                id=id,
                actor_role=_get_actor_role(request),
                name=body.name,
                started_at=body.started_at,
                ended_at=body.ended_at,
                season_id=body.season_id,
                team_id=body.team_id,
                objective=body.objective,
                notes=body.notes,
            )
        )
    except MesocycleNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (ValueError, DataError, IntegrityError) as exc:
        raise HttpError(422, str(exc))
    return 200, _mesocycle_to_out(meso)


@router.patch("/microcycles/{id}", response={200: MicrocycleOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut})
def update_microcycle(request, id: uuid.UUID, body: UpdateMicrocycleIn):
    repo = MicrocycleRepository()
    try:
        micro = UpdateMicrocycleUseCase(repo).execute(
            UpdateMicrocycleInput(
                id=id,
                actor_role=_get_actor_role(request),
                week_number=body.week_number,
                started_at=body.started_at,
                ended_at=body.ended_at,
                team_id=body.team_id,
                name=body.name,
                objective=body.objective,
                planned_sessions_count=body.planned_sessions_count,
                notes=body.notes,
            )
        )
    except MicrocycleNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except (ValueError, DataError, IntegrityError) as exc:
        raise HttpError(422, str(exc))
    return 200, _microcycle_to_out(micro)


@router.get(
    "/training-sessions/{id}/execution-records/{record_id}",
    response={200: ExecutionRecordOut, 403: ErrorOut, 404: ErrorOut},
)
def get_execution_record(request, id: uuid.UUID, record_id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    record_repo = ExecutionRecordRepository()
    try:
        record = GetExecutionRecordUseCase(session_repo, record_repo).execute(
            GetExecutionRecordInput(
                session_id=id,
                record_id=record_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
            )
        )
    except (TrainingSessionNotFound, ExecutionRecordNotFound) as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, _execution_record_to_out(record)

@router.get(
    "/training-sessions/{id}/feedback-threads",
    response={200: FeedbackThreadListOut, 403: ErrorOut, 404: ErrorOut},
)
def list_feedback_threads(
    request,
    id: uuid.UUID,
    contextType: Optional[str] = None,
    athleteId: Optional[uuid.UUID] = None,
):
    session_repo = TrainingSessionRepository()
    thread_repo = FeedbackThreadRepository()
    try:
        items = ListFeedbackThreadsUseCase(session_repo, thread_repo).execute(
            ListFeedbackThreadsInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                context_type=contextType,
                athlete_id=athleteId,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, FeedbackThreadListOut(data=[_feedback_thread_to_out(item) for item in items])


@router.post(
    "/training-sessions/{id}/feedback-threads",
    response={201: FeedbackThreadOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def create_feedback_thread(request, id: uuid.UUID, body: CreateFeedbackThreadIn):
    session_repo = TrainingSessionRepository()
    thread_repo = FeedbackThreadRepository()
    try:
        thread = CreateFeedbackThreadUseCase(session_repo, thread_repo).execute(
            CreateFeedbackThreadInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                context_type=body.context_type,
                context_ref_id=body.context_ref_id,
                athlete_id=body.athlete_id,
                content=body.content,
                conversation_outcome=body.conversation_outcome,
                follow_up_at=body.follow_up_at,
                commitment_text=body.commitment_text,
                decision_text=body.decision_text,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return 201, _feedback_thread_to_out(thread)


@router.post(
    "/training-sessions/{id}/feedback-threads/{thread_id}/close",
    response={200: FeedbackThreadOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def close_feedback_thread(request, id: uuid.UUID, thread_id: uuid.UUID, body: CloseFeedbackThreadIn):
    session_repo = TrainingSessionRepository()
    thread_repo = FeedbackThreadRepository()
    try:
        thread = CloseFeedbackThreadUseCase(session_repo, thread_repo).execute(
            CloseFeedbackThreadInput(
                session_id=id,
                thread_id=thread_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                resolution_summary=body.resolution_summary,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except FeedbackThreadNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        raise HttpError(409, str(exc))
    return 200, _feedback_thread_to_out(thread)


@router.get(
    "/training-sessions/{id}/attention-queue",
    response={200: AttentionQueueListOut, 403: ErrorOut, 404: ErrorOut},
)
def list_attention_queue_items(
    request,
    id: uuid.UUID,
    severity: Optional[str] = None,
    resolved: bool = False,
):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    try:
        items = ListAttentionQueueItemsUseCase(session_repo, queue_repo).execute(
            ListAttentionQueueItemsInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                severity=severity,
                resolved=resolved,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, AttentionQueueListOut(data=[_attention_queue_item_to_out(item) for item in items])


@router.post(
    "/training-sessions/{id}/attention-queue/{item_id}/resolve",
    response={200: AttentionQueueItemOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def resolve_attention_queue_item(request, id: uuid.UUID, item_id: uuid.UUID, body: ResolveAttentionQueueItemIn):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    try:
        item = ResolveAttentionQueueItemUseCase(session_repo, queue_repo).execute(
            ResolveAttentionQueueItemInput(
                session_id=id,
                item_id=item_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                resolution_evidence=body.resolution_evidence,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except AttentionQueueItemNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except AttentionQueueConflict as exc:
        raise HttpError(409, str(exc))
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return 200, _attention_queue_item_to_out(item)


@router.post(
    "/training-sessions/{id}/attention-queue/{item_id}/dismiss",
    response={200: AttentionQueueItemOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def dismiss_attention_queue_item(request, id: uuid.UUID, item_id: uuid.UUID, body: DismissAttentionQueueItemIn):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    try:
        item = DismissAttentionQueueItemUseCase(session_repo, queue_repo).execute(
            DismissAttentionQueueItemInput(
                session_id=id,
                item_id=item_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                dismissal_reason=body.dismissal_reason,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except AttentionQueueItemNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except AttentionQueueConflict as exc:
        raise HttpError(409, str(exc))
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return 200, _attention_queue_item_to_out(item)


@router.post(
    "/training-sessions/{id}/attention-queue/{item_id}/escalate",
    response={200: AttentionQueueItemOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def escalate_attention_queue_item(request, id: uuid.UUID, item_id: uuid.UUID, body: EscalateAttentionQueueItemIn):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    try:
        item = EscalateAttentionQueueItemUseCase(session_repo, queue_repo).execute(
            EscalateAttentionQueueItemInput(
                session_id=id,
                item_id=item_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                escalation_target=body.escalation_target,
                escalation_note=body.escalation_note,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except AttentionQueueItemNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except AttentionQueueConflict as exc:
        raise HttpError(409, str(exc))
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return 200, _attention_queue_item_to_out(item)


@router.get(
    "/training-sessions/{id}/recommendations",
    response={200: RecommendationListOut, 403: ErrorOut, 404: ErrorOut},
)
def list_recommendations(request, id: uuid.UUID, status: Optional[str] = None):
    session_repo = TrainingSessionRepository()
    recommendation_repo = RecommendationRepository()
    try:
        items = ListRecommendationsUseCase(session_repo, recommendation_repo).execute(
            ListRecommendationsInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                status=status,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, RecommendationListOut(data=[_recommendation_to_out(item) for item in items])


@router.post(
    "/training-sessions/{id}/recommendations/{rec_id}/accept",
    response={200: RecommendationOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def accept_recommendation(request, id: uuid.UUID, rec_id: uuid.UUID, body: AcceptRecommendationIn | None = None):
    session_repo = TrainingSessionRepository()
    recommendation_repo = RecommendationRepository()
    try:
        recommendation = AcceptRecommendationUseCase(session_repo, recommendation_repo).execute(
            AcceptRecommendationInput(
                session_id=id,
                recommendation_id=rec_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                coach_note=body.coach_note if body else None,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except RecommendationNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except RecommendationConflict as exc:
        raise HttpError(409, str(exc))
    return 200, _recommendation_to_out(recommendation)


@router.post(
    "/training-sessions/{id}/recommendations/{rec_id}/dismiss",
    response={200: RecommendationOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def dismiss_recommendation(request, id: uuid.UUID, rec_id: uuid.UUID, body: DismissRecommendationIn):
    session_repo = TrainingSessionRepository()
    recommendation_repo = RecommendationRepository()
    try:
        recommendation = DismissRecommendationUseCase(session_repo, recommendation_repo).execute(
            DismissRecommendationInput(
                session_id=id,
                recommendation_id=rec_id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                dismissal_reason=body.dismissal_reason,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except RecommendationNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except RecommendationConflict as exc:
        raise HttpError(409, str(exc))
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return 200, _recommendation_to_out(recommendation)


@router.get(
    "/training-sessions/{id}/ineligibility",
    response={200: AthleteIneligibilityDeclarationOut, 403: ErrorOut, 404: ErrorOut},
)
def get_ineligibility_status(request, id: uuid.UUID, athleteId: Optional[uuid.UUID] = None):
    session_repo = TrainingSessionRepository()
    ineligibility_repo = AthleteIneligibilityDeclarationRepository()
    try:
        declaration = GetIneligibilityStatusUseCase(session_repo, ineligibility_repo).execute(
            GetIneligibilityStatusInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                athlete_id=athleteId,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except IneligibilityDeclarationNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, _ineligibility_to_out(declaration)


@router.post(
    "/training-sessions/{id}/ineligibility",
    response={201: AthleteIneligibilityDeclarationOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def submit_ineligibility_declaration(request, id: uuid.UUID, body: SubmitIneligibilityDeclarationIn):
    session_repo = TrainingSessionRepository()
    ineligibility_repo = AthleteIneligibilityDeclarationRepository()
    try:
        declaration = SubmitIneligibilityDeclarationUseCase(session_repo, ineligibility_repo).execute(
            SubmitIneligibilityDeclarationInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                athlete_id=body.athlete_id,
                reason_flags=body.reason_flags,
                reason_other=body.reason_other,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        message = str(exc)
        if "PUBLISHED ou IN_PROGRESS" in message:
            raise HttpError(409, message)
        raise HttpError(400, message)
    return 201, _ineligibility_to_out(declaration)

@router.get(
    "/training-sessions/{id}/load-chart",
    response={200: LoadChartOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def get_load_chart(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    execution_record_repo = ExecutionRecordRepository()
    try:
        result = GetLoadChartUseCase(session_repo, execution_record_repo).execute(
            GetLoadChartInput(
                session_id=id,
                actor_role=_get_actor_role(request),
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, LoadChartOut(
        session_id=result.session.id,
        planned_load=result.session.planned_load,
        actual_load_recorded=result.session.actual_load_recorded,
        entries=[
            LoadChartEntryOut(
                id=e.id,
                recorded_at=e.recorded_at,
                planned_value=e.planned_value,
                actual_value=e.actual_value,
                planned_unit=e.planned_unit,
                actual_unit=e.actual_unit,
                notes=e.notes,
            )
            for e in result.load_entries
        ],
    )


@router.get(
    "/training-sessions/{id}/messages",
    response={200: FeedbackThreadListOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
def list_chat_messages(request, id: uuid.UUID):
    session_repo = TrainingSessionRepository()
    feedback_thread_repo = FeedbackThreadRepository()
    try:
        threads = ListChatMessagesUseCase(session_repo, feedback_thread_repo).execute(
            ListChatMessagesInput(
                session_id=id,
                actor_role=_get_actor_role(request),
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    return 200, FeedbackThreadListOut(data=[_feedback_thread_to_out(t) for t in threads])


@router.post(
    "/training-sessions/{id}/suggestions",
    response={201: FeedbackThreadOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
def submit_training_suggestion(request, id: uuid.UUID, body: SubmitTrainingSuggestionIn):
    session_repo = TrainingSessionRepository()
    feedback_thread_repo = FeedbackThreadRepository()
    try:
        thread = SubmitTrainingSuggestionUseCase(session_repo, feedback_thread_repo).execute(
            SubmitTrainingSuggestionInput(
                session_id=id,
                actor_role=_get_actor_role(request),
                actor_id=_get_actor_id(request),
                athlete_id=body.athlete_id,
                subject=body.subject,
                body=body.body,
            )
        )
    except TrainingSessionNotFound as exc:
        raise HttpError(404, str(exc))
    except InsufficientPrivilege as exc:
        raise HttpError(403, str(exc))
    except ValueError as exc:
        message = str(exc)
        if "PUBLISHED ou IN_PROGRESS" in message:
            raise HttpError(409, message)
        raise HttpError(400, message)
    return 201, _feedback_thread_to_out(thread)
