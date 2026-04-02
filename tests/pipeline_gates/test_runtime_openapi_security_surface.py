from __future__ import annotations

import django


django.setup()

from config.urls import api


def test_runtime_openapi_declares_httpbearer_for_protected_operations():
    schema = api.get_openapi_schema()

    assert schema["components"]["securitySchemes"]["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
    }
    assert schema["paths"]["/api/auth/me"]["get"]["security"] == [{"HTTPBearer": []}]
    assert schema["paths"]["/api/users"]["get"]["security"] == [{"HTTPBearer": []}]


def test_runtime_openapi_keeps_public_auth_endpoints_without_security():
    schema = api.get_openapi_schema()

    assert "security" not in schema["paths"]["/api/auth/login"]["post"]
    assert "security" not in schema["paths"]["/api/auth/refresh"]["post"]
