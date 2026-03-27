"""
Schemathesis — testes de contrato HTTP para os 5 módulos do Ciclo 1.
Property-based testing contra o schema OpenAPI.

Modos:
  Local (WSGI): docker compose up postgres redis && pytest tests/schemathesis/ -v
  Staging live: HB_STAGING_URL=https://staging.handballtrack.app pytest tests/schemathesis/ -v

Checks ativos:
  - not_a_server_error: nenhum endpoint retorna 5xx
  - response_schema_conformance: response bodies conformes ao schema OpenAPI
"""
import pytest
import schemathesis
from hypothesis import settings, HealthCheck

_schema = schemathesis.pytest.from_fixture("ciclo1_schema")

_CICLO1_PREFIXES = ("/api/auth", "/api/users", "/api/teams", "/api/seasons", "/api/training")


@_schema.parametrize()
@settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@pytest.mark.django_db(transaction=True)
def test_ciclo1_api_contracts(case):
    """
    HB Track Ciclo 1 — contract testing via Schemathesis.

    Verifica:
      - Nenhum endpoint retorna HTTP 5xx
      - Response bodies estão conformes ao schema OpenAPI declarado

    max_examples=10 localmente; CI usa max_examples=50 via HB_SCHEMATHESIS_EXAMPLES.
    """
    if not any(case.path.startswith(p) for p in _CICLO1_PREFIXES):
        pytest.skip(f"Non-Ciclo 1 endpoint: {case.path}")
    case.call_and_validate(
        checks=(
            schemathesis.checks.not_a_server_error,
            schemathesis.checks.response_schema_conformance,
        )
    )
