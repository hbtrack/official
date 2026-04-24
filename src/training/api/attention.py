"""attention sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/attention-queue
  POST /training-sessions/{id}/attention-queue/{item_id}/resolve
  POST /training-sessions/{id}/attention-queue/{item_id}/dismiss
  POST /training-sessions/{id}/attention-queue/{item_id}/escalate
"""

import uuid
from typing import Optional

from ninja import Router
from .deps import CamelRouter

from ..application.common.services import TrainingServices
from ..application.use_cases import (
    DismissAttentionQueueItemInput,
    EscalateAttentionQueueItemInput,
    ListAttentionQueueItemsInput,
    ResolveAttentionQueueItemInput,
)
from ..schemas import (
    AttentionQueueItemOut,
    AttentionQueueListOut,
    DismissAttentionQueueItemIn,
    ProblemOut,
    EscalateAttentionQueueItemIn,
    ResolveAttentionQueueItemIn,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _attention_queue_item_to_out

router = CamelRouter()


@router.get(
    "/training-sessions/{id}/attention-queue",
    response={200: AttentionQueueListOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def list_attention_queue_items(
    request,
    id: uuid.UUID,
    severity: Optional[str] = None,
    resolved: bool = False,
):
    svc = TrainingServices()
    items = svc.list_attention_queue_items_uc().execute(
        ListAttentionQueueItemsInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            severity=severity,
            resolved=resolved,
        )
    )
    return 200, AttentionQueueListOut(data=[_attention_queue_item_to_out(item) for item in items])


@router.post(
    "/training-sessions/{id}/attention-queue/{item_id}/resolve",
    response={200: AttentionQueueItemOut, 400: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut},
)
@map_exceptions
def resolve_attention_queue_item(
    request, id: uuid.UUID, item_id: uuid.UUID, body: ResolveAttentionQueueItemIn
):
    svc = TrainingServices()
    item = svc.resolve_attention_queue_item_uc().execute(
        ResolveAttentionQueueItemInput(
            session_id=id,
            item_id=item_id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            resolution_evidence=body.resolution_evidence,
        )
    )
    return 200, _attention_queue_item_to_out(item)


@router.post(
    "/training-sessions/{id}/attention-queue/{item_id}/dismiss",
    response={200: AttentionQueueItemOut, 400: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut},
)
@map_exceptions
def dismiss_attention_queue_item(
    request, id: uuid.UUID, item_id: uuid.UUID, body: DismissAttentionQueueItemIn
):
    svc = TrainingServices()
    item = svc.dismiss_attention_queue_item_uc().execute(
        DismissAttentionQueueItemInput(
            session_id=id,
            item_id=item_id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            dismissal_reason=body.dismissal_reason,
        )
    )
    return 200, _attention_queue_item_to_out(item)


@router.post(
    "/training-sessions/{id}/attention-queue/{item_id}/escalate",
    response={200: AttentionQueueItemOut, 400: ProblemOut, 403: ProblemOut, 404: ProblemOut, 409: ProblemOut},
)
@map_exceptions
def escalate_attention_queue_item(
    request, id: uuid.UUID, item_id: uuid.UUID, body: EscalateAttentionQueueItemIn
):
    svc = TrainingServices()
    item = svc.escalate_attention_queue_item_uc().execute(
        EscalateAttentionQueueItemInput(
            session_id=id,
            item_id=item_id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            escalation_target=body.escalation_target,
            escalation_note=body.escalation_note,
        )
    )
    return 200, _attention_queue_item_to_out(item)


def register(parent: Router) -> None:
    parent.add_router("", router)
