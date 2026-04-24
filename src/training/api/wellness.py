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
from .deps import CamelRouter

from ..application.common.services import TrainingServices
from ..application.use_cases import (
    GetWellnessPostInput,
    GetWellnessPreInput,
    SubmitWellnessPostInput,
    SubmitWellnessPreInput,
    UpdateWellnessPostInput,
    UpdateWellnessPreInput,
)
from ..schemas import (
    ProblemOut,
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

router = CamelRouter()


# ---------------------------------------------------------------------------
# Wellness Pre
# ---------------------------------------------------------------------------

@router.post(
    "/training-sessions/{id}/wellness-pre",
    response={
        201: WellnessPreOut,
        400: ProblemOut,
        401: ProblemOut,
        403: ProblemOut,
        404: ProblemOut,
        409: ProblemOut,
    },
)
@map_exceptions
def submit_wellness_pre(request, id: uuid.UUID, body: SubmitWellnessPreIn):
    svc = TrainingServices()
    wellness = svc.submit_wellness_pre_uc().execute(
        SubmitWellnessPreInput(
            session_id=id,
            athlete_id=body.athlete_id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            readiness=body.readiness,
            sleep_quality=body.sleep_quality,
            sleep_hours=body.sleep_hours,
            mood=body.mood,
            fatigue=body.fatigue,
            muscle_soreness=body.muscle_soreness,
            notes=body.notes,
        )
    )
    return 201, _wellness_pre_to_out(wellness)


@router.get(
    "/training-sessions/{id}/wellness-pre/{athleteId}",
    response={200: WellnessPreOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def get_wellness_pre(request, id: uuid.UUID, athleteId: uuid.UUID):
    svc = TrainingServices()
    wellness = svc.get_wellness_pre_uc().execute(
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
    response={200: WellnessPreOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def update_wellness_pre(request, id: uuid.UUID, athleteId: uuid.UUID, body: UpdateWellnessPreIn):
    svc = TrainingServices()
    wellness = svc.update_wellness_pre_uc().execute(
        UpdateWellnessPreInput(
            session_id=id,
            athlete_id=athleteId,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            readiness=body.readiness,
            sleep_quality=body.sleep_quality,
            sleep_hours=body.sleep_hours,
            mood=body.mood,
            fatigue=body.fatigue,
            muscle_soreness=body.muscle_soreness,
            notes=body.notes,
            provided_fields=frozenset(body.model_fields_set),
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
        400: ProblemOut,
        401: ProblemOut,
        403: ProblemOut,
        404: ProblemOut,
        409: ProblemOut,
    },
)
@map_exceptions
def submit_wellness_post(request, id: uuid.UUID, body: SubmitWellnessPostIn):
    svc = TrainingServices()
    wellness = svc.submit_wellness_post_uc().execute(
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
    response={200: WellnessPostOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def get_wellness_post(request, id: uuid.UUID, athleteId: uuid.UUID):
    svc = TrainingServices()
    wellness = svc.get_wellness_post_uc().execute(
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
    response={200: WellnessPostOut, 400: ProblemOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def update_wellness_post(
    request, id: uuid.UUID, athleteId: uuid.UUID, body: UpdateWellnessPostIn
):
    svc = TrainingServices()
    wellness = svc.update_wellness_post_uc().execute(
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
