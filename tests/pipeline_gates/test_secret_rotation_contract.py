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


def test_rotate_keys_contract_script_reports_catalogued_runtime_secret_for_public_key():
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts" / "ops" / "rotate_keys.sh"),
            "--secret",
            "JWT_PUBLIC_KEY",
            "--environment",
            "production",
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
    assert payload["secret"] == "JWT_PUBLIC_KEY"
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


def test_pact_broker_token_is_catalogued_with_rotation_policy():
    """B8-002: PACT_BROKER_TOKEN deve estar no secrets_catalog com rotation_period_days definido."""
    import yaml as _yaml

    catalog_path = ROOT / "docs" / "_canon" / "graph" / "ops" / "secrets_catalog.yaml"
    catalog = _yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}

    runtime_secrets = catalog.get("runtime_secrets") or []
    pact_entry = next((s for s in runtime_secrets if isinstance(s, dict) and s.get("name") == "PACT_BROKER_TOKEN"), None)

    assert pact_entry is not None, "PACT_BROKER_TOKEN deve estar em runtime_secrets do secrets_catalog.yaml"
    assert isinstance(pact_entry.get("rotation_period_days"), int) and pact_entry["rotation_period_days"] > 0, (
        "PACT_BROKER_TOKEN deve ter rotation_period_days > 0"
    )
    assert pact_entry.get("rotation_command_ref") == "scripts/ops/rotate_keys.sh", (
        "rotation_command_ref de PACT_BROKER_TOKEN deve apontar para rotate_keys.sh"
    )
