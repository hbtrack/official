from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from scripts.contracts.validate import validate_contracts as gates


ROOT = Path(__file__).resolve().parents[2]


def test_secret_rotation_contract_passes_against_repo():
    result = gates._g2w_secrets_catalog(ROOT)

    assert result["status"] == "PASS", result


def test_rotate_keys_contract_script_reports_catalogued_runtime_secret():
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts" / "ops" / "rotate_keys.sh"),
            "--secret",
            "JWT_PRIVATE_KEY",
            "--environment",
            "staging",
            "--format",
            "json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["secret"] == "JWT_PRIVATE_KEY"
    assert payload["rotation_command_ref"] == "scripts/ops/rotate_keys.sh"


def test_secret_rotation_contract_fails_when_runtime_secret_lacks_rotation_command(monkeypatch):
    payload, checked, violations = gates._load_ops_operational_bundle(ROOT)
    assert not violations
    broken = copy.deepcopy(payload)
    broken["secrets_catalog"]["runtime_secrets"][0].pop("rotation_command_ref", None)

    monkeypatch.setattr(gates, "_load_ops_operational_bundle", lambda root: (broken, checked, []))

    result = gates._g2w_secrets_catalog(ROOT)

    assert result["status"] == "FAIL", result
    assert any("rotation_command_ref" in item["message"] for item in result["violations"])


def test_secret_rotation_contract_fails_when_adr_inventory_has_prose_only_secret(monkeypatch):
    payload, checked, violations = gates._load_ops_operational_bundle(ROOT)
    assert not violations
    broken = copy.deepcopy(payload)
    broken["adr_012"] = broken["adr_012"].replace(
        "<!-- OPS_RUNTIME_SECRETS_END -->",
        "- `PROSE_ONLY_SECRET`\n<!-- OPS_RUNTIME_SECRETS_END -->",
        1,
    )

    monkeypatch.setattr(gates, "_load_ops_operational_bundle", lambda root: (broken, checked, []))

    result = gates._g2w_secrets_catalog(ROOT)

    assert result["status"] == "FAIL", result
    assert any("Inventário runtime em ADR-012 diverge" in item["message"] for item in result["violations"])


def test_deploy_workflow_gate_fails_for_hardcoded_runtime_secret(monkeypatch):
    payload, checked, violations = gates._load_ops_operational_bundle(ROOT)
    assert not violations
    broken = copy.deepcopy(payload)
    workflow_doc = copy.deepcopy(broken["workflow"])
    workflow_doc["jobs"]["deploy-staging"]["steps"][2]["env"]["HB_ENV_SECRET_KEY"] = "hardcoded-secret"
    broken["workflow"] = workflow_doc

    monkeypatch.setattr(gates, "_load_ops_operational_bundle", lambda root: (broken, checked, []))

    result = gates._g2v_deploy_workflow_env_parity(ROOT)

    assert result["status"] == "FAIL", result
    assert any("HB_ENV_SECRET_KEY" in item["message"] for item in result["violations"])
