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

from ..application.use_cases import (
    DismissAttentionQueueItemInput,
    DismissAttentionQueueItemUseCase,
    EscalateAttentionQueueItemInput,
    EscalateAttentionQueueItemUseCase,
    ListAttentionQueueItemsInput,
    ListAttentionQueueItemsUseCase,
    ResolveAttentionQueueItemInput,
    ResolveAttentionQueueItemUseCase,
)
from ..infrastructure.repository import (
    AttentionQueueRepository,
    TrainingSessionRepository,
)
from ..schemas import (
    AttentionQueueItemOut,
    AttentionQueueListOut,
    DismissAttentionQueueItemIn,
    ErrorOut,
    EscalateAttentionQueueItemIn,
    ResolveAttentionQueueItemIn,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _attention_queue_item_to_out

router = Router()


@router.get(
    "/training-sessions/{id}/attention-queue",
    response={200: AttentionQueueListOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def list_attention_queue_items(
    request,
    id: uuid.UUID,
    severity: Optional[str] = None,
    resolved: bool = False,
):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    items = ListAttentionQueueItemsUseCase(session_repo, queue_repo).execute(
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
    response={200: AttentionQueueItemOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
@map_exceptions
def resolve_attention_queue_item(
    request, id: uuid.UUID, item_id: uuid.UUID, body: ResolveAttentionQueueItemIn
):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    item = ResolveAttentionQueueItemUseCase(session_repo, queue_repo).execute(
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
    response={200: AttentionQueueItemOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
@map_exceptions
def dismiss_attention_queue_item(
    request, id: uuid.UUID, item_id: uuid.UUID, body: DismissAttentionQueueItemIn
):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    item = DismissAttentionQueueItemUseCase(session_repo, queue_repo).execute(
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
    response={200: AttentionQueueItemOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut, 409: ErrorOut},
)
@map_exceptions
def escalate_attention_queue_item(
    request, id: uuid.UUID, item_id: uuid.UUID, body: EscalateAttentionQueueItemIn
):
    session_repo = TrainingSessionRepository()
    queue_repo = AttentionQueueRepository()
    item = EscalateAttentionQueueItemUseCase(session_repo, queue_repo).execute(
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
