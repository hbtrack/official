"""
Ciclo 1 — Identidade e Acesso: testes estruturais + live staging (opcional).
"""
from __future__ import annotations

import pytest
from replay import replay_identity_access as mod


class TestStructure:
    def test_cycle_id(self):
        assert mod.CYCLE_ID == "ciclo1_identidade_acesso"

    def test_modules_declared(self):
        assert "identity_access" in mod.CYCLE_MODULES
        assert "users" in mod.CYCLE_MODULES
        assert "audit" in mod.CYCLE_MODULES

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


class TestLive:
    @pytest.fixture(autouse=True)
    def require_staging(self, live_staging):
        if not live_staging:
            pytest.skip("HB_STAGING_URL não definida — modo estrutural apenas")

    def test_ciclo1_autenticacao_e_perfil(self, http_client, staging_url):
        from scripts.replay.common import SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD
        result = mod.run_live(
            http_client,
            staging_url,
            {"email": SEED_ADMIN_EMAIL, "password": SEED_ADMIN_PASSWORD},
        )
        assert result["status"] == "PASS"
        assert len(result["steps"]) >= 2
