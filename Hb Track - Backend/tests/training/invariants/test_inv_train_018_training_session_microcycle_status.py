import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone
from uuid import uuid4

from app.core.context import ExecutionContext
from app.services.training_session_service import TrainingSessionService
from app.schemas.training_sessions import TrainingSessionCreate, SessionTypeEnum
from app.models.team import Team


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
    db.execute.return_value = _Result(team)

    ctx = ExecutionContext(
        user_id=uuid4(),
        email="test@example.com",
        role_code="coordenador",
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
