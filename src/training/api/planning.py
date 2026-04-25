"""planning sub-router — training.api.

Endpoints:
  GET   /mesocycles
  POST  /mesocycles
  GET   /mesocycles/{id}
  PATCH /mesocycles/{id}
  GET   /microcycles
  POST  /microcycles
  GET   /microcycles/{id}
  PATCH /microcycles/{id}
"""

import uuid
from typing import Optional

from django.db import DataError, IntegrityError
from ninja import Router
from .deps import CamelRouter
from ninja.errors import HttpError

from ..application.common.services import TrainingServices
from ..application.planning.dto import (
    CreateMesocycleInput,
    CreateMicrocycleInput,
    GetMesocycleInput,
    GetMicrocycleInput,
    ListMesocyclesInput,
    ListMicrocyclesInput,
    UpdateMesocycleInput,
    UpdateMicrocycleInput,
)
from ..schemas.planning import (
    CreateMesocycleIn,
    CreateMicrocycleIn,
    MesocycleListOut,
    MesocycleOut,
    MicrocycleListOut,
    MicrocycleOut,
    UpdateMesocycleIn,
    UpdateMicrocycleIn,
)
from ..schemas.sessions import ProblemOut
from .deps import _get_actor_role
from .errors import map_exceptions
from .mappers import _mesocycle_to_out, _microcycle_to_out

router = CamelRouter()


# ---------------------------------------------------------------------------
# Mesocycles
# ---------------------------------------------------------------------------

@router.get("/mesocycles", response={200: MesocycleListOut, 403: ProblemOut})
@map_exceptions
def list_mesocycles(request, organization_id: Optional[uuid.UUID] = None):
    svc = TrainingServices()
    items = svc.list_mesocycles_uc().execute(
        ListMesocyclesInput(organization_id=organization_id)
    )
    return 200, MesocycleListOut(items=[_mesocycle_to_out(m) for m in items])


@router.post("/mesocycles", response={201: MesocycleOut, 401: ProblemOut, 403: ProblemOut, 422: ProblemOut})
@map_exceptions
def create_mesocycle(request, body: CreateMesocycleIn):
    svc = TrainingServices()
    meso = svc.create_mesocycle_uc().execute(
        CreateMesocycleInput(
            actor_role=_get_actor_role(request),
            organization_id=body.organization_id,
            name=body.name,
            started_at=body.started_at,
            ended_at=body.ended_at,
            season_id=body.season_id,
            team_id=body.team_id,
            objective=body.objective,
            notes=body.notes,
        )
    )
    return 201, _mesocycle_to_out(meso)


@router.get("/mesocycles/{id}", response={200: MesocycleOut, 404: ProblemOut})
@map_exceptions
def get_mesocycle(request, id: uuid.UUID):
    svc = TrainingServices()
    meso = svc.get_mesocycle_uc().execute(GetMesocycleInput(id=id))
    return 200, _mesocycle_to_out(meso)


@router.patch("/mesocycles/{id}", response={200: MesocycleOut, 403: ProblemOut, 404: ProblemOut, 422: ProblemOut})
@map_exceptions
def update_mesocycle(request, id: uuid.UUID, body: UpdateMesocycleIn):
    svc = TrainingServices()
    meso = svc.update_mesocycle_uc().execute(
        UpdateMesocycleInput(
            id=id,
            actor_role=_get_actor_role(request),
            name=body.name,
            started_at=body.started_at,
            ended_at=body.ended_at,
            season_id=body.season_id,
            team_id=body.team_id,
            objective=body.objective,
            notes=body.notes,
        )
    )
    return 200, _mesocycle_to_out(meso)


# ---------------------------------------------------------------------------
# Microcycles
# ---------------------------------------------------------------------------

@router.get("/microcycles", response={200: MicrocycleListOut, 403: ProblemOut})
@map_exceptions
def list_microcycles(
    request,
    organization_id: Optional[uuid.UUID] = None,
    mesocycle_id: Optional[uuid.UUID] = None,
):
    svc = TrainingServices()
    items = svc.list_microcycles_uc().execute(
        ListMicrocyclesInput(
            organization_id=organization_id,
            mesocycle_id=mesocycle_id,
        )
    )
    return 200, MicrocycleListOut(items=[_microcycle_to_out(m) for m in items])


@router.post(
    "/microcycles", response={201: MicrocycleOut, 401: ProblemOut, 403: ProblemOut, 422: ProblemOut}
)
@map_exceptions
def create_microcycle(request, body: CreateMicrocycleIn):
    svc = TrainingServices()
    micro = svc.create_microcycle_uc().execute(
        CreateMicrocycleInput(
            actor_role=_get_actor_role(request),
            organization_id=body.organization_id,
            mesocycle_id=body.mesocycle_id,
            week_number=body.week_number,
            started_at=body.started_at,
            ended_at=body.ended_at,
            team_id=body.team_id,
            name=body.name,
            objective=body.objective,
            planned_sessions_count=body.planned_sessions_count,
            notes=body.notes,
        )
    )
    return 201, _microcycle_to_out(micro)


@router.get("/microcycles/{id}", response={200: MicrocycleOut, 404: ProblemOut})
@map_exceptions
def get_microcycle(request, id: uuid.UUID):
    svc = TrainingServices()
    micro = svc.get_microcycle_uc().execute(GetMicrocycleInput(id=id))
    return 200, _microcycle_to_out(micro)


@router.patch(
    "/microcycles/{id}", response={200: MicrocycleOut, 403: ProblemOut, 404: ProblemOut, 422: ProblemOut}
)
@map_exceptions
def update_microcycle(request, id: uuid.UUID, body: UpdateMicrocycleIn):
    svc = TrainingServices()
    micro = svc.update_microcycle_uc().execute(
        UpdateMicrocycleInput(
            id=id,
            actor_role=_get_actor_role(request),
            week_number=body.week_number,
            started_at=body.started_at,
            ended_at=body.ended_at,
            team_id=body.team_id,
            name=body.name,
            objective=body.objective,
            planned_sessions_count=body.planned_sessions_count,
            notes=body.notes,
        )
    )
    return 200, _microcycle_to_out(micro)


def register(parent: Router) -> None:
    parent.add_router("", router)
