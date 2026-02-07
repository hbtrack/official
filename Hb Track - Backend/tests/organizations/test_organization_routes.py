"""
Testes de integração das rotas de Organization.

Usa fixture `client` que faz override de get_db e get_current_user
para compartilhar a sessão de teste com isolamento transacional.
"""
import pytest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.db import get_db
from app.core.auth import get_current_user, MockUser


class TestListOrganizations:
    """Testes GET /v1/organizations."""

    def test_list_organizations_returns_200(self, client, organization):
        """Lista organizações com sucesso."""
        response = client.get("/v1/organizations")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert data["total"] >= 1


class TestCreateOrganization:
    """Testes POST /v1/organizations."""

    def test_create_organization_returns_201(self, client, owner_user_id):
        """Criar organização retorna 201."""
        payload = {
            "name": f"Nova Org {uuid4().hex[:8]}",
        }

        response = client.post("/v1/organizations", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert "id" in data


class TestGetOrganization:
    """Testes GET /v1/organizations/{id}."""

    def test_get_organization_returns_200(self, client, organization):
        """Buscar organização existente."""
        response = client.get(f"/v1/organizations/{organization.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(organization.id)
        assert data["name"] == organization.name

    def test_get_organization_not_found_returns_404(self, client):
        """Buscar organização inexistente."""
        fake_id = uuid4()
        response = client.get(f"/v1/organizations/{fake_id}")

        assert response.status_code == 404


class TestUpdateOrganization:
    """Testes PATCH /v1/organizations/{id}."""

    def test_update_organization_returns_200(self, client, organization):
        """Atualizar organização com sucesso."""
        payload = {"name": "Nome Atualizado Via API"}

        response = client.patch(
            f"/v1/organizations/{organization.id}",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nome Atualizado Via API"


@pytest.fixture
def client(db, owner_user_id, organization):
    """
    TestClient com override de get_db E get_current_user.
    
    Esta fixture cria um client com os IDs reais das fixtures.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    async def override_get_current_user():
        """Retorna MockUser com IDs reais das fixtures."""
        return MockUser(
            user_id=owner_user_id,
            person_id=str(uuid4()),
            membership_id=str(uuid4()),
            organization_id=str(organization.id),
            role="coordenador",
            permissions=["*"],
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
