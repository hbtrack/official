"""
conftest para testes de integração do módulo training.
Requer PostgreSQL em execução (localhost:5433, ou DB_HOST:DB_PORT).
Pula graciosamente quando o banco não está disponível.
"""
import os
import socket
import pytest


def _postgres_available() -> bool:
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5433"))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
        return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def django_db_setup():
    """Pula testes de integração se PostgreSQL não estiver acessível."""
    if not _postgres_available():
        pytest.skip(
            "PostgreSQL não disponível. "
            "Inicie com: docker compose -f infra/docker-compose.yml up -d postgres"
        )
    from django.test.utils import setup_test_environment
    setup_test_environment()
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=0)
    old_config = runner.setup_databases()
    yield
    runner.teardown_databases(old_config)
