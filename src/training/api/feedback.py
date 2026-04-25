"""feedback sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/feedback-threads
  POST /training-sessions/{id}/feedback-threads
  POST /training-sessions/{id}/feedback-threads/{thread_id}/close
"""

import uuid
from typing import Optional

from ninja import Router
from .deps import CamelRouter

from ..application.common.services import TrainingServices
from ..application.communication.dto import (
    CloseFeedbackThreadInput,
    CreateFeedbackThreadInput,
    ListFeedbackThreadsInput,
)
from ..schemas.communication import (
    CloseFeedbackThreadIn,
    CreateFeedbackThreadIn,
    FeedbackThreadListOut,
    FeedbackThreadOut,
)
from ..schemas.sessions import ProblemOut
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _feedback_thread_to_out

router = CamelRouter()


@router.get(
    "/training-sessions/{id}/feedback-threads",
    response={200: FeedbackThreadListOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def list_feedback_threads(
    request,
    id: uuid.UUID,
    contextType: Optional[str] = None,
    athleteId: Optional[uuid.UUID] = None,
):
    svc = TrainingServices()
    items = svc.list_feedback_threads_uc().execute(
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
    response={201: FeedbackThreadOut, 400: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def create_feedback_thread(request, id: uuid.UUID, body: CreateFeedbackThreadIn):
    svc = TrainingServices()
    thread = svc.create_feedback_thread_uc().execute(
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
    response={200: FeedbackThreadOut, 400: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut},
)
@map_exceptions
def close_feedback_thread(
    request, id: uuid.UUID, thread_id: uuid.UUID, body: CloseFeedbackThreadIn
):
    svc = TrainingServices()
    thread = svc.close_feedback_thread_uc().execute(
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
