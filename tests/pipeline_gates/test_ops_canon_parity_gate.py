from __future__ import annotations

import copy
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def test_ops_canon_parity_gate_passes_against_repo():
    result = gates._g2t_ops_canon_parity(ROOT)

    assert result["status"] == "PASS", result


def test_ops_canon_parity_gate_fails_when_sync_manifest_loses_generated_consumer(monkeypatch):
    payload, checked, violations = gates._load_ops_operational_bundle(ROOT)
    assert not violations
    broken = copy.deepcopy(payload)
    ops_rule = next(
        rule
        for rule in broken["sync_manifest"]["rules"]
        if isinstance(rule, dict) and rule.get("rule_id") == "OPS_SOURCE_GRAPH_SYNC"
    )
    ops_rule["blocking_consumers"].remove("compiled_ops/deploy/secrets_catalog.json")

    monkeypatch.setattr(gates, "_load_ops_operational_bundle", lambda root: (broken, checked, []))

    result = gates._g2t_ops_canon_parity(ROOT)

    assert result["status"] == "FAIL", result
    assert result["blocking_code"] == gates.BLOCKED_OPS_CANON_PARITY
    assert any(
        "blocking_consumers" in violation["message"]
        for violation in result["violations"]
    )
