"""
Ciclo 3 — Partida e Competição: testes estruturais + live staging (opcional).
"""
from __future__ import annotations

import pytest
from replay import replay_match_competition as mod


class TestStructure:
    def test_cycle_id(self):
        assert mod.CYCLE_ID == "ciclo3_partida_competicao"

    def test_modules_declared(self):
        assert "matches" in mod.CYCLE_MODULES
        assert "competitions" in mod.CYCLE_MODULES

    def test_endpoints_have_required_fields(self):
        for ep in mod.ENDPOINTS:
            assert "method" in ep, f"Endpoint sem 'method': {ep}"
            assert "path" in ep, f"Endpoint sem 'path': {ep}"
            assert "name" in ep, f"Endpoint sem 'name': {ep}"

    def test_endpoints_not_empty(self):
        assert len(mod.ENDPOINTS) >= 3

    def test_describe_returns_dict(self):
        info = mod.describe()
        assert info["cycle_id"] == mod.CYCLE_ID
        assert info["modules"] == mod.CYCLE_MODULES
        assert info["endpoints"] == mod.ENDPOINTS

    def test_run_live_callable(self):
        assert callable(mod.run_live)

    def test_has_match_create_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "matches_create" in names

    def test_has_competition_create_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "competitions_create" in names

    def test_has_patch_method(self):
        methods = [ep["method"] for ep in mod.ENDPOINTS]
        assert "PATCH" in methods


class TestLive:
    @pytest.fixture(autouse=True)
    def require_staging(self, live_staging):
        if not live_staging:
            pytest.skip("HB_STAGING_URL não definida — modo estrutural apenas")

    def test_ciclo3_partida_competicao(self, http_client, staging_url):
        r = http_client.post(
            f"{staging_url}/api/auth/token/",
            json={"email": "admin@hbtrack.test", "password": "hbtrack_test_2024!"},
        )
        assert r.status_code == 200
        token = r.json()["access"]
        auth = {"Authorization": f"Bearer {token}"}
        # criar equipe para usar como referência
        r2 = http_client.post(f"{staging_url}/api/teams/", json={"name": "T3", "gender": "M"}, headers=auth)
        team_id = r2.json().get("id")
        result = mod.run_live(http_client, staging_url, auth, team_id=team_id)
        assert result["status"] == "PASS"
