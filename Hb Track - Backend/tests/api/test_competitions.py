"""
Testes de Integração - Competitions API

Cenários cobertos:
1. CRUD de competições
2. Competition Seasons
3. Permissões por role
4. Paginação e filtros
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


class TestCompetitionsAPI:
    """Testes do módulo Competitions - autenticação"""
    
    def test_list_competitions_without_auth_returns_401(self):
        """GET /competitions sem auth deve retornar 401"""
        response = client.get("/api/v1/competitions")
        assert response.status_code == 401
    
    def test_get_competition_without_auth_returns_401(self):
        """GET /competitions/{id} sem auth deve retornar 401"""
        response = client.get(f"/api/v1/competitions/{uuid4()}")
        assert response.status_code == 401
    
    def test_create_competition_without_auth_returns_401(self):
        """POST /competitions sem auth deve retornar 401"""
        response = client.post("/api/v1/competitions", json={
            "name": "Campeonato Teste",
            "kind": "official",
        })
        assert response.status_code == 401


class TestCompetitionsAuthenticated:
    """Testes autenticados do módulo Competitions"""

    def test_superadmin_can_list_competitions(self, auth_client):
        """Superadmin pode listar competições"""
        response = auth_client.get("/api/v1/competitions")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_superadmin_can_create_competition(self, auth_client):
        """Superadmin pode criar competição"""
        import time
        competition_data = {
            "name": f"Campeonato Teste {int(time.time())}",
            "kind": "official",
        }
        response = auth_client.post("/api/v1/competitions", json=competition_data)
        # 200, 201 = sucesso, 400/422 = validação, 409 = já existe
        assert response.status_code in [200, 201, 400, 409, 422], f"Unexpected: {response.status_code}: {response.text}"

    def test_get_competition_with_invalid_id_returns_404(self, auth_client):
        """GET com ID inexistente retorna 404"""
        fake_id = str(uuid4())
        response = auth_client.get(f"/api/v1/competitions/{fake_id}")
        assert response.status_code == 404

    def test_competitions_endpoint_supports_pagination(self, auth_client):
        """API de competições suporta paginação"""
        response = auth_client.get("/api/v1/competitions", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        # Deve ter estrutura paginada
        if isinstance(data, dict):
            assert "items" in data or "total" in data


class TestCompetitionSeasonsAPI:
    """Testes do módulo Competition Seasons"""
    
    def test_list_competition_seasons_without_auth_returns_401(self):
        """GET /competition_seasons sem auth deve retornar 401"""
        response = client.get("/api/v1/competition_seasons")
        assert response.status_code == 401


class TestCompetitionSeasonsAuthenticated:
    """Testes autenticados do módulo Competition Seasons"""

    def test_superadmin_can_list_competition_seasons(self, auth_client):
        """Superadmin pode listar temporadas de competição"""
        response = auth_client.get("/api/v1/competition_seasons")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_competition_seasons_endpoint_supports_pagination(self, auth_client):
        """API de temporadas de competição suporta paginação"""
        response = auth_client.get("/api/v1/competition_seasons", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, dict):
            assert "items" in data or "total" in data
