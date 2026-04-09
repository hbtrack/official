"""
Ciclo 5 — Treino e Wellness: testes estruturais + live staging (opcional).
"""
from __future__ import annotations

import pytest
from replay import replay_training_wellness as mod


class TestStructure:
    def test_cycle_id(self):
        assert mod.CYCLE_ID == "ciclo5_treino_wellness"

    def test_modules_declared(self):
        assert "training" in mod.CYCLE_MODULES
        assert "wellness" in mod.CYCLE_MODULES

    def test_endpoints_have_required_fields(self):
        for ep in mod.ENDPOINTS:
            assert "method" in ep, f"Endpoint sem 'method': {ep}"
            assert "path" in ep, f"Endpoint sem 'path': {ep}"
            assert "name" in ep, f"Endpoint sem 'name': {ep}"

    def test_endpoints_not_empty(self):
        assert len(mod.ENDPOINTS) >= 2

    def test_describe_returns_dict(self):
        info = mod.describe()
        assert info["cycle_id"] == mod.CYCLE_ID
        assert info["modules"] == mod.CYCLE_MODULES
        assert info["endpoints"] == mod.ENDPOINTS

    def test_run_live_callable(self):
        assert callable(mod.run_live)

    def test_has_training_sessions_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "training_sessions_create" in names

    def test_has_wellness_entries_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "wellness_entries_create" in names

    def test_covers_extra_modules(self):
        assert "medical" in mod.CYCLE_MODULES
        assert "exercises" in mod.CYCLE_MODULES


class TestLive:
    @pytest.fixture(autouse=True)
    def require_staging(self, live_staging):
        if not live_staging:
            pytest.skip("HB_STAGING_URL não definida — modo estrutural apenas")

    def test_ciclo5_treino_wellness(self, http_client, staging_url):
        r = http_client.post(
            f"{staging_url}/api/auth/token/",
            json={"email": "admin@hbtrack.test", "password": "hbtrack_test_2024!"},
        )
        assert r.status_code == 200
        token = r.json()["access"]
        auth = {"Authorization": f"Bearer {token}"}
        r2 = http_client.get(f"{staging_url}/api/teams/", headers=auth)
        teams = r2.json().get("results", r2.json() if isinstance(r2.json(), list) else [])
        team_id = teams[0]["id"] if teams else "00000000-0000-0000-0000-000000000001"
        result = mod.run_live(http_client, staging_url, auth, team_id=team_id)
        assert result["status"] == "PASS"
