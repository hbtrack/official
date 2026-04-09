"""
Ciclo 4 — Scout e Vídeo: testes estruturais + live staging (opcional).
"""
from __future__ import annotations

import pytest
from replay import replay_scout_video as mod


class TestStructure:
    def test_cycle_id(self):
        assert mod.CYCLE_ID == "ciclo4_scout_video"

    def test_modules_declared(self):
        assert "scout" in mod.CYCLE_MODULES
        assert "video" in mod.CYCLE_MODULES

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

    def test_has_video_session_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "video_sessions_create" in names

    def test_has_scout_events_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "scout_events_create" in names

    def test_has_scout_complete_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "scout_sessions_complete" in names


class TestLive:
    @pytest.fixture(autouse=True)
    def require_staging(self, live_staging):
        if not live_staging:
            pytest.skip("HB_STAGING_URL não definida — modo estrutural apenas")

    def test_ciclo4_scout_video(self, http_client, staging_url):
        r = http_client.post(
            f"{staging_url}/api/auth/token/",
            json={"email": "admin@hbtrack.test", "password": "hbtrack_test_2024!"},
        )
        assert r.status_code == 200
        token = r.json()["access"]
        auth = {"Authorization": f"Bearer {token}"}
        # precisamos de um match_id para scout/video
        r2 = http_client.get(f"{staging_url}/api/matches/", headers=auth)
        matches = r2.json().get("results", r2.json() if isinstance(r2.json(), list) else [])
        match_id = matches[0]["id"] if matches else "00000000-0000-0000-0000-000000000001"
        result = mod.run_live(http_client, staging_url, auth, match_id=match_id)
        assert result["status"] == "PASS"
