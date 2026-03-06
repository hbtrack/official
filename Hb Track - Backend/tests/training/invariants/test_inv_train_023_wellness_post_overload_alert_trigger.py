import pytest
from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.wellness_post_service import WellnessPostService
from app.models.training_session import TrainingSession


@pytest.mark.asyncio
async def test_trigger_overload_alert_on_wellness_post_runs_without_error(
    async_db: AsyncSession, organization, team, category,
):
    """
    INV-TRAIN-023 TRUTH: _trigger_overload_alert_on_wellness_post deve executar sem
    erro quando o Team existe no DB. Sem sessões na semana → check_weekly_overload
    retorna None cedo e nenhum alerta é criado.
    """
    # Arrange: cria TrainingSession Python obj (NÃO inserido no DB — só precisa das attrs)
    training_session = TrainingSession(
        id=uuid4(),
        organization_id=UUID(str(organization.id)),
        team_id=UUID(str(team.id)),
        session_at=datetime(2026, 1, 15, 15, 30, tzinfo=timezone.utc),
        session_type="quadra",
    )

    # Act: método busca team via db.get (team existe no DB via fixture)
    service = WellnessPostService(async_db)
    await service._trigger_overload_alert_on_wellness_post(training_session)

    # Assert: nenhum treinamento na semana → check_weekly_overload retorna None → 0 alertas
    result = await async_db.execute(
        text("SELECT COUNT(*) FROM training_alerts WHERE team_id = :tid"),
        {"tid": str(team.id)},
    )
    count = result.scalar()
    assert count == 0, (
        "INV-023: sem sessões na semana, nenhum alerta de sobrecarga deve ser criado"
    )
