"""
Testes de integração das rotas de Season.

Usa fixture `client` do conftest.py global que faz override
de get_db para compartilhar a sessão de teste com isolamento
transacional.
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4


class TestListSeasons:
    """Testes GET /v1/seasons."""
    
    def test_list_seasons_returns_200(self, client, season_planejada):
        """Lista temporadas com sucesso."""
        response = client.get("/v1/seasons")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert data["total"] >= 1  # Pelo menos a season_planejada


class TestCreateSeason:
    """Testes POST /v1/seasons."""
    
    def test_create_season_returns_201(self, client, organization_id, membership_id):
        """Criar temporada retorna 201."""
        payload = {
            "year": 2030,
            "name": "Nova Temporada",
            "start_date": str(date.today() + timedelta(days=30)),
            "end_date": str(date.today() + timedelta(days=365)),
        }
        
        response = client.post("/v1/seasons", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Nova Temporada"
        assert data["year"] == 2030
        assert "id" in data


class TestGetSeason:
    """Testes GET /v1/seasons/{id}."""
    
    def test_get_season_returns_200(self, client, season_planejada):
        """Buscar temporada existente."""
        response = client.get(f"/v1/seasons/{season_planejada.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(season_planejada.id)
        assert data["name"] == season_planejada.name
    
    def test_get_season_not_found_returns_404(self, client):
        """Buscar temporada inexistente."""
        fake_id = uuid4()
        response = client.get(f"/v1/seasons/{fake_id}")
        
        assert response.status_code == 404


class TestUpdateSeason:
    """Testes PATCH /v1/seasons/{id}."""
    
    def test_update_season_returns_200(self, client, season_planejada):
        """Atualizar temporada com sucesso."""
        payload = {"name": "Nome Atualizado"}
        
        response = client.patch(
            f"/v1/seasons/{season_planejada.id}", 
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nome Atualizado"


class TestInterruptSeason:
    """Testes POST /v1/seasons/{id}/interrupt."""
    
    def test_interrupt_season_returns_200(self, client, season_ativa):
        """Interromper temporada ativa."""
        payload = {"reason": "Força maior"}
        
        response = client.post(
            f"/v1/seasons/{season_ativa.id}/interrupt",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "interrompida"
