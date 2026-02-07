"""
Helper canônico para asserts de violações Postgres.

Encapsula a extração de SQLSTATE e constraint_name de exceções
IntegrityError, abstraindo as diferenças entre psycopg2 e asyncpg.
"""

from typing import Optional
from sqlalchemy.exc import IntegrityError


def assert_pg_constraint_violation(
    exc_info,
    expected_sqlstate: str,
    expected_constraint: str,
    message: Optional[str] = None,
) -> None:
    """
    Verifica que uma IntegrityError contém o SQLSTATE e constraint_name esperados.

    Args:
        exc_info: pytest.ExceptionInfo[IntegrityError] do pytest.raises()
        expected_sqlstate: SQLSTATE esperado (ex: "23514" para CHECK, "23505" para UNIQUE)
        expected_constraint: Nome da constraint esperada
        message: Mensagem opcional para falha de assert

    Example:
        >>> with pytest.raises(IntegrityError) as exc_info:
        ...     await async_db.flush()
        >>> assert_pg_constraint_violation(
        ...     exc_info,
        ...     "23514",
        ...     "ck_training_sessions_focus_total_sum"
        ... )

    Raises:
        AssertionError: Se SQLSTATE ou constraint_name não baterem

    Notes:
        - Para psycopg2: usa orig.diag.constraint_name
        - Para asyncpg: usa orig.__cause__.constraint_name
        - Ambos usam orig.pgcode para SQLSTATE
    """
    orig = exc_info.value.orig
    
    # Verifica SQLSTATE (comum em ambos drivers)
    actual_sqlstate = orig.pgcode
    if actual_sqlstate != expected_sqlstate:
        msg = message or f"Expected SQLSTATE {expected_sqlstate}, got {actual_sqlstate}"
        raise AssertionError(msg)
    
    # Extrai constraint_name (diferente entre drivers)
    constraint_name = _extract_constraint_name(orig)
    
    if constraint_name != expected_constraint:
        msg = message or f"Expected constraint '{expected_constraint}', got '{constraint_name}'"
        raise AssertionError(msg)


def _extract_constraint_name(orig) -> str:
    """
    Extrai constraint_name do erro original, abstraindo diferenças entre drivers.

    Args:
        orig: Objeto de erro original (psycopg2.Error ou asyncpg.PostgresError)

    Returns:
        Nome da constraint ou string vazia se não encontrada

    Notes:
        - psycopg2: orig.diag.constraint_name
        - asyncpg: orig.__cause__.constraint_name
    """
    # Tenta psycopg2 (sync)
    if hasattr(orig, 'diag') and hasattr(orig.diag, 'constraint_name'):
        return orig.diag.constraint_name or ""
    
    # Tenta asyncpg (async)
    if hasattr(orig, '__cause__') and hasattr(orig.__cause__, 'constraint_name'):
        return orig.__cause__.constraint_name or ""
    
    return ""
