"""feedback sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/feedback-threads
  POST /training-sessions/{id}/feedback-threads
  POST /training-sessions/{id}/feedback-threads/{thread_id}/close
"""

import uuid
from typing import Optional

from ninja import Router

from ..application.use_cases import (
    CloseFeedbackThreadInput,
    CloseFeedbackThreadUseCase,
    CreateFeedbackThreadInput,
    CreateFeedbackThreadUseCase,
    ListFeedbackThreadsInput,
    ListFeedbackThreadsUseCase,
)
from ..infrastructure.repository import (
    FeedbackThreadRepository,
    TrainingSessionRepository,
)
from ..schemas import (
    CloseFeedbackThreadIn,
    CreateFeedbackThreadIn,
    ErrorOut,
    FeedbackThreadListOut,
    FeedbackThreadOut,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _feedback_thread_to_out

router = Router()


@router.get(
    "/training-sessions/{id}/feedback-threads",
    response={200: FeedbackThreadListOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def list_feedback_threads(
    request,
    id: uuid.UUID,
    contextType: Optional[str] = None,
    athleteId: Optional[uuid.UUID] = None,
):
    session_repo = TrainingSessionRepository()
    thread_repo = FeedbackThreadRepository()
    items = ListFeedbackThreadsUseCase(session_repo, thread_repo).execute(
        ListFeedbackThreadsInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            context_type=contextType,
            athlete_id=athleteId,
        )
    )
    return 200, FeedbackThreadListOut(data=[_feedback_thread_to_out(item) for item in items])


@router.post(
    "/training-sessions/{id}/feedback-threads",
    response={201: FeedbackThreadOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def create_feedback_thread(request, id: uuid.UUID, body: CreateFeedbackThreadIn):
    session_repo = TrainingSessionRepository()
    thread_repo = FeedbackThreadRepository()
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
    return 201, _feedback_thread_to_out(thread)


@router.post(
    "/training-sessions/{id}/feedback-threads/{thread_id}/close",
    response={200: FeedbackThreadOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
@map_exceptions
def close_feedback_thread(
    request, id: uuid.UUID, thread_id: uuid.UUID, body: CloseFeedbackThreadIn
):
    session_repo = TrainingSessionRepository()
    thread_repo = FeedbackThreadRepository()
    thread = CloseFeedbackThreadUseCase(session_repo, thread_repo).execute(
        CloseFeedbackThreadInput(
            session_id=id,
            thread_id=thread_id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            resolution_summary=body.resolution_summary,
        )
    )
    return 200, _feedback_thread_to_out(thread)


def register(parent: Router) -> None:
    parent.add_router("", router)
