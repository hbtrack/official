"""eligibility sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/ineligibility
  POST /training-sessions/{id}/ineligibility
"""

import uuid
from typing import Optional

from ninja import Router
from ninja.errors import HttpError

from ..application.use_cases import (
    GetIneligibilityStatusInput,
    GetIneligibilityStatusUseCase,
    SubmitIneligibilityDeclarationInput,
    SubmitIneligibilityDeclarationUseCase,
)
from ..infrastructure.repository import (
    AthleteIneligibilityDeclarationRepository,
    TrainingSessionRepository,
)
from ..schemas import (
    AthleteIneligibilityDeclarationOut,
    ErrorOut,
    SubmitIneligibilityDeclarationIn,
)
from .deps import _get_actor_id, _get_actor_role
from .errors import map_exceptions
from .mappers import _ineligibility_to_out

router = Router()


@router.get(
    "/training-sessions/{id}/ineligibility",
    response={200: AthleteIneligibilityDeclarationOut, 403: ErrorOut, 404: ErrorOut},
)
@map_exceptions
def get_ineligibility_status(request, id: uuid.UUID, athleteId: Optional[uuid.UUID] = None):
    session_repo = TrainingSessionRepository()
    ineligibility_repo = AthleteIneligibilityDeclarationRepository()
    declaration = GetIneligibilityStatusUseCase(session_repo, ineligibility_repo).execute(
        GetIneligibilityStatusInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            athlete_id=athleteId,
        )
    )
    return 200, _ineligibility_to_out(declaration)


@router.post(
    "/training-sessions/{id}/ineligibility",
    response={
        201: AthleteIneligibilityDeclarationOut,
        400: ErrorOut,
        403: ErrorOut,
        404: ErrorOut,
        409: ErrorOut,
    },
)
@map_exceptions
def submit_ineligibility_declaration(
    request, id: uuid.UUID, body: SubmitIneligibilityDeclarationIn
):
    session_repo = TrainingSessionRepository()
    ineligibility_repo = AthleteIneligibilityDeclarationRepository()
    declaration = SubmitIneligibilityDeclarationUseCase(
        session_repo, ineligibility_repo
    ).execute(
        SubmitIneligibilityDeclarationInput(
            session_id=id,
            actor_role=_get_actor_role(request),
            actor_id=_get_actor_id(request),
            athlete_id=body.athlete_id,
            reason_flags=body.reason_flags,
            reason_other=body.reason_other,
        )
    )
    return 201, _ineligibility_to_out(declaration)


def register(parent: Router) -> None:
    parent.add_router("", router)
