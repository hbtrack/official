import pytest
from django.test import Client, RequestFactory
from ninja.errors import AuthenticationError

from identity_access.infrastructure.jwt_adapter import JWTAdapter
from identity_access.middleware import HTTPBearer


def test_http_bearer_returns_none_when_jwt_verification_crashes(monkeypatch):
    request = RequestFactory().get("/api/auth/me")

    def _boom(self, token):
        raise RuntimeError("JWT verification backend unavailable")

    monkeypatch.setattr(JWTAdapter, "verify_access_token", _boom)

    assert HTTPBearer().authenticate(request, "Bearer broken") is None


def test_verify_access_token_returns_none_when_key_config_missing(monkeypatch):
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)

    assert JWTAdapter().verify_access_token("not-a-jwt") is None


def test_auth_me_with_bearer_and_missing_jwt_config_returns_401_not_500(monkeypatch):
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)

    response = Client().get("/api/auth/me", HTTP_AUTHORIZATION="Bearer not-a-jwt")

    assert response.status_code == 401


def test_http_bearer_raises_contract_detail_when_token_is_invalid(monkeypatch):
    request = RequestFactory().get("/api/auth/me", HTTP_AUTHORIZATION="Bearer broken")

    monkeypatch.setattr(JWTAdapter, "verify_access_token", lambda self, token: None)

    with pytest.raises(AuthenticationError, match="Token ausente ou inválido."):
        HTTPBearer()(request)


def test_auth_me_invalid_bearer_returns_problem_json_detail(monkeypatch):
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)

    response = Client().get("/api/auth/me", HTTP_AUTHORIZATION="Bearer not-a-jwt")

    assert response.status_code == 401
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.json()["detail"] == "Token ausente ou inválido."


def test_auth_logout_invalid_bearer_returns_problem_json_detail(monkeypatch):
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)

    response = Client().post("/api/auth/logout", HTTP_AUTHORIZATION="Bearer not-a-jwt")

    assert response.status_code == 401
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.json()["detail"] == "Token ausente ou inválido."
