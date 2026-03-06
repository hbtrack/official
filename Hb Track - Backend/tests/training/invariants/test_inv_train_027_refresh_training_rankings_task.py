"""
Teste unitário para refresh_training_rankings_task (INV-TRAIN-027).

Verifica que a task:
1. Busca teams ativos
2. Busca caches com cache_dirty=true para cada team
3. Marca caches como não-dirty e atualiza calculated_at

Sem unittest.mock — usa contextlib.asynccontextmanager + data classes Python puros.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

import app.core.celery_tasks as _celery_mod
from app.core.celery_tasks import refresh_training_rankings_task


# ---------------------------------------------------------------------------
# Helpers Python puros (sem unittest.mock)
# ---------------------------------------------------------------------------

class _Rows:
    """Simula o resultado de db.execute(...).scalars().all() sem mock."""

    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class _Team:
    """Team fake com os atributos lidos pela task."""

    def __init__(self):
        self.id = uuid4()
        self.deleted_at = None
        self.active_from = datetime(2025, 1, 1, tzinfo=timezone.utc)


class _Cache:
    """Cache fake mutável — a task define cache_dirty/calculated_at in-place."""

    def __init__(self, team_id):
        self.id = uuid4()
        self.team_id = team_id
        self.cache_dirty = True
        self.calculated_at = None


class _SequenceDB:
    """DB fake que retorna resultados pré-configurados em sequência."""

    def __init__(self, *returns):
        self._idx = 0
        self._returns = list(returns)
        self.commit_calls = 0

    async def execute(self, stmt):
        r = self._returns[self._idx]
        self._idx += 1
        return r

    async def commit(self):
        self.commit_calls += 1


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

def test_refresh_training_rankings_task_recalculates_dirty_caches():
    """
    Verifica que a task refresh_training_rankings_task:
    1. Busca teams ativos
    2. Busca caches com cache_dirty=true
    3. Atualiza caches dirty -> clean (cache_dirty=False, calculated_at preenchido)
    """
    team = _Team()
    cache = _Cache(team.id)
    fake_db = _SequenceDB(_Rows([team]), _Rows([cache]))

    @asynccontextmanager
    async def _fake_ctx():
        yield fake_db

    original = _celery_mod.get_db_context
    _celery_mod.get_db_context = _fake_ctx
    try:
        result = refresh_training_rankings_task()
    finally:
        _celery_mod.get_db_context = original

    assert result["teams_processed"] == 1
    assert result["caches_refreshed"] == 1
    assert result["success"] is True
    assert len(result["errors"]) == 0
    assert cache.cache_dirty is False, "Cache deve estar marcado como não-dirty"
    assert cache.calculated_at is not None, "calculated_at deve ter sido preenchido"


def test_refresh_training_rankings_task_no_dirty_caches():
    """
    Verifica que a task não falha quando não há caches dirty.
    """
    team = _Team()
    fake_db = _SequenceDB(_Rows([team]), _Rows([]))

    @asynccontextmanager
    async def _fake_ctx():
        yield fake_db

    original = _celery_mod.get_db_context
    _celery_mod.get_db_context = _fake_ctx
    try:
        result = refresh_training_rankings_task()
    finally:
        _celery_mod.get_db_context = original

    assert result["teams_processed"] == 1
    assert result["caches_refreshed"] == 0
    assert result["success"] is True
    assert len(result["errors"]) == 0


def test_refresh_training_rankings_task_no_active_teams():
    """
    Verifica que a task não falha quando não há teams ativos.
    """
    fake_db = _SequenceDB(_Rows([]))

    @asynccontextmanager
    async def _fake_ctx():
        yield fake_db

    original = _celery_mod.get_db_context
    _celery_mod.get_db_context = _fake_ctx
    try:
        result = refresh_training_rankings_task()
    finally:
        _celery_mod.get_db_context = original

    assert result["teams_processed"] == 0
    assert result["caches_refreshed"] == 0
    assert result["success"] is True
