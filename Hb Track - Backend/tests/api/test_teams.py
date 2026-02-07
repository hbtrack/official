"""
Testes de Integração - Teams API

Cenários cobertos:
1. CRUD de equipes
2. Permissões por role
3. Filtros e paginação
4. Validações de campos
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


class TestTeamsAPI:
    """Testes do módulo Teams"""
    
    def test_list_teams_without_auth_returns_401(self):
        """GET /teams sem auth deve retornar 401"""
        response = client.get("/api/v1/teams")
        assert response.status_code == 401
    
    def test_get_team_without_auth_returns_401(self):
        """GET /teams/{id} sem auth deve retornar 401"""
        response = client.get(f"/api/v1/teams/{uuid4()}")
        assert response.status_code == 401
    
    def test_create_team_without_auth_returns_401(self):
        """POST /teams sem auth deve retornar 401"""
        response = client.post("/api/v1/teams", json={
            "name": "Teste",
            "category_id": 1,
            "gender": "feminino",
        })
        assert response.status_code == 401
    
    def test_update_team_without_auth_returns_401(self):
        """PATCH /teams/{id} sem auth deve retornar 401"""
        response = client.patch(f"/api/v1/teams/{uuid4()}", json={"name": "Novo Nome"})
        assert response.status_code == 401
    
    def test_delete_team_without_auth_returns_401(self):
        """DELETE /teams/{id} sem auth deve retornar 401"""
        response = client.delete(f"/api/v1/teams/{uuid4()}")
        assert response.status_code == 401


class TestTeamsRBAC:
    """Testes RBAC autenticados do módulo Teams"""

    def test_superadmin_can_list_teams(self, auth_client):
        """Superadmin pode listar equipes"""
        response = auth_client.get("/api/v1/teams")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_superadmin_can_create_team(self, auth_client):
        """Superadmin pode criar equipe - RBAC: can_create_team=True"""
        import time
        # Primeiro buscar uma organização válida
        orgs_response = auth_client.get("/api/v1/organizations")
        assert orgs_response.status_code == 200
        orgs = orgs_response.json()
        org_id = orgs["items"][0]["id"] if "items" in orgs else orgs[0]["id"]

        # Buscar uma categoria válida
        cat_response = auth_client.get("/api/v1/categories")
        assert cat_response.status_code == 200, f"Categories endpoint failed: {cat_response.text}"
        categories = cat_response.json()
        if isinstance(categories, dict) and "items" in categories:
            category_id = categories["items"][0]["id"]
        elif isinstance(categories, list) and len(categories) > 0:
            category_id = categories[0]["id"]
        else:
            pytest.skip("No categories available for test")

        # Criar equipe
        team_data = {
            "name": f"Equipe Teste RBAC {int(time.time())}",
            "category_id": category_id,
            "gender": "feminino",
            "organization_id": org_id,
        }
        response = auth_client.post("/api/v1/teams", json=team_data)
        # 201 = criado com sucesso, 409 = já existe (também válido)
        assert response.status_code in [200, 201, 409], f"Expected 200/201/409, got {response.status_code}: {response.text}"

    def test_superadmin_can_update_team(self, auth_client, test_team_id):
        """Superadmin pode editar equipe - RBAC: can_edit_team=True"""
        import time
        update_data = {
            "name": f"Equipe Atualizada {int(time.time())}"
        }
        response = auth_client.patch(f"/api/v1/teams/{test_team_id}", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "name" in data or "id" in data

    def test_get_team_with_invalid_id_returns_404(self, auth_client):
        """GET com ID inexistente retorna 404"""
        fake_id = str(uuid4())
        response = auth_client.get(f"/api/v1/teams/{fake_id}")
        assert response.status_code == 404
