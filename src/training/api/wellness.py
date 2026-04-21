"""wellness sub-router — training.api.

Endpoints:
  POST  /training-sessions/{id}/wellness-pre
  GET   /training-sessions/{id}/wellness-pre/{athleteId}
  PATCH /training-sessions/{id}/wellness-pre/{athleteId}
  POST  /training-sessions/{id}/wellness-post
  GET   /training-sessions/{id}/wellness-post/{athleteId}
  PATCH /training-sessions/{id}/wellness-post/{athleteId}
"""

import uuid

from ninja import Router

from ..application.use_cases import (
    GetWellnessPostInput,
    GetWellnessPostUseCase,
    GetWellnessPreInput,
    GetWellnessPreUseCase,
    SubmitWellnessPostInput,
    SubmitWellnessPostUseCase,
    SubmitWellnessPreInput,
    SubmitWellnessPreUseCase,
    UpdateWellnessPostInput,
    UpdateWellnessPostUseCase,
    UpdateWellnessPreInput,
    UpdateWellnessPreUseCase,
)
from ..infrastructure.repository import (
    TrainingSessionRepository,
    WellnessPostRepository,
    WellnessPreRepository,
)
from ..schemas import (
    ErrorOut,
    SubmitWellnessPostIn,
    SubmitWellnessPreIn,
    UpdateWellnessPostIn,
    UpdateWellnessPreIn,
    WellnessPostOut,
    WellnessPreOut,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _wellness_post_to_out, _wellness_pre_to_out

router = Router()


# ---------------------------------------------------------------------------
# Wellness Pre
# ---------------------------------------------------------------------------

@router.post(
    "/training-sessions/{id}/wellness-pre",
    response={
        201: WellnessPreOut,
        400: ErrorOut,
        401: ErrorOut,
        403: ErrorOut,
        404: ErrorOut,
        409: ErrorOut,
    },
)
@map_exceptions
def submit_wellness_pre(request, id: uuid.UUID, body: SubmitWellnessPreIn):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPreRepository()
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
    return 201, _wellness_pre_to_out(wellness)


@router.get(
    "/training-sessions/{id}/wellness-pre/{athleteId}",
    response={200: WellnessPreOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def get_wellness_pre(request, id: uuid.UUID, athleteId: uuid.UUID):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPreRepository()
    wellness = GetWellnessPreUseCase(session_repo, wellness_repo).execute(
        GetWellnessPreInput(
            session_id=id,
            athlete_id=athleteId,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 200, _wellness_pre_to_out(wellness)


@router.patch(
    "/training-sessions/{id}/wellness-pre/{athleteId}",
    response={200: WellnessPreOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def update_wellness_pre(request, id: uuid.UUID, athleteId: uuid.UUID, body: UpdateWellnessPreIn):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPreRepository()
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
    return 200, _wellness_pre_to_out(wellness)


# ---------------------------------------------------------------------------
# Wellness Post
# ---------------------------------------------------------------------------

@router.post(
    "/training-sessions/{id}/wellness-post",
    response={
        201: WellnessPostOut,
        400: ErrorOut,
        401: ErrorOut,
        403: ErrorOut,
        404: ErrorOut,
        409: ErrorOut,
    },
)
@map_exceptions
def submit_wellness_post(request, id: uuid.UUID, body: SubmitWellnessPostIn):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPostRepository()
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
    return 201, _wellness_post_to_out(wellness)


@router.get(
    "/training-sessions/{id}/wellness-post/{athleteId}",
    response={200: WellnessPostOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def get_wellness_post(request, id: uuid.UUID, athleteId: uuid.UUID):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPostRepository()
    wellness = GetWellnessPostUseCase(session_repo, wellness_repo).execute(
        GetWellnessPostInput(
            session_id=id,
            athlete_id=athleteId,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 200, _wellness_post_to_out(wellness)


@router.patch(
    "/training-sessions/{id}/wellness-post/{athleteId}",
    response={200: WellnessPostOut, 400: ErrorOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def update_wellness_post(
    request, id: uuid.UUID, athleteId: uuid.UUID, body: UpdateWellnessPostIn
):
    session_repo = TrainingSessionRepository()
    wellness_repo = WellnessPostRepository()
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
    return 200, _wellness_post_to_out(wellness)


def register(parent: Router) -> None:
    parent.add_router("", router)
