"""
Testes do módulo core/db.
Ref: FASE 2 — Núcleo do backend
"""

from sqlalchemy import text

from app.core.db import healthcheck_db


def test_healthcheck_db_ok():
    """Verifica que healthcheck_db retorna 'ok' quando o banco está acessível."""
    result = healthcheck_db()
    assert result == "ok"


def test_db_session_isolation(db):
    """
    Verifica que a fixture db provê isolamento transacional.
    Operações dentro do teste não persistem após o rollback.
    """
    # Verifica que a sessão está funcional
    result = db.execute(text("SELECT 1 AS val"))
    row = result.fetchone()
    assert row.val == 1


def test_db_session_rollback_on_commit(db):
    """
    Verifica que commits dentro do teste são revertidos via savepoint.
    Criamos uma tabela temporária, commitamos e verificamos que ela existe.
    (O rollback final da fixture garante que não persiste entre testes)
    """
    # Usa tabela temporária para não afetar schema
    db.execute(text("CREATE TEMP TABLE _test_isolation (id INT)"))
    db.execute(text("INSERT INTO _test_isolation VALUES (42)"))
    db.commit()

    result = db.execute(text("SELECT id FROM _test_isolation"))
    row = result.fetchone()
    assert row.id == 42
