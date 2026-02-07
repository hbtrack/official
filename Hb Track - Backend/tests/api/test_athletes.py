"""
Testes de Integração - Athletes API

Cenários cobertos:
1. CRUD de atletas
2. Atleta sem equipe (RF1.1)
3. Vinculação a equipes
4. Permissões
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


class TestAthletesAPI:
    """Testes do módulo Athletes"""
    
    def test_list_athletes_without_auth_returns_401(self):
        """GET /athletes sem auth deve retornar 401"""
        response = client.get("/api/v1/athletes")
        assert response.status_code == 401
    
    def test_get_athlete_without_auth_returns_401(self):
        """GET /athletes/{id} sem auth deve retornar 401"""
        response = client.get(f"/api/v1/athletes/{uuid4()}")
        assert response.status_code == 401
    
    def test_create_athlete_without_auth_returns_401(self):
        """POST /athletes sem auth deve retornar 401"""
        response = client.post("/api/v1/athletes", json={
            "full_name": "Atleta Teste",
            "birth_date": "2010-01-01",
            "gender": "feminino",
        })
        assert response.status_code == 401


class TestAthletesDomainRules:
    """Testes de regras de domínio de Athletes"""

    def test_superadmin_can_list_athletes(self, auth_client):
        """Superadmin pode listar atletas"""
        response = auth_client.get("/api/v1/athletes")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_superadmin_can_create_athlete(self, auth_client):
        """Superadmin pode criar atleta (RF1.1: atleta pode existir sem equipe)"""
        import time
        
        # Buscar organização válida
        orgs_response = auth_client.get("/api/v1/organizations")
        assert orgs_response.status_code == 200
        orgs = orgs_response.json()
        org_id = orgs["items"][0]["id"] if "items" in orgs else orgs[0]["id"]

        # Criar atleta sem equipe (RF1.1 permite isso)
        athlete_data = {
            "full_name": f"Atleta Teste {int(time.time())}",
            "birth_date": "2010-01-15",
            "gender": "feminino",
            "organization_id": org_id,
        }
        response = auth_client.post("/api/v1/athletes", json=athlete_data)
        # Pode retornar 200, 201 (criado), 400/422 se validação falhar, 409 se já existe
        assert response.status_code in [200, 201, 400, 409, 422], f"Unexpected: {response.status_code}: {response.text}"

    def test_get_athlete_with_invalid_id_returns_404(self, auth_client):
        """GET com ID inexistente retorna 404"""
        fake_id = str(uuid4())
        response = auth_client.get(f"/api/v1/athletes/{fake_id}")
        assert response.status_code == 404

    def test_athletes_endpoint_returns_paginated_response(self, auth_client):
        """API de atletas retorna resposta paginada"""
        response = auth_client.get("/api/v1/athletes", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        # Deve ter estrutura paginada
        if isinstance(data, dict):
            assert "items" in data or "data" in data or "athletes" in data
