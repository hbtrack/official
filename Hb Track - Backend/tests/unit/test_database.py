"""Testes para database core"""
import pytest
from sqlalchemy import text
from app.core.db import engine, get_db, healthcheck_db


def test_engine_created():
    """Valida que engine foi criado"""
    assert engine is not None
    assert engine.url.database is not None


def test_get_db_yields_session():
    """Valida que get_db retorna sessão"""
    gen = get_db()
    db = next(gen)
    assert db is not None
    assert hasattr(db, "execute")
    assert hasattr(db, "commit")
    assert hasattr(db, "rollback")
    # Fechar sessão
    try:
        next(gen)
    except StopIteration:
        pass


def test_healthcheck_db_success():
    """Valida healthcheck do banco"""
    health = healthcheck_db()
    assert health["status"] == "healthy"
    assert health["pgcrypto_enabled"] is True  # RDB1
    assert health["alembic_version"] is not None


@pytest.mark.integration
def test_database_timezone_utc():
    """Valida que timezone é UTC (RDB3)"""
    with engine.connect() as conn:
        result = conn.execute(text("SHOW timezone"))
        timezone = result.scalar()
        assert timezone.upper() == "UTC"


@pytest.mark.integration
def test_database_can_generate_uuid():
    """Valida que gen_random_uuid() funciona (RDB1, RDB2)"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT gen_random_uuid()"))
        uuid_value = result.scalar()
        assert uuid_value is not None
        assert len(str(uuid_value)) == 36  # UUID v4 format
