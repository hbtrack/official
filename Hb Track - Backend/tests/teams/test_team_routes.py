"""Testes de integração das rotas de Team."""
import pytest


class TestListTeams:
    def test_list_teams_returns_200(self, client, team):
        response = client.get("/v1/teams")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestCreateTeam:
    def test_create_team_returns_201(self, client, season_ativa):
        payload = {
            "name": "Nova Equipe",
            "season_id": str(season_ativa.id),
        }
        response = client.post("/v1/teams", json=payload)
        assert response.status_code == 201


class TestGetTeam:
    def test_get_team_returns_200(self, client, team):
        response = client.get(f"/v1/teams/{team.id}")
        assert response.status_code == 200
