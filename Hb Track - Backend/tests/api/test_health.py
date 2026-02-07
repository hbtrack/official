"""
Testes do endpoint /api/v1/health.
Ref: FASE 2 — Núcleo do backend
"""


def test_health_endpoint_returns_ok(client):
    """Verifica que GET /api/v1/health retorna status healthy."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data or "db" in data
