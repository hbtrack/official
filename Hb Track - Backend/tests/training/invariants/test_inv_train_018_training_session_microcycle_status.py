import pytest
from datetime import datetime, timezone, date
from uuid import uuid4, UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.services.training_session_service import TrainingSessionService
from app.schemas.training_sessions import TrainingSessionCreate, SessionTypeEnum


@pytest.mark.asyncio
async def test_microcycle_session_status_respects_completeness(
    async_db: AsyncSession, organization, team, category, user,
):
    """
    INV-TRAIN-018 TRUTH: status da sessão deve ser 'scheduled' quando payload completo
    (duration_planned_minutes + location + main_objective) e 'draft' quando incompleto.
    Usa DB real — sem mocks ou monkeypatch.
    """
    # Arrange: cria microciclo real no DB (cobre 2026-01-19 a 2026-01-25)
    mc_id = uuid4()
    await async_db.execute(text("""
        INSERT INTO training_microcycles
            (id, organization_id, team_id, week_start, week_end, created_by_user_id)
        VALUES (:id, :org_id, :team_id, :ws, :we, :user_id)
    """), {
        "id": str(mc_id),
        "org_id": str(organization.id),
        "team_id": str(team.id),
        "ws": date(2026, 1, 19),
        "we": date(2026, 1, 25),
        "user_id": str(user.id),
    })
    await async_db.flush()

    ctx = ExecutionContext(
        user_id=UUID(str(user.id)),
        email="test@example.com",
        role_code="coordenador",
        request_id=str(uuid4()),
        organization_id=UUID(str(organization.id)),
        permissions={},
    )
    service = TrainingSessionService(async_db, ctx)

    base_payload = dict(
        organization_id=UUID(str(organization.id)),
        team_id=UUID(str(team.id)),
        session_at=datetime(2026, 1, 20, 10, 0, tzinfo=timezone.utc),
        session_type=SessionTypeEnum.QUADRA,
        microcycle_id=mc_id,
    )

    # Act 1: payload completo → status deve ser "scheduled"
    complete_payload = TrainingSessionCreate(
        **base_payload,
        duration_planned_minutes=90,
        location="Campo A",
        main_objective="Tático",
    )
    complete_session = await service.create(complete_payload)
    assert complete_session.status == "scheduled", (
        "INV-018: sessão com payload completo deve ter status 'scheduled'"
    )

    # Act 2: payload incompleto → status deve ser "draft"
    incomplete_payload = TrainingSessionCreate(
        **base_payload,
        duration_planned_minutes=None,
        location=None,
        main_objective=None,
    )
    incomplete_session = await service.create(incomplete_payload)
    assert incomplete_session.status == "draft", (
        "INV-018: sessão com payload incompleto deve ter status 'draft'"
    )
