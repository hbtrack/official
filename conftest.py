# conftest.py — configura path e Django para o pytest
import os
import sys
import socket
import pathlib

import pytest

# Adiciona src/, raiz (config/) e scripts/ ao sys.path
_ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

# tools/diagnostics não existe ainda (módulo pendente, fora do escopo atual)
collect_ignore = ["tests/tools/diagnostics/test_diagnose_connectivity.py"]


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
    """Skip integration tests if PostgreSQL is not available."""
    if not _postgres_available():
        pytest.skip(
            "PostgreSQL não disponível. "
            "Inicie com: docker compose -f infra/docker-compose.yml up -d postgres"
        )
    # pytest-django (_django_db_helper) handles setup_test_environment() and setup_databases()
