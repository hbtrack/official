"""
Teste unitário para refresh_training_rankings_task (INV-TRAIN-027).

Verifica que a task:
1. Busca teams ativos
2. Busca caches com cache_dirty=true
3. Marca caches como não-dirty e atualiza calculated_at
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4


def test_refresh_training_rankings_task_recalculates_dirty_caches():
    """
    Verifica que a task refresh_training_rankings_task:
    1. Busca teams ativos
    2. Busca caches com cache_dirty=true
    3. Atualiza caches dirty -> clean
    """
    # Mock team
    team_id = uuid4()
    mock_team = MagicMock()
    mock_team.id = team_id
    mock_team.deleted_at = None
    mock_team.active_from = datetime(2025, 1, 1)

    # Mock cache dirty
    cache_id = uuid4()
    mock_cache = MagicMock()
    mock_cache.id = cache_id
    mock_cache.team_id = team_id
    mock_cache.cache_dirty = True
    mock_cache.calculated_at = None

    # Setup execute returns
    teams_result = MagicMock()
    teams_result.scalars.return_value.all.return_value = [mock_team]

    caches_result = MagicMock()
    caches_result.scalars.return_value.all.return_value = [mock_cache]

    # Setup mock DB
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=[teams_result, caches_result])
    mock_db.commit = AsyncMock()

    with patch("app.core.celery_tasks.get_db_context") as mock_db_ctx:
        # Mock async context manager
        mock_ctx_manager = AsyncMock()
        mock_ctx_manager.__aenter__.return_value = mock_db
        mock_ctx_manager.__aexit__.return_value = None
        mock_db_ctx.return_value = mock_ctx_manager

        # Import and run task
        from app.core.celery_tasks import refresh_training_rankings_task

        result = refresh_training_rankings_task()

        # Assertions
        assert result["teams_processed"] == 1
        assert result["caches_refreshed"] == 1
        assert result["success"] is True
        assert "errors" in result
        assert len(result["errors"]) == 0

        # Verify cache was updated
        assert mock_cache.cache_dirty is False
        assert mock_cache.calculated_at is not None


def test_refresh_training_rankings_task_no_dirty_caches():
    """
    Verifica que a task não falha quando não há caches dirty.
    """
    # Mock team
    team_id = uuid4()
    mock_team = MagicMock()
    mock_team.id = team_id
    mock_team.deleted_at = None
    mock_team.active_from = datetime(2025, 1, 1)

    # Setup execute returns
    teams_result = MagicMock()
    teams_result.scalars.return_value.all.return_value = [mock_team]

    # No dirty caches
    caches_result = MagicMock()
    caches_result.scalars.return_value.all.return_value = []

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=[teams_result, caches_result])
    mock_db.commit = AsyncMock()

    with patch("app.core.celery_tasks.get_db_context") as mock_db_ctx:
        mock_ctx_manager = AsyncMock()
        mock_ctx_manager.__aenter__.return_value = mock_db
        mock_ctx_manager.__aexit__.return_value = None
        mock_db_ctx.return_value = mock_ctx_manager

        from app.core.celery_tasks import refresh_training_rankings_task

        result = refresh_training_rankings_task()

        assert result["teams_processed"] == 1
        assert result["caches_refreshed"] == 0
        assert result["success"] is True


def test_refresh_training_rankings_task_no_active_teams():
    """
    Verifica que a task não falha quando não há teams ativos.
    """
    # No teams
    teams_result = MagicMock()
    teams_result.scalars.return_value.all.return_value = []

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=teams_result)

    with patch("app.core.celery_tasks.get_db_context") as mock_db_ctx:
        mock_ctx_manager = AsyncMock()
        mock_ctx_manager.__aenter__.return_value = mock_db
        mock_ctx_manager.__aexit__.return_value = None
        mock_db_ctx.return_value = mock_ctx_manager

        from app.core.celery_tasks import refresh_training_rankings_task

        result = refresh_training_rankings_task()

        assert result["teams_processed"] == 0
        assert result["caches_refreshed"] == 0
        assert result["success"] is True
