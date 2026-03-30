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


@pytest.fixture(autouse=True, scope="session")
def _patch_flush_allow_cascade():
    """Necessário para PostgreSQL: TRUNCATE no teardown transacional falha com
    FeatureNotSupported quando tabelas intermediárias (auth_user_groups,
    auth_user_user_permissions) têm FK sem CASCADE.
    Django define allow_cascade=False por padrão quando available_apps is None.
    """
    try:
        from django.core.management.commands import flush as flush_module
    except ImportError:
        # Django não instalado (ex: jobs de CI de governança) — fixture no-op
        yield
        return

    original_handle = flush_module.Command.handle

    def _handle_with_cascade(self, **options):
        options["allow_cascade"] = True
        return original_handle(self, **options)

    flush_module.Command.handle = _handle_with_cascade
    yield
    flush_module.Command.handle = original_handle


@pytest.fixture(scope="session")
def django_db_setup():
    """Override pytest-django database setup.

    Most tests in this repo are contract/governance tests that don't need DB.
    Tests requiring DB (schemathesis, integration) should skip gracefully
    or be run with explicit infrastructure: docker compose up postgres.
    """
    if not _postgres_available():
        pytest.skip(
            "PostgreSQL não disponível. "
            "Inicie com: docker compose -f infra/docker-compose.yml up -d postgres"
        )
