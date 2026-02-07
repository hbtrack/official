"""
Testes das rotas de Athletes.
Ref: R12, R13, R25/R26
"""
import pytest
from uuid import uuid4


class TestAthleteRoutesList:
    """Testes GET /athletes."""

    def test_list_athletes_returns_200(self, client, athlete):
        """Listar atletas retorna 200."""
        response = client.get("/v1/athletes")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_athletes_pagination(self, client, athlete):
        """Paginação funciona corretamente."""
        response = client.get("/v1/athletes?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10


class TestAthleteRoutesCreate:
    """Testes POST /athletes."""

    def test_create_athlete_returns_201(self, client, organization, membership):
        """Criar atleta retorna 201."""
        payload = {
            "organization_id": str(organization.id),
            "created_by_membership_id": str(membership.id),
            "full_name": "Nova Atleta",
        }
        response = client.post("/v1/athletes", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Nova Atleta"
        assert data["state"] == "ativa"

    def test_create_athlete_with_optional_fields(self, client, organization, membership):
        """Criar atleta com campos opcionais."""
        payload = {
            "organization_id": str(organization.id),
            "created_by_membership_id": str(membership.id),
            "full_name": "Atleta Completa",
            "nickname": "AC",
            "birth_date": "2007-06-15",
            "position": "pivô",
        }
        response = client.post("/v1/athletes", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["nickname"] == "AC"
        assert data["position"] == "pivô"

    def test_create_athlete_missing_required_field(self, client, organization):
        """Criar atleta sem campo obrigatório retorna 422."""
        payload = {
            "organization_id": str(organization.id),
            # missing full_name
        }
        response = client.post("/v1/athletes", json=payload)

        assert response.status_code == 422


class TestAthleteRoutesGetById:
    """Testes GET /athletes/{id}."""

    def test_get_athlete_returns_200(self, client, athlete):
        """Buscar atleta por ID retorna 200."""
        response = client.get(f"/v1/athletes/{athlete.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(athlete.id)

    def test_get_athlete_not_found_returns_404(self, client):
        """Buscar atleta inexistente retorna 404."""
        fake_id = uuid4()
        response = client.get(f"/v1/athletes/{fake_id}")

        assert response.status_code == 404


class TestAthleteRoutesUpdate:
    """Testes PATCH /athletes/{id}."""

    def test_update_athlete_returns_200(self, client, athlete):
        """Atualizar atleta retorna 200."""
        payload = {"full_name": "Nome Atualizado"}
        response = client.patch(f"/v1/athletes/{athlete.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Nome Atualizado"

    def test_update_athlete_not_found_returns_404(self, client):
        """Atualizar atleta inexistente retorna 404."""
        fake_id = uuid4()
        payload = {"full_name": "Teste"}
        response = client.patch(f"/v1/athletes/{fake_id}", json=payload)

        assert response.status_code == 404


class TestAthleteStatesRoutes:
    """Testes das rotas de estados (R13/R14)."""

    def test_list_states_returns_200(self, client, athlete):
        """Listar histórico de estados retorna 200."""
        response = client.get(f"/v1/athletes/{athlete.id}/states")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_change_state_returns_201(self, client, athlete):
        """Mudar estado retorna 201."""
        payload = {
            "state": "lesionada",
            "reason": "Lesão no tornozelo",
        }
        response = client.post(f"/v1/athletes/{athlete.id}/state", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["state"] == "lesionada"

    def test_change_state_invalid_returns_422(self, client, athlete):
        """Estado inválido retorna 422."""
        payload = {
            "state": "estado_invalido",
            "reason": "Teste",
        }
        response = client.post(f"/v1/athletes/{athlete.id}/state", json=payload)

        assert response.status_code == 422

    def test_change_state_athlete_not_found_returns_404(self, client):
        """Mudar estado de atleta inexistente retorna 404."""
        fake_id = uuid4()
        payload = {
            "state": "lesionada",
            "reason": "Teste",
        }
        response = client.post(f"/v1/athletes/{fake_id}/state", json=payload)

        assert response.status_code == 404
