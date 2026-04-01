from __future__ import annotations

import copy
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def test_secrets_catalog_gate_passes_against_repo():
    result = gates._g2w_secrets_catalog(ROOT)

    assert result["status"] == "PASS", result


def test_secrets_catalog_gate_fails_for_missing_rotation_ref(monkeypatch):
    payload, checked, violations = gates._load_ops_operational_bundle(ROOT)
    assert not violations
    broken = copy.deepcopy(payload)
    broken["secrets_catalog"]["runtime_secrets"][0]["rotation_ref"] = "docs/_canon/decisions/MISSING.md"

    monkeypatch.setattr(gates, "_load_ops_operational_bundle", lambda root: (broken, checked, []))

    result = gates._g2w_secrets_catalog(ROOT)

    assert result["status"] == "FAIL", result
    assert result["blocking_code"] == gates.BLOCKED_SECRETS_CATALOG_INVALID
    assert any(
        "rotation_ref inexistente" in violation["message"]
        for violation in result["violations"]
    )
