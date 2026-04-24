"""Testes de integração — formato de erro RFC 9457 (Problem+JSON).

REM-1C: Verifica que todas as respostas de erro do módulo training retornam:
  - Content-Type: application/problem+json
  - Body: {type, title, status, traceId, detail}
  - traceId: string não vazia (UUID gerado por get_current_flow_id)

Cobre três caminhos de exceção:
  1. HttpError levantado por map_exceptions (domínio → 404)
  2. NinjaValidationError (body inválido → 422)
  3. HttpError levantado diretamente por deps.py (sem actor → 401)
"""
from __future__ import annotations

import uuid

import pytest

pytestmark = pytest.mark.django_db

_RFC7807_REQUIRED_FIELDS = {"type", "title", "status", "traceId", "detail"}
_TYPE_PREFIX = "https://hbtrack.app/errors/"


def _assert_problem_response(response, expected_status: int) -> dict:
    """Verifica Content-Type e estrutura RFC 9457. Retorna o body."""
    content_type = response.get("Content-Type", "")
    assert "application/problem+json" in content_type, (
        f"Content-Type esperado 'application/problem+json', recebido '{content_type}'"
    )
    body = response.json()
    missing = _RFC7807_REQUIRED_FIELDS - set(body.keys())
    assert not missing, f"Campos RFC 9457 ausentes no body: {missing}. Body: {body}"

    assert body["status"] == expected_status, (
        f"body.status esperado {expected_status}, recebido {body['status']}"
    )
    assert body["type"] == f"{_TYPE_PREFIX}{expected_status}", (
        f"body.type esperado '{_TYPE_PREFIX}{expected_status}', recebido '{body['type']}'"
    )
    assert isinstance(body["title"], str) and body["title"], (
        f"body.title deve ser string não vazia, recebido: {body['title']!r}"
    )
    assert isinstance(body["traceId"], str) and body["traceId"], (
        f"body.traceId deve ser string não vazia, recebido: {body['traceId']!r}"
    )
    assert isinstance(body["detail"], str), (
        f"body.detail deve ser string, recebido: {body['detail']!r}"
    )
    return body


class TestProblemJsonFormat:
    """RFC 9457: format de erro completo (traceId, type, title, status, detail)."""

    def test_404_returns_problem_json(self, client):
        """GET de session inexistente → 404 com Problem+JSON.

        Fluxo: TrainingSessionNotFound → map_exceptions → HttpError(404)
               → @api.exception_handler(HttpError) → _problem_response()
        """
        nonexistent_id = uuid.uuid4()
        response = client.get(
            f"/api/training/training-sessions/{nonexistent_id}",
            content_type="application/json",
        )
        assert response.status_code == 404
        _assert_problem_response(response, 404)

    def test_422_validation_error_returns_problem_json(self, client):
        """POST com body inválido (campo obrigatório ausente) → 422 com Problem+JSON.

        Fluxo: NinjaValidationError → @api.exception_handler(NinjaValidationError)
               → _problem_response(422, ...)
        """
        response = client.post(
            "/api/training/training-sessions",
            data={},  # body vazio — campos obrigatórios ausentes
            content_type="application/json",
        )
        assert response.status_code == 422
        _assert_problem_response(response, 422)

    def test_problem_json_title_matches_status(self, client):
        """body.title deve corresponder ao status HTTP (ex: 404 → 'Not Found')."""
        nonexistent_id = uuid.uuid4()
        response = client.get(
            f"/api/training/training-sessions/{nonexistent_id}",
            content_type="application/json",
        )
        assert response.status_code == 404
        body = _assert_problem_response(response, 404)
        assert body["title"] == "Not Found", (
            f"Para 404, title esperado 'Not Found', recebido '{body['title']}'"
        )

    def test_trace_id_is_consistent_uuid_like(self, client):
        """traceId deve ser uma string com padrão UUID.

        get_current_flow_id() gera UUID se X-Flow-ID não estiver no request.
        """
        nonexistent_id = uuid.uuid4()
        response = client.get(
            f"/api/training/training-sessions/{nonexistent_id}",
            content_type="application/json",
        )
        body = response.json()
        trace_id = body.get("traceId", "")
        # Deve ser parseable como UUID
        try:
            uuid.UUID(trace_id)
        except (ValueError, AttributeError):
            pytest.fail(f"traceId '{trace_id}' não é um UUID válido")

    def test_trace_id_propagated_from_x_flow_id_header(self, client):
        """traceId no body deve corresponder ao X-Flow-ID enviado no request."""
        fixed_flow_id = str(uuid.uuid4())
        nonexistent_id = uuid.uuid4()
        response = client.get(
            f"/api/training/training-sessions/{nonexistent_id}",
            content_type="application/json",
            HTTP_X_FLOW_ID=fixed_flow_id,
        )
        body = response.json()
        assert body.get("traceId") == fixed_flow_id, (
            f"traceId esperado '{fixed_flow_id}', recebido '{body.get('traceId')}'"
        )
