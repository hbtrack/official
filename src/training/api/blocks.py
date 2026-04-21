"""blocks sub-router — training.api.

Endpoints:
  GET    /training-sessions/{id}/blocks
  POST   /training-sessions/{id}/blocks
  GET    /training-sessions/{id}/blocks/{block_id}
  PATCH  /training-sessions/{id}/blocks/{block_id}
  DELETE /training-sessions/{id}/blocks/{block_id}
  POST   /training-sessions/{id}/blocks/reorder
"""

import uuid

from ninja import Router
from ninja.errors import HttpError

from ..application.common.services import TrainingServices
from ..application.use_cases import (
    AddSessionBlockInput,
    DeleteSessionBlockInput,
    ListSessionBlocksInput,
    ReorderSessionBlocksInput,
    UpdateSessionBlockInput,
)
from ..schemas import (
    AddSessionBlockIn,
    ErrorOut,
    ReorderSessionBlocksIn,
    SessionBlockListOut,
    SessionBlockOut,
    UpdateSessionBlockIn,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _block_to_out

router = Router()


@router.get(
    "/training-sessions/{id}/blocks",
    response={200: SessionBlockListOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def list_session_blocks(request, id: uuid.UUID):
    svc = TrainingServices()
    blocks = svc.list_session_blocks_uc().execute(
        ListSessionBlocksInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
        )
    )
    return 200, SessionBlockListOut(data=[_block_to_out(b) for b in blocks])


@router.post(
    "/training-sessions/{id}/blocks",
    response={
        201: SessionBlockOut,
        401: ErrorOut,
        403: ErrorOut,
        404: ErrorOut,
        409: ErrorOut,
        422: ErrorOut,
    },
)
@map_exceptions
def add_session_block(request, id: uuid.UUID, body: AddSessionBlockIn):
    svc = TrainingServices()
    block = svc.add_session_block_uc().execute(
        AddSessionBlockInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            phase=body.phase,
            order_index=body.order_index,
            duration_minutes=body.duration_minutes,
            block_objective=body.block_objective,
            intensity=body.intensity,
            is_optional=body.is_optional,
            exercise_id=body.exercise_id,
            exercise_version_id=body.exercise_version_id,
            notes=body.notes,
        )
    )
    return 201, _block_to_out(block)


@router.get(
    "/training-sessions/{id}/blocks/{block_id}",
    response={200: SessionBlockOut, 403: ErrorOut, 404: ErrorOut},
)
def get_session_block(request, id: uuid.UUID, block_id: uuid.UUID):
    from ..domain.rules import SessionBlockNotFound
    block_repo = TrainingServices().session_block_repo()
    block = block_repo.get_by_id(block_id)
    if not block or block.session_id != id:
        raise SessionBlockNotFound("Bloco não encontrado")
    return 200, _block_to_out(block)


@router.patch(
    "/training-sessions/{id}/blocks/{block_id}",
    response={200: SessionBlockOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
@map_exceptions
def update_session_block(request, id: uuid.UUID, block_id: uuid.UUID, body: UpdateSessionBlockIn):
    svc = TrainingServices()
    block = svc.update_session_block_uc().execute(
        UpdateSessionBlockInput(
            session_id=id,
            block_id=block_id,
            actor_role=_get_actor_role(request),
            duration_minutes=body.duration_minutes,
            block_objective=body.block_objective,
            intensity=body.intensity,
            phase=body.phase,
            is_optional=body.is_optional,
            notes=body.notes,
            exercise_id=body.exercise_id,
            exercise_version_id=body.exercise_version_id,
        )
    )
    return 200, _block_to_out(block)


@router.delete(
    "/training-sessions/{id}/blocks/{block_id}",
    response={204: None, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
@map_exceptions
def delete_session_block(request, id: uuid.UUID, block_id: uuid.UUID):
    svc = TrainingServices()
    svc.delete_session_block_uc().execute(
        DeleteSessionBlockInput(
            session_id=id,
            block_id=block_id,
            actor_role=_get_actor_role(request),
        )
    )
    return 204, None


@router.post(
    "/training-sessions/{id}/blocks/reorder",
    response={200: SessionBlockListOut, 401: ErrorOut, 403: ErrorOut, 404: ErrorOut, 422: ErrorOut},
)
@map_exceptions
def reorder_session_blocks(request, id: uuid.UUID, body: ReorderSessionBlocksIn):
    svc = TrainingServices()
    blocks = svc.reorder_session_blocks_uc().execute(
        ReorderSessionBlocksInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            block_ids=body.block_ids,
        )
    )
    return 200, SessionBlockListOut(data=[_block_to_out(b) for b in blocks])


def register(parent: Router) -> None:
    parent.add_router("", router)
