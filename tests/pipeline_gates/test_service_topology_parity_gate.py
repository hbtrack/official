from __future__ import annotations

import copy
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def test_service_topology_parity_gate_passes_against_repo():
    result = gates._g2x_service_topology_parity(ROOT)

    assert result["status"] == "PASS", result


def test_service_topology_parity_gate_fails_for_runtime_topology_drift(monkeypatch):
    payload, checked, violations = gates._load_ops_operational_bundle(ROOT)
    assert not violations
    broken = copy.deepcopy(payload)
    broken["runtime_topology_json"]["services"].pop("frontend")

    monkeypatch.setattr(gates, "_load_ops_operational_bundle", lambda root: (broken, checked, []))

    result = gates._g2x_service_topology_parity(ROOT)

    assert result["status"] == "FAIL", result
    assert result["blocking_code"] == gates.BLOCKED_SERVICE_TOPOLOGY_PARITY
    assert any(
        violation["artifact"] == "compiled_ops/deploy/runtime_topology.json"
        for violation in result["violations"]
    )
