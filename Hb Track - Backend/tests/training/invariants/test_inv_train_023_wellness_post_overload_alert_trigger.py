import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from uuid import uuid4

from app.services.wellness_post_service import WellnessPostService
from app.services.training_alerts_service import TrainingAlertsService
from app.models.training_session import TrainingSession
from app.models.team import Team


@pytest.mark.asyncio
async def test_trigger_overload_alert_on_wellness_post_uses_session_week_and_team_multiplier(monkeypatch):
    db = AsyncMock()
    service = WellnessPostService(db)

    team_id = uuid4()
    session_at = datetime(2026, 1, 15, 15, 30, tzinfo=timezone.utc)
    training_session = TrainingSession(
        id=uuid4(),
        organization_id=uuid4(),
        team_id=team_id,
        session_at=session_at,
        session_type="quadra",
    )
    team = Team(
        id=team_id,
        organization_id=uuid4(),
        name="Equipe A",
        category_id=1,
        gender="masculino",
        is_our_team=True,
        alert_threshold_multiplier=2.5,
    )
    db.get.return_value = team

    check_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(TrainingAlertsService, "check_weekly_overload", check_mock)

    await service._trigger_overload_alert_on_wellness_post(training_session)

    check_mock.assert_awaited_once()
    _, kwargs = check_mock.call_args
    assert kwargs["team_id"] == team_id
    assert kwargs["alert_threshold_multiplier"] == float(team.alert_threshold_multiplier)
    assert kwargs["week_start"] == datetime(2026, 1, 12, tzinfo=timezone.utc)
