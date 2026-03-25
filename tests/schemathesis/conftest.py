"""
Fixtures Schemathesis para Ciclo 1 — carregadas apenas no momento de execução,
não durante a coleta, para evitar hang no import.
"""
import os
import pytest
import schemathesis


@pytest.fixture(autouse=True, scope="session")
def _patch_flush_allow_cascade():
    """Patching necessário para PostgreSQL: TRUNCATE no teardown transacional falha
    com FeatureNotSupported quando auth_user_groups referencia auth_group sem CASCADE.
    Django define allow_cascade=False por padrão quando available_apps is None.
    """
    from django.core.management.commands import flush as flush_module
    original_handle = flush_module.Command.handle

    def _handle_with_cascade(self, **options):
        options["allow_cascade"] = True
        return original_handle(self, **options)

    flush_module.Command.handle = _handle_with_cascade
    yield
    flush_module.Command.handle = original_handle


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
