"""
Testes de integração para health endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_health_endpoint_returns_200():
    """Valida que /health retorna 200"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.integration
def test_health_endpoint_structure():
    """Valida estrutura do response de /health"""
    response = client.get("/api/v1/health")
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "database" in data

    # Validar database health
    assert data["database"]["status"] == "healthy"
    assert data["database"]["pgcrypto_enabled"] is True  # RDB1
    assert data["database"]["alembic_version"] is not None


@pytest.mark.integration
def test_liveness_endpoint():
    """Valida /health/liveness"""
    response = client.get("/api/v1/health/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.integration
def test_readiness_endpoint():
    """Valida /health/readiness"""
    response = client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_root_endpoint():
    """Valida endpoint raiz /"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs" in response.json()
