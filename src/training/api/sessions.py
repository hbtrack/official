"""sessions sub-router — training.api.

Endpoints:
  GET    /training-sessions
  POST   /training-sessions
  GET    /training-sessions/{id}
  PATCH  /training-sessions/{id}
  DELETE /training-sessions/{id}
  POST   /training-sessions/{id}/publish
  POST   /training-sessions/{id}/unpublish
  POST   /training-sessions/{id}/start
  POST   /training-sessions/{id}/complete
  POST   /training-sessions/{id}/cancel
  POST   /training-sessions/{id}/archive
"""

import uuid
from typing import Optional

from ninja import Router
from .deps import CamelRouter

from ..application.common.services import TrainingServices
from ..application.use_cases import (
    CreateTrainingSessionInput,
    DeleteTrainingSessionInput,
    GetTrainingSessionInput,
    ListTrainingSessionsInput,
    TransitionTrainingSessionInput,
    UpdateTrainingSessionInput,
)
from ..domain.entities import TrainingSessionStatus
from ..schemas import (
    CreateTrainingSessionIn,
    ProblemOut,
    TransitionOut,
    TrainingSessionListOut,
    TrainingSessionOut,
    UpdateTrainingSessionIn,
)
from .deps import _get_actor_id, _get_actor_role, get_cursor_codec, resolve_access
from .errors import map_exceptions
from .mappers import _session_to_out

router = CamelRouter()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.get(
    "/training-sessions",
    response={200: TrainingSessionListOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut},
)
@map_exceptions
def list_training_sessions(
    request,
    organization_id: Optional[uuid.UUID] = None,
    team_id: Optional[uuid.UUID] = None,
    season_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    page_size: int = 20,
    page_token: Optional[str] = None,
):
    access = resolve_access(request)  # AccessContext — Fase 2; use cases ainda consomem campos soltos
    codec = get_cursor_codec()
    svc = TrainingServices()
    result = svc.list_training_sessions_uc(codec).execute(
        ListTrainingSessionsInput(
            actor_role=access.role,
            actor_id=access.actor_id,
            organization_id=organization_id,
            team_id=team_id,
            season_id=season_id,
            status=status,
            page_size=min(max(page_size, 1), 100),
            page_token=page_token,
        )
    )
    return 200, TrainingSessionListOut(
        items=[_session_to_out(s) for s in result.items],
        next_page_token=result.next_page_token,
    )


@router.post(
    "/training-sessions",
    response={
        201: TrainingSessionOut,
        400: ProblemOut,
        401: ProblemOut,
        403: ProblemOut,
        422: ProblemOut,
    },
)
@map_exceptions
def create_training_session(request, body: CreateTrainingSessionIn):
    svc = TrainingServices()
    session = svc.create_training_session_uc().execute(
        CreateTrainingSessionInput(
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
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
    return 201, _session_to_out(session)


@router.get(
    "/training-sessions/{id}",
    response={200: TrainingSessionOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def get_training_session(request, id: uuid.UUID):
    svc = TrainingServices()
    session = svc.get_training_session_uc().execute(
        GetTrainingSessionInput(
            id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 200, _session_to_out(session)


@router.patch(
    "/training-sessions/{id}",
    response={
        200: TrainingSessionOut,
        401: ProblemOut,
        403: ProblemOut,
        404: ProblemOut,
        422: ProblemOut,
    },
)
@map_exceptions
def update_training_session(request, id: uuid.UUID, body: UpdateTrainingSessionIn):
    svc = TrainingServices()
    session = svc.update_training_session_uc().execute(
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
    return 200, _session_to_out(session)


@router.delete(
    "/training-sessions/{id}",
    response={204: None, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut, 422: ProblemOut},
)
@map_exceptions
def delete_training_session(request, id: uuid.UUID, deleted_reason: str = ""):
    svc = TrainingServices()
    svc.delete_training_session_uc().execute(
        DeleteTrainingSessionInput(
            id=id,
            actor_role=_get_actor_role(request),
            deleted_reason=deleted_reason,
        )
    )
    return 204, None


# ---------------------------------------------------------------------------
# State transitions
# ---------------------------------------------------------------------------

def _do_transition(request, id: uuid.UUID, target_status: TrainingSessionStatus) -> TransitionOut:
    svc = TrainingServices()
    session = svc.transition_training_session_uc().execute(
        TransitionTrainingSessionInput(
            id=id,
            target_status=target_status,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return TransitionOut(id=session.id, status=session.status.value, updated_at=session.updated_at)


_TRANSITION_RESPONSE = {
    200: TransitionOut,
    401: ProblemOut,
    403: ProblemOut,
    404: ProblemOut,
    422: ProblemOut,
}


@router.post("/training-sessions/{id}/publish", response=_TRANSITION_RESPONSE)
@map_exceptions
def publish_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.PUBLISHED)


@router.post("/training-sessions/{id}/unpublish", response=_TRANSITION_RESPONSE)
@map_exceptions
def unpublish_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.SCHEDULED)


@router.post("/training-sessions/{id}/start", response=_TRANSITION_RESPONSE)
@map_exceptions
def start_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.IN_PROGRESS)


@router.post("/training-sessions/{id}/complete", response=_TRANSITION_RESPONSE)
@map_exceptions
def complete_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.COMPLETED)


@router.post("/training-sessions/{id}/cancel", response=_TRANSITION_RESPONSE)
@map_exceptions
def cancel_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.CANCELLED)


@router.post("/training-sessions/{id}/archive", response=_TRANSITION_RESPONSE)
@map_exceptions
def archive_training_session(request, id: uuid.UUID):
    return 200, _do_transition(request, id, TrainingSessionStatus.ARCHIVED)


def register(parent: Router) -> None:
    parent.add_router("", router)
