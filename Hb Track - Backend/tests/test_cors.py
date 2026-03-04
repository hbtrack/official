"""
tests/test_cors.py — Suíte mínima de testes CORS (AR_235)

Cobre preflight, request real, origem bloqueada, fail-fast e strip de env.
Rota alvo: GET /api/v1/health/liveness (público, sem banco).

Nota: Usa mini-app isolada (sem startup DB) conforme Nota do Arquiteto AR_235 —
"Se app não tem factory create_app, usar TestClient com lifespan=False ou mock do startup."
"""
from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixture — mini-app CORS isolada (sem dependência de banco)
# ---------------------------------------------------------------------------

_TEST_ENV = {
    "CORS_ORIGINS": "http://allowed.test",
    "CORS_ALLOW_CREDENTIALS": "true",
    "CORS_ALLOW_HEADERS": "Authorization,Content-Type,Accept,X-CSRF-Token,X-Request-ID,X-Organization-ID",
    "CORS_ALLOW_METHODS": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
    "CORS_EXPOSE_HEADERS": "X-Request-ID",
    "CORS_MAX_AGE": "600",
    "ENV": "test",
    "JWT_SECRET": "test_secret_for_cors_tests",
}


@pytest.fixture(scope="module")
def cors_client():
    """
    App mínima com CORS configurado via Settings recarregadas do env de teste.
    Sem startup DB — seguro para CI (AR_235 Nota do Arquiteto).
    """
    with patch.dict("os.environ", _TEST_ENV, clear=False):
        import app.core.config as cfg_module
        importlib.reload(cfg_module)
        test_settings = cfg_module.settings

        mini_app = FastAPI()
        mini_app.add_middleware(
            CORSMiddleware,
            allow_origins=test_settings.cors_origins_list,
            allow_credentials=test_settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=test_settings.cors_allow_methods_list,
            allow_headers=test_settings.cors_allow_headers_list,
            expose_headers=test_settings.cors_expose_headers_list,
            max_age=test_settings.CORS_MAX_AGE,
            **(
                {"allow_origin_regex": test_settings.CORS_ALLOW_ORIGIN_REGEX}
                if test_settings.CORS_ALLOW_ORIGIN_REGEX
                else {}
            ),
        )

        @mini_app.get("/api/v1/health/liveness")
        async def liveness():
            return {"status": "alive"}

        client = TestClient(mini_app)
        yield client

        # Restore: reload cfg sem patch para não vazar estado entre módulos
        importlib.reload(cfg_module)


# ---------------------------------------------------------------------------
# AC-001 — Preflight de origem permitida
# ---------------------------------------------------------------------------

def test_preflight_allowed_origin(cors_client):
    """Preflight de origem permitida retorna headers CORS completos."""
    response = cors_client.options(
        "/api/v1/health/liveness",
        headers={
            "Origin": "http://allowed.test",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, X-CSRF-Token",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://allowed.test"
    assert "GET" in response.headers.get("access-control-allow-methods", "")
    assert "authorization" in response.headers.get("access-control-allow-headers", "").lower()
    assert "x-csrf-token" in response.headers.get("access-control-allow-headers", "").lower()
    assert response.headers.get("access-control-allow-credentials") == "true"


# ---------------------------------------------------------------------------
# AC-002 — Preflight de origem bloqueada
# ---------------------------------------------------------------------------

def test_preflight_blocked_origin(cors_client):
    """Preflight de origem não-permitida não retorna Access-Control-Allow-Origin."""
    response = cors_client.options(
        "/api/v1/health/liveness",
        headers={
            "Origin": "http://evil.test",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    # Starlette responde sem o header (não necessariamente 403)
    assert "access-control-allow-origin" not in response.headers


# ---------------------------------------------------------------------------
# AC-003 — Request real com origem permitida
# ---------------------------------------------------------------------------

def test_real_request_allowed_origin(cors_client):
    """Request real GET com Origin permitida retorna access-control-allow-origin correto."""
    response = cors_client.get(
        "/api/v1/health/liveness",
        headers={
            "Origin": "http://allowed.test",
            "Authorization": "Bearer dummy_for_cors_test",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://allowed.test"


# ---------------------------------------------------------------------------
# AC-004 — Fail-fast: credentials=True + wildcard
# ---------------------------------------------------------------------------

def test_credentials_wildcard_fail_fast():
    """Settings com credentials=True + wildcard deve levantar ValidationError/ValueError."""
    from pydantic import ValidationError

    from app.core.config import Settings

    with pytest.raises((ValidationError, ValueError)):
        Settings(
            CORS_ORIGINS="*",
            CORS_ALLOW_CREDENTIALS=True,
            JWT_SECRET="test_secret",
        )


# ---------------------------------------------------------------------------
# AC-005 — cors_origins_list: strip + filtro de vazios
# ---------------------------------------------------------------------------

def test_origins_read_from_env_with_spaces():
    """cors_origins_list faz strip e filtra itens vazios (trailing comma + espaços)."""
    from app.core.config import Settings

    s = Settings(
        CORS_ORIGINS="http://a.test, http://b.test,",
        CORS_ALLOW_CREDENTIALS=False,
        JWT_SECRET="test_secret",
    )
    assert s.cors_origins_list == ["http://a.test", "http://b.test"]
