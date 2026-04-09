"""
Ciclo 6 — Notificações, Analytics e Relatórios: testes estruturais + live staging (opcional).
"""
from __future__ import annotations

import pytest
from replay import replay_notifications_analytics_reports as mod


class TestStructure:
    def test_cycle_id(self):
        assert mod.CYCLE_ID == "ciclo6_notificacao_analytics"

    def test_modules_declared(self):
        assert "notifications" in mod.CYCLE_MODULES
        assert "analytics" in mod.CYCLE_MODULES
        assert "reports" in mod.CYCLE_MODULES
        assert "ai_ingestion" in mod.CYCLE_MODULES

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

    def test_has_notifications_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "notifications_intents_create" in names

    def test_has_analytics_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "analytics_snapshots_create" in names

    def test_has_reports_endpoint(self):
        names = [ep["name"] for ep in mod.ENDPOINTS]
        assert "reports_jobs_create" in names


class TestLive:
    @pytest.fixture(autouse=True)
    def require_staging(self, live_staging):
        if not live_staging:
            pytest.skip("HB_STAGING_URL não definida — modo estrutural apenas")

    def test_ciclo6_notificacoes_analytics_relatorios(self, http_client, staging_url):
        r = http_client.post(
            f"{staging_url}/api/auth/token/",
            json={"email": "admin@hbtrack.test", "password": "hbtrack_test_2024!"},
        )
        assert r.status_code == 200
        token = r.json()["access"]
        auth = {"Authorization": f"Bearer {token}"}
        result = mod.run_live(http_client, staging_url, auth)
        assert result["status"] == "PASS"
