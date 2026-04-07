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
    CreateExecutionRecordUseCase,
    CreateExecutionRecordInput,
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
    GetTrainingSessionUseCase,
    GetTrainingSessionInput,
    ListSessionBlocksUseCase,
    ListSessionBlocksInput,
    ListTrainingSessionsUseCase,
    ListTrainingSessionsInput,
    SubmitWellnessPostUseCase,
    SubmitWellnessPostInput,
    SubmitWellnessPreUseCase,
    SubmitWellnessPreInput,
    TransitionTrainingSessionUseCase,
    TransitionTrainingSessionInput,
    UpdateSessionBlockUseCase,
    UpdateSessionBlockInput,
)
from .domain.entities import TrainingSessionStatus
from .domain.rules import (
    DuplicateWellnessEntry,
    ElasticSumRuleViolation,
    InsufficientPrivilege,
    InvalidStatusTransition,
    RoleLabel,
    SessionBlockNotFound,
    SessionNotMutable,
    TrainingSessionNotFound,
    WellnessWindowClosed,
)
from .infrastructure.repository import (
    AttentionQueueRepository,
    ExecutionRecordRepository,
    FeedbackThreadRepository,
    MesocycleRepository,
    MicrocycleRepository,
    SessionBlockRepository,
    SessionObjectiveRepository,
    TrainingSessionRepository,
    WellnessPostRepository,
    WellnessPreRepository,
)
from .schemas import (
    AddSessionBlockIn,
    CreateExecutionRecordIn,
    CreateMesocycleIn,
    CreateMicrocycleIn,
    CreateSessionObjectiveIn,
    CreateTrainingSessionIn,
    ErrorOut,
    ExecutionRecordListOut,
    ExecutionRecordOut,
    MesocycleListOut,
    MesocycleOut,
    MicrocycleListOut,
    MicrocycleOut,
    SessionBlockListOut,
    SessionBlockOut,
    SessionObjectiveListOut,
    SessionObjectiveOut,
    SubmitWellnessPostIn,
    SubmitWellnessPreIn,
    TransitionOut,
    TrainingSessionListOut,
    TrainingSessionOut,
    UpdateSessionBlockIn,
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
    session = session_repo.get_by_id(id)
    if not session:
        raise HttpError(404, "Sessão não encontrada")
    records = record_repo.list_by_session(id)
    return 200, ExecutionRecordListOut(
        data=[ExecutionRecordOut(
            id=r.id,
            session_id=r.session_id,
            execution_type=r.execution_type.value,
            recorded_at=r.recorded_at,
            created_by_user_id=r.created_by_user_id,
            created_at=r.created_at,
            updated_at=r.updated_at,
            block_id=r.block_id,
            planned_value=r.planned_value,
            actual_value=r.actual_value,
            planned_unit=r.planned_unit,
            actual_unit=r.actual_unit,
            adjustment_reason_type=r.adjustment_reason_type,
            coach_rationale=r.coach_rationale,
            notes=r.notes,
        ) for r in records]
    )

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
    session = session_repo.get_by_id(id)
    if not session:
        raise HttpError(404, "Sessão não encontrada")
    objs = obj_repo.list_by_session(id)
    return 200, SessionObjectiveListOut(
        data=[SessionObjectiveOut(
            id=o.id,
            session_id=o.session_id,
            origin=o.origin.value,
            objective_type=o.objective_type,
            description=o.description,
            origin_notes=o.origin_notes,
            priority=o.priority,
            created_at=o.created_at,
            updated_at=o.updated_at,
        ) for o in objs]
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
    return 201, SessionObjectiveOut(
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

# ---------------------------------------------------------------------------
# Mesocycles
# ---------------------------------------------------------------------------

@router.get("/mesocycles", response={200: MesocycleListOut, 403: ErrorOut})
def list_mesocycles(request, organization_id: Optional[uuid.UUID] = None):
    repo = MesocycleRepository()
    items = repo.list(organization_id=organization_id)
    return 200, MesocycleListOut(items=[
        MesocycleOut(
            id=m.id,
            organization_id=m.organization_id,
            name=m.name,
            started_at=m.started_at,
            ended_at=m.ended_at,
            created_at=m.created_at,
            updated_at=m.updated_at,
            season_id=m.season_id,
            team_id=m.team_id,
            objective=m.objective,
            notes=m.notes,
        ) for m in items
    ])

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
    return 201, MesocycleOut(
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

@router.get("/mesocycles/{id}", response={200: MesocycleOut, 404: ErrorOut})
def get_mesocycle(request, id: uuid.UUID):
    repo = MesocycleRepository()
    meso = repo.get_by_id(id)
    if not meso:
        raise HttpError(404, "Mesociclo não encontrado")
    return 200, MesocycleOut(
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
    items = repo.list(organization_id=organization_id, mesocycle_id=mesocycle_id)
    return 200, MicrocycleListOut(items=[
        MicrocycleOut(
            id=m.id,
            organization_id=m.organization_id,
            mesocycle_id=m.mesocycle_id,
            week_number=m.week_number,
            started_at=m.started_at,
            ended_at=m.ended_at,
            created_at=m.created_at,
            updated_at=m.updated_at,
            team_id=m.team_id,
            name=m.name,
            objective=m.objective,
            planned_sessions_count=m.planned_sessions_count,
            notes=m.notes,
        ) for m in items
    ])

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
    return 201, MicrocycleOut(
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

@router.get("/microcycles/{id}", response={200: MicrocycleOut, 404: ErrorOut})
def get_microcycle(request, id: uuid.UUID):
    repo = MicrocycleRepository()
    micro = repo.get_by_id(id)
    if not micro:
        raise HttpError(404, "Microciclo não encontrado")
    return 200, MicrocycleOut(
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

# ---------------------------------------------------------------------------
# Stubs de contrato — B10-001 source graph integrity
# Implementação pendente (known_gaps). raise NotImplementedError até fase de implementação.
# ---------------------------------------------------------------------------

def update_training_session(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def delete_training_session(request, id):
    raise NotImplementedError("stub — B10-001")

def reorder_session_blocks(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def list_session_attendance(request, id):
    raise NotImplementedError("stub — B10-001")

def record_session_attendance(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def get_wellness_pre(request, id):
    raise NotImplementedError("stub — B10-001")

def update_wellness_pre(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def get_wellness_post(request, id):
    raise NotImplementedError("stub — B10-001")

def update_wellness_post(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def update_mesocycle(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def update_microcycle(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def get_execution_record(request, id, record_id):
    raise NotImplementedError("stub — B10-001")

def list_feedback_threads(request, id):
    raise NotImplementedError("stub — B10-001")

def create_feedback_thread(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def close_feedback_thread(request, id, thread_id):
    raise NotImplementedError("stub — B10-001")

def list_attention_queue_items(request, id):
    raise NotImplementedError("stub — B10-001")

def resolve_attention_queue_item(request, id, item_id, body=None):
    raise NotImplementedError("stub — B10-001")

def dismiss_attention_queue_item(request, id, item_id):
    raise NotImplementedError("stub — B10-001")

def escalate_attention_queue_item(request, id, item_id):
    raise NotImplementedError("stub — B10-001")

def list_recommendations(request, id):
    raise NotImplementedError("stub — B10-001")

def accept_recommendation(request, id, rec_id):
    raise NotImplementedError("stub — B10-001")

def dismiss_recommendation(request, id, rec_id):
    raise NotImplementedError("stub — B10-001")

def get_ineligibility_status(request, id):
    raise NotImplementedError("stub — B10-001")

def submit_ineligibility_declaration(request, id, body=None):
    raise NotImplementedError("stub — B10-001")

def get_load_chart(request, id):
    raise NotImplementedError("stub — B10-001")

def list_chat_messages(request, id):
    raise NotImplementedError("stub — B10-001")

def submit_training_suggestion(request, id, body=None):
    raise NotImplementedError("stub — B10-001")
