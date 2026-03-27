"""
Fixtures Schemathesis para Ciclo 1.

Dois modos de execução:
- WSGI local (padrão): testa contra Django em memória, sem servidor live.
- Live staging: ativado quando HB_STAGING_URL está definida — testa contra URL real.
"""
import os
import pytest
import schemathesis

_CICLO1_PATH_REGEX = r"^/api/(auth|users|teams|seasons|training)/"


@pytest.fixture(scope="session")
def ciclo1_wsgi_app():
    """WSGI app do Django — carregado após setup do pytest-django."""
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()


@pytest.fixture(scope="session")
def ciclo1_schema(ciclo1_wsgi_app):
    """
    Schema Schemathesis filtrado para os 5 módulos do Ciclo 1.

    Se HB_STAGING_URL estiver definida, aponta para o servidor live.
    Caso contrário usa WSGI local (requer PostgreSQL disponível).
    """
    staging_url = os.environ.get("HB_STAGING_URL", "").strip()
    if staging_url:
        schema = schemathesis.openapi.from_url(
            staging_url.rstrip("/") + "/api/openapi.json",
            base_url=staging_url.rstrip("/"),
        )
    else:
        schema = schemathesis.openapi.from_wsgi("/api/openapi.json", ciclo1_wsgi_app)
    return schema.include(path_regex=_CICLO1_PATH_REGEX)
