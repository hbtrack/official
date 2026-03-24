"""
Fixtures Schemathesis para Ciclo 1 — carregadas apenas no momento de execução,
não durante a coleta, para evitar hang no import.
"""
import os
import pytest
import schemathesis


@pytest.fixture(scope="session")
def ciclo1_wsgi_app():
    """WSGI app do Django — carregado após setup do pytest-django."""
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()


@pytest.fixture(scope="session")
def ciclo1_schema(ciclo1_wsgi_app):
    """
    Schema Schemathesis filtrado para os 5 módulos do Ciclo 1.
    Requer PostgreSQL disponível (skip automático se não houver).
    """
    schema = schemathesis.openapi.from_wsgi("/api/openapi.json", ciclo1_wsgi_app)
    return schema.include(path_regex=r"^/api/(auth|users|teams|seasons|training)/")
