"""chat sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/messages
  POST /training-sessions/{id}/suggestions
"""

import uuid

from ninja import Router
from .deps import CamelRouter

from ..application.common.services import TrainingServices
from ..application.use_cases import (
    ListChatMessagesInput,
    SubmitTrainingSuggestionInput,
)
from ..schemas import (
    ProblemOut,
    FeedbackThreadListOut,
    FeedbackThreadOut,
    SubmitTrainingSuggestionIn,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _feedback_thread_to_out

router = CamelRouter()


@router.get(
    "/training-sessions/{id}/messages",
    response={200: FeedbackThreadListOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def list_chat_messages(request, id: uuid.UUID):
    svc = TrainingServices()
    threads = svc.list_chat_messages_uc().execute(
        ListChatMessagesInput(
            session_id=id,
            actor_role=_get_actor_role(request),
        )
    )
    return 200, FeedbackThreadListOut(data=[_feedback_thread_to_out(t) for t in threads])


@router.post(
    "/training-sessions/{id}/suggestions",
    response={201: FeedbackThreadOut, 400: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut},
)
@map_exceptions
def submit_training_suggestion(request, id: uuid.UUID, body: SubmitTrainingSuggestionIn):
    svc = TrainingServices()
    thread = svc.submit_training_suggestion_uc().execute(
        SubmitTrainingSuggestionInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            athlete_id=body.athlete_id,
            subject=body.subject,
            body=body.body,
        )
    )
    return 201, _feedback_thread_to_out(thread)


def register(parent: Router) -> None:
    parent.add_router("", router)
