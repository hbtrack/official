"""analytics sub-router — training.api.

Endpoints:
  GET  /training-sessions/{id}/load-chart
"""

import uuid

from ninja import Router
from .deps import CamelRouter
from ninja.errors import HttpError

from ..application.common.services import TrainingServices
from ..application.use_cases import (
    GetLoadChartInput,
)
from ..schemas import ProblemOut, LoadChartEntryOut, LoadChartOut
from .deps import _get_actor_role
from .errors import map_exceptions

router = CamelRouter()


@router.get(
    "/training-sessions/{id}/load-chart",
    response={200: LoadChartOut, 401: ProblemOut, 403: ProblemOut, 404: ProblemOut},
)
@map_exceptions
def get_load_chart(request, id: uuid.UUID):
    svc = TrainingServices()
    result = svc.get_load_chart_uc().execute(
        GetLoadChartInput(
            session_id=id,
            actor_role=_get_actor_role(request),
        )
    )
    return 200, LoadChartOut(
        session_id=result.session.id,
        planned_load=result.session.planned_load,
        actual_load_recorded=result.session.actual_load_recorded,
        entries=[
            LoadChartEntryOut(
                id=e.id,
                recorded_at=e.recorded_at,
                planned_value=e.planned_value,
                actual_value=e.actual_value,
                planned_unit=e.planned_unit,
                actual_unit=e.actual_unit,
                notes=e.notes,
            )
            for e in result.load_entries
        ],
    )


def register(parent: Router) -> None:
    parent.add_router("", router)
