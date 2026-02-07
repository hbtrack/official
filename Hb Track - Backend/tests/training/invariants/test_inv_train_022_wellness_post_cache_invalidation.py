import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.sql.dml import Update

from app.services.wellness_post_service import WellnessPostService
from app.models.training_session import TrainingSession
from app.models.training_analytics_cache import TrainingAnalyticsCache


@pytest.mark.asyncio
async def test_invalidate_training_analytics_cache_marks_weekly_and_monthly():
    db = AsyncMock()
    service = WellnessPostService(db)

    training_session = TrainingSession(
        organization_id=uuid4(),
        created_by_user_id=uuid4(),
        team_id=uuid4(),
        session_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        session_type="quadra",
        microcycle_id=uuid4(),
    )

    await service._invalidate_training_analytics_cache(training_session)

    assert db.execute.call_count == 2
    stmts = [call.args[0] for call in db.execute.call_args_list]

    for stmt in stmts:
        assert isinstance(stmt, Update)
        assert stmt.table.name == TrainingAnalyticsCache.__tablename__

    weekly_stmt = next(stmt for stmt in stmts if "microcycle_id" in str(stmt))
    monthly_stmt = next(stmt for stmt in stmts if "month" in str(stmt))
    assert "granularity" in str(weekly_stmt)
    assert "granularity" in str(monthly_stmt)
