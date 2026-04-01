from __future__ import annotations

import copy
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def test_deploy_workflow_env_parity_gate_passes_against_repo():
    result = gates._g2v_deploy_workflow_env_parity(ROOT)

    assert result["status"] == "PASS", result


def test_deploy_workflow_env_parity_gate_fails_for_health_check_drift(monkeypatch):
    payload, checked, violations = gates._load_ops_operational_bundle(ROOT)
    assert not violations
    broken = copy.deepcopy(payload)
    broken["deploy_contract"]["health_checks"]["staging"]["url"] = "https://invalid.example/health"

    monkeypatch.setattr(gates, "_load_ops_operational_bundle", lambda root: (broken, checked, []))

    result = gates._g2v_deploy_workflow_env_parity(ROOT)

    assert result["status"] == "FAIL", result
    assert result["blocking_code"] == gates.BLOCKED_DEPLOY_WORKFLOW_ENV_PARITY
    assert any(
        "health_checks.staging.url" in violation["message"]
        for violation in result["violations"]
    )
