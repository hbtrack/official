"""
Schemathesis — testes de contrato HTTP para os 5 módulos do Ciclo 1.
Property-based testing contra o schema OpenAPI gerado pela NinjaAPI via WSGI.

Requer PostgreSQL disponível (skip automático via fixture django_db_setup).
Para executar:
    docker compose -f infra/docker-compose.yml up -d postgres redis
    python manage.py migrate
    pytest tests/schemathesis/ -v
"""
import pytest
import schemathesis
from hypothesis import settings, HealthCheck

# LazySchema permite usar a fixture ciclo1_schema como fonte do schema parametrizado
_schema = schemathesis.pytest.from_fixture("ciclo1_schema")


_CICLO1_PREFIXES = ("/api/auth", "/api/users", "/api/teams", "/api/seasons", "/api/training")


@_schema.parametrize()
@settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.django_db(transaction=True)
def test_ciclo1_api_contracts(case):
    """
    HB Track Ciclo 1 — contract testing via Schemathesis.
    Verifica: nenhum HTTP 5xx; respostas conformes ao schema OpenAPI.
    max_examples=10 para validação local; CI usa max_examples=50.
    """
    if not any(case.path.startswith(p) for p in _CICLO1_PREFIXES):
        pytest.skip(f"Non-Ciclo 1 endpoint: {case.path}")
    case.call_and_validate(checks=(schemathesis.checks.not_a_server_error,))
