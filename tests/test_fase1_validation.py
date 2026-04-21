"""
Testes de validação — FASE 1
Cobertura: JWT 401, X-Flow-ID, /health, CORS preflight, constraint violation 422.
"""
import pytest
from django.test import Client


@pytest.mark.django_db
class TestHealthEndpoint:
    """1.6 — /health retorna 200."""

    def test_health_returns_200(self):
        client = Client()
        response = client.get("/health")
        assert response.status_code == 200, f"Esperado 200, got {response.status_code}"

    def test_health_response_has_status_ok(self):
        client = Client()
        response = client.get("/health")
        data = response.json()
        assert data.get("status") == "ok"
        assert "buildSha" in data

    def test_health_response_reports_build_sha(self, monkeypatch):
        monkeypatch.setenv("HB_BUILD_SHA", "test-build-sha")
        client = Client()
        response = client.get("/health")
        data = response.json()
        assert data.get("buildSha") == "test-build-sha"


@pytest.mark.django_db
class TestFlowIDMiddleware:
    """1.4 — X-Flow-ID presente em todos os responses."""

    def test_response_has_x_flow_id_header(self):
        client = Client()
        response = client.get("/health")
        assert "X-Flow-ID" in response, "Header X-Flow-ID ausente no response"

    def test_flow_id_propagated_when_sent_in_request(self):
        client = Client()
        custom_id = "test-flow-id-abc123"
        response = client.get("/health", HTTP_X_FLOW_ID=custom_id)
        assert response["X-Flow-ID"] == custom_id, (
            f"flow_id não propagado: esperado '{custom_id}', "
            f"got '{response.get('X-Flow-ID')}'"
        )

    def test_flow_id_generated_when_not_sent(self):
        client = Client()
        response = client.get("/health")
        flow_id = response.get("X-Flow-ID", "")
        assert len(flow_id) == 36, (
            f"X-Flow-ID gerado deve ser UUID v4 (36 chars), got '{flow_id}'"
        )


@pytest.mark.django_db
class TestJWT401:
    """1.3 — Endpoint protegido retorna 401 sem token."""

    def test_protected_endpoint_returns_401_without_token(self):
        client = Client()
        # Django Ninja registra as rotas sem trailing slash
        response = client.get("/api/users")
        assert response.status_code == 401, (
            f"Esperado 401 em endpoint protegido sem token, got {response.status_code}"
        )

    def test_protected_endpoint_returns_401_with_wrong_token(self):
        client = Client()
        response = client.get(
            "/api/users",
            HTTP_AUTHORIZATION="Bearer token-invalido",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestCORSPreflight:
    """1.5 — Preflight OPTIONS de localhost retorna CORS headers."""

    def test_cors_preflight_options(self):
        client = Client()
        response = client.options(
            "/api/users",
            HTTP_ORIGIN="http://localhost:5173",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization",
        )
        # django-cors-headers deve retornar 200 ou 204 para preflight válido
        assert response.status_code in (200, 204), (
            f"CORS preflight falhou: {response.status_code}"
        )
        assert "Access-Control-Allow-Origin" in response, (
            "Header Access-Control-Allow-Origin ausente no preflight"
        )


@pytest.mark.django_db
class TestConstraintViolation:
    """
    2.2 — Violations de constraint retornam 422 antes de chegar à camada de aplicação.
    Testa que validação Pydantic de schema captura valores fora do range permitido.
    """

    def test_week_number_out_of_range_returns_422(self):
        """week_number > 32767 deve ser rejeitado com 422 (SmallIntegerField)."""
        import json
        client = Client()
        # week_number fora do range de SmallIntegerField (max 32767)
        response = client.post(
            "/api/training/microcycles",
            data=json.dumps({
                "organization_id": "00000000-0000-0000-0000-000000000001",
                "mesocycle_id": "00000000-0000-0000-0000-000000000002",
                "week_number": 9_999_999,
                "started_at": "2025-01-01T00:00:00Z",
                "ended_at": "2025-01-07T00:00:00Z",
            }),
            content_type="application/json",
        )
        assert response.status_code == 422, (
            f"Esperado 422 para week_number fora do range, got {response.status_code}"
        )

    def test_planned_sessions_count_out_of_range_returns_422(self):
        """planned_sessions_count > 32767 deve ser rejeitado com 422."""
        import json
        client = Client()
        response = client.post(
            "/api/training/microcycles",
            data=json.dumps({
                "organization_id": "00000000-0000-0000-0000-000000000001",
                "mesocycle_id": "00000000-0000-0000-0000-000000000002",
                "week_number": 1,
                "started_at": "2025-01-01T00:00:00Z",
                "ended_at": "2025-01-07T00:00:00Z",
                "planned_sessions_count": 99_999,
            }),
            content_type="application/json",
        )
        assert response.status_code == 422, (
            f"Esperado 422 para planned_sessions_count fora do range, got {response.status_code}"
        )

    def test_week_number_zero_returns_422(self):
        """week_number = 0 invalida a regra de domínio (>= 1)."""
        import json
        client = Client()
        response = client.post(
            "/api/training/microcycles",
            data=json.dumps({
                "organization_id": "00000000-0000-0000-0000-000000000001",
                "mesocycle_id": "00000000-0000-0000-0000-000000000002",
                "week_number": 0,
                "started_at": "2025-01-01T00:00:00Z",
                "ended_at": "2025-01-07T00:00:00Z",
            }),
            content_type="application/json",
        )
        assert response.status_code == 422, (
            f"Esperado 422 para week_number=0, got {response.status_code}"
        )
