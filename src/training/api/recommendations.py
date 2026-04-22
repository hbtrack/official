"""recommendations sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/recommendations
  POST /training-sessions/{id}/recommendations/{rec_id}/accept
  POST /training-sessions/{id}/recommendations/{rec_id}/dismiss
"""

import uuid
from typing import Optional

from ninja import Router

from ..application.common.services import TrainingServices
from ..application.use_cases import (
    AcceptRecommendationInput,
    DismissRecommendationInput,
    ListRecommendationsInput,
)
from ..schemas import (
    AcceptRecommendationIn,
    DismissRecommendationIn,
    ErrorOut,
    RecommendationListOut,
    RecommendationOut,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _recommendation_to_out

router = Router()


@router.get(
    "/training-sessions/{id}/recommendations",
    response={200: RecommendationListOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def list_recommendations(request, id: uuid.UUID, status: Optional[str] = None):
    svc = TrainingServices()
    items = svc.list_recommendations_uc().execute(
        ListRecommendationsInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            status=status,
        )
    )
    return 200, RecommendationListOut(data=[_recommendation_to_out(item) for item in items])


@router.post(
    "/training-sessions/{id}/recommendations/{rec_id}/accept",
    response={200: RecommendationOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
@map_exceptions
def accept_recommendation(
    request, id: uuid.UUID, rec_id: uuid.UUID, body: AcceptRecommendationIn | None = None
):
    svc = TrainingServices()
    recommendation = svc.accept_recommendation_uc().execute(
        AcceptRecommendationInput(
            session_id=id,
            recommendation_id=rec_id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            coach_note=body.coach_note if body else None,
        )
    )
    return 200, _recommendation_to_out(recommendation)


@router.post(
    "/training-sessions/{id}/recommendations/{rec_id}/dismiss",
    response={200: RecommendationOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
@map_exceptions
def dismiss_recommendation(
    request, id: uuid.UUID, rec_id: uuid.UUID, body: DismissRecommendationIn
):
    svc = TrainingServices()
    recommendation = svc.dismiss_recommendation_uc().execute(
        DismissRecommendationInput(
            session_id=id,
            recommendation_id=rec_id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            dismissal_reason=body.dismissal_reason,
        )
    )
    return 200, _recommendation_to_out(recommendation)


def register(parent: Router) -> None:
    parent.add_router("", router)
