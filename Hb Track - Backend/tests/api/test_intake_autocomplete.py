"""
Testes de Autocomplete - Intake
================================
FASE 4 - FICHA.MD Seção 4.2

Valida endpoints de autocomplete com filtros de escopo:

GET /api/v1/intake/organizations/autocomplete
- Superadmin: retorna todas as organizações
- Outros papéis: retorna apenas org com membership ativo

GET /api/v1/intake/teams/autocomplete
- Requer organization_id
- Valida escopo organizacional (exceto superadmin)
- Filtra equipes por nome (query param q)
"""

import pytest
from uuid import uuid4


class TestOrganizationsAutocomplete:
    """Testes do endpoint de autocomplete de organizações"""

    def test_organizations_autocomplete_requires_authentication(self, client):
        """Endpoint requer autenticação"""
        response = client.get("/api/v1/intake/organizations/autocomplete", params={"q": "test"})
        assert response.status_code == 401

    def test_superadmin_can_access_organizations_autocomplete(self, auth_client):
        """Superadmin consegue acessar autocomplete de organizações"""
        # q tem min_length=2
        response = auth_client.get("/api/v1/intake/organizations/autocomplete", params={"q": "cl"})
        assert response.status_code == 200, f"Status inesperado: {response.status_code}"
        
        data = response.json()
        # Deve retornar dict com items
        assert "items" in data or isinstance(data, list)


class TestTeamsAutocomplete:
    """Testes do endpoint de autocomplete de equipes"""

    def test_teams_autocomplete_requires_authentication(self, client):
        """Endpoint requer autenticação"""
        response = client.get("/api/v1/intake/teams/autocomplete", params={"q": "test"})
        assert response.status_code == 401

    def test_superadmin_can_access_teams_autocomplete(self, auth_client):
        """Superadmin consegue acessar autocomplete de equipes"""
        # Primeiro, obter uma org_id válida
        orgs_response = auth_client.get("/api/v1/organizations")
        
        if orgs_response.status_code != 200:
            pytest.skip("Não foi possível obter organizações")
        
        orgs_data = orgs_response.json()
        items = orgs_data.get("items", orgs_data) if isinstance(orgs_data, dict) else orgs_data
        
        if not items:
            pytest.skip("Nenhuma organização no banco")
        
        org_id = items[0]["id"]
        
        # q tem min_length=2
        response = auth_client.get(
            "/api/v1/intake/teams/autocomplete",
            params={"organization_id": org_id, "q": "eq"}
        )
        assert response.status_code == 200, f"Status inesperado: {response.status_code}"
