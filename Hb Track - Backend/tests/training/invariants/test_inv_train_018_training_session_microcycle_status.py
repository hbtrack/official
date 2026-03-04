import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone, date
from uuid import uuid4

from app.core.context import ExecutionContext
from app.services.training_session_service import TrainingSessionService
from app.schemas.training_sessions import TrainingSessionCreate, SessionTypeEnum
from app.models.team import Team
from app.models.training_microcycle import TrainingMicrocycle


class _Result:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


@pytest.mark.asyncio
async def test_microcycle_session_status_respects_completeness(monkeypatch):
    db = AsyncMock()
    db.add = Mock()

    org_id = uuid4()
    team_id = uuid4()
    team = Team(
        id=team_id,
        organization_id=org_id,
        name="Equipe A",
        category_id=1,
        gender="masculino",
        is_our_team=True,
    )
    microcycle = TrainingMicrocycle(
        id=uuid4(),
        organization_id=org_id,
        team_id=team_id,
        week_start=date(2026, 1, 19),
        week_end=date(2026, 1, 25),
    )
    # 3 db.execute calls per service.create: team, microcycle, audit (x2 chamadas)
    db.execute.side_effect = [
        _Result(team), _Result(microcycle), Mock(),
        _Result(team), _Result(microcycle), Mock(),
    ]

    ctx = ExecutionContext(
        user_id=uuid4(),
        email="test@example.com",
        role_code="coordenador",
        request_id=str(uuid4()),
        organization_id=org_id,
        permissions={},
    )
    service = TrainingSessionService(db, ctx)
    monkeypatch.setattr(service, "_check_and_generate_compensation_suggestion", AsyncMock())

    base_payload = dict(
        organization_id=org_id,
        team_id=team_id,
        session_at=datetime(2026, 1, 20, 10, 0, tzinfo=timezone.utc),
        session_type=SessionTypeEnum.QUADRA,
        microcycle_id=uuid4(),
    )

    complete_payload = TrainingSessionCreate(
        **base_payload,
        duration_planned_minutes=90,
        location="Campo A",
        main_objective="Tático",
    )
    complete_session = await service.create(complete_payload)
    assert complete_session.status == "scheduled"

    incomplete_payload = TrainingSessionCreate(
        **base_payload,
        duration_planned_minutes=None,
        location=None,
        main_objective=None,
    )
    incomplete_session = await service.create(incomplete_payload)
    assert incomplete_session.status == "draft"
