import pytest
from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.wellness_post_service import WellnessPostService
from app.models.training_session import TrainingSession


@pytest.mark.asyncio
async def test_invalidate_training_analytics_cache_marks_weekly_and_monthly(
    async_db: AsyncSession, organization, team, category, user,
):
    """
    INV-TRAIN-022 TRUTH: _invalidate_training_analytics_cache deve marcar
    cache_dirty=True nos registros weekly e monthly correspondentes.
    """
    # Arrange: cria microciclo no DB (FK training_microcycles.id)
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

    # Insere cache weekly com cache_dirty=False
    weekly_id = uuid4()
    await async_db.execute(text("""
        INSERT INTO training_analytics_cache
            (id, team_id, microcycle_id, granularity, cache_dirty)
        VALUES (:id, :team_id, :mc_id, 'weekly', false)
    """), {"id": str(weekly_id), "team_id": str(team.id), "mc_id": str(mc_id)})

    # Insere cache monthly com cache_dirty=False
    monthly_id = uuid4()
    await async_db.execute(text("""
        INSERT INTO training_analytics_cache
            (id, team_id, month, granularity, cache_dirty)
        VALUES (:id, :team_id, :month, 'monthly', false)
    """), {"id": str(monthly_id), "team_id": str(team.id), "month": date(2026, 1, 1)})

    await async_db.flush()

    # TrainingSession como objeto Python puro (não inserido no DB — só precisa das attrs)
    training_session = TrainingSession(
        organization_id=organization.id,
        created_by_user_id=user.id,
        team_id=team.id,
        session_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        session_type="quadra",
        microcycle_id=mc_id,
    )

    # Act
    service = WellnessPostService(async_db)
    await service._invalidate_training_analytics_cache(training_session)
    await async_db.flush()

    # Assert: ambos os registros devem estar com cache_dirty=True
    weekly_dirty = (await async_db.execute(
        text("SELECT cache_dirty FROM training_analytics_cache WHERE id = :id"),
        {"id": str(weekly_id)},
    )).scalar()

    monthly_dirty = (await async_db.execute(
        text("SELECT cache_dirty FROM training_analytics_cache WHERE id = :id"),
        {"id": str(monthly_id)},
    )).scalar()

    assert weekly_dirty is True, \
        "Cache weekly deve estar marcado como dirty após invalidação"
    assert monthly_dirty is True, \
        "Cache monthly deve estar marcado como dirty após invalidação"
