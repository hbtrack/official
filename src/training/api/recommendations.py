"""recommendations sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/recommendations
  POST /training-sessions/{id}/recommendations/{rec_id}/accept
  POST /training-sessions/{id}/recommendations/{rec_id}/dismiss
"""

import uuid
from typing import Optional

from ninja import Router

from ..application.use_cases import (
    AcceptRecommendationInput,
    AcceptRecommendationUseCase,
    DismissRecommendationInput,
    DismissRecommendationUseCase,
    ListRecommendationsInput,
    ListRecommendationsUseCase,
)
from ..infrastructure.repository import (
    RecommendationRepository,
    TrainingSessionRepository,
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
    session_repo = TrainingSessionRepository()
    recommendation_repo = RecommendationRepository()
    items = ListRecommendationsUseCase(session_repo, recommendation_repo).execute(
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
    session_repo = TrainingSessionRepository()
    recommendation_repo = RecommendationRepository()
    recommendation = AcceptRecommendationUseCase(session_repo, recommendation_repo).execute(
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
    session_repo = TrainingSessionRepository()
    recommendation_repo = RecommendationRepository()
    recommendation = DismissRecommendationUseCase(session_repo, recommendation_repo).execute(
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
