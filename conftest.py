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

# Containers Testcontainers levantados nesta sessão (escopo session)
_tc_postgres = None
_tc_redis = None


def _postgres_available() -> bool:
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5432"))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
        return True
    except OSError:
        return False


def _try_start_testcontainers() -> bool:
    """Tenta subir Postgres + Redis via Testcontainers. Retorna True se OK."""
    global _tc_postgres, _tc_redis
    try:
        from testcontainers.postgres import PostgresContainer
        from testcontainers.redis import RedisContainer
    except ImportError:
        return False

    try:
        pg = PostgresContainer("postgres:16")
        pg = pg.with_env("POSTGRES_DB", "hbtrack_test")
        pg = pg.with_env("POSTGRES_USER", "hbtrack")
        pg = pg.with_env("POSTGRES_PASSWORD", "testpassword")
        pg.start()
        _tc_postgres = pg

        rd = RedisContainer("redis:7-alpine")
        rd.start()
        _tc_redis = rd

        # Expor vars para Django / pytest-django
        os.environ.setdefault("DB_NAME", "hbtrack_test")
        os.environ.setdefault("DB_USER", "hbtrack")
        os.environ.setdefault("DB_PASSWORD", "testpassword")
        os.environ["DB_HOST"] = pg.get_container_host_ip()
        os.environ["DB_PORT"] = str(pg.get_exposed_port(5432))
        os.environ["DATABASE_URL"] = (
            f"postgres://hbtrack:testpassword@"
            f"{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/hbtrack_test"
        )
        redis_port = rd.get_exposed_port(6379)
        os.environ["REDIS_URL"] = f"redis://localhost:{redis_port}/0"
        os.environ["CELERY_BROKER_URL"] = f"redis://localhost:{redis_port}/1"
        os.environ["CELERY_RESULT_BACKEND"] = f"redis://localhost:{redis_port}/2"
        return True
    except Exception:
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

    Ordem de preferência:
    1. Postgres disponível via socket (docker compose up ou CI service)
    2. Testcontainers — sobe Postgres + Redis automaticamente
    3. Skip — nenhuma infra disponível
    """
    if _postgres_available():
        return

    if _try_start_testcontainers():
        return

    pytest.skip(
        "PostgreSQL não disponível e Testcontainers falhou. "
        "Inicie com: docker compose -f infra/docker-compose.yml up -d postgres"
    )


def pytest_sessionfinish(session, exitstatus):
    """Parar containers Testcontainers ao final da sessão."""
    if _tc_redis is not None:
        try:
            _tc_redis.stop()
        except Exception:
            pass
    if _tc_postgres is not None:
        try:
            _tc_postgres.stop()
        except Exception:
            pass
