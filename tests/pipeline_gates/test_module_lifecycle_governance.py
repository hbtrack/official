from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_module_registry_schema_supports_post_implementation_statuses():
    schema = json.loads(
        (ROOT / "contracts" / "schemas" / "shared" / "module_registry.schema.json").read_text(encoding="utf-8")
    )
    enum_values = set(schema["$defs"]["moduleEntry"]["properties"]["status"]["enum"])

    assert {
        "scaffold",
        "draft_contract",
        "validated_contract",
        "implementation_ready",
        "implemented",
        "staging_validated",
        "released",
    } == enum_values


def test_module_registry_policy_declares_full_lifecycle_order():
    registry = yaml.safe_load((ROOT / "docs" / "_canon" / "MODULE_REGISTRY.yaml").read_text(encoding="utf-8"))
    policy = registry["policy"]

    assert policy["status_order"] == [
        "scaffold",
        "draft_contract",
        "validated_contract",
        "implementation_ready",
        "implemented",
        "staging_validated",
        "released",
    ]

    for status in ("implemented", "staging_validated", "released"):
        assert status in policy["status_semantics"]
        assert policy["status_semantics"][status]


def test_generate_frontend_stays_frozen_until_contract_gate_passes():
    catalog = yaml.safe_load((ROOT / ".contract_driven" / "TASK_CATALOG.yaml").read_text(encoding="utf-8"))
    entry = catalog["task_catalog"]["generate_frontend"]
    condition = entry["unblock_condition"]

    assert entry["status"] == "frozen"
    for expected in (
        "FRONTEND_CONTRACT_GATE",
        "passar",
        "sign-off",
    ):
        assert expected in condition


def test_frontend_contract_gate_is_active_and_registered():
    registry = yaml.safe_load((ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml").read_text(encoding="utf-8"))
    gate = next(item for item in registry["gates"] if item["gate_id"] == "FRONTEND_CONTRACT_GATE")
    validator = (ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py").read_text(encoding="utf-8")

    assert gate["status"] == "active"
    assert gate["blocking"] is True
    assert "BLOCKED_FRONTEND_CONTRACT_NONCOMPLIANCE" in gate["blocking_codes"]
    assert "(\"FRONTEND_CONTRACT_GATE\", lambda: _g_frontend_contract(root))" in validator
    assert "\"FRONTEND_CONTRACT_GATE\"," in validator
    for expected in ("command palette", "Conta e Acesso", "Resend", "Cloudinary"):
        assert expected in gate["description"] or expected in validator


def test_active_taxonomy_docs_use_17_modules():
    expected_files = [
        "docs/_canon/README.md",
        "docs/_canon/SYSTEM_SCOPE.md",
        "docs/_canon/CI_CONTRACT_GATES.md",
        "docs/_canon/SCOPE_BOUNDARY_POLICY.md",
        "docs/_canon/HANDBALL_RULES_DOMAIN.md",
        "docs/_canon/gates/README.md",
        "docs/_canon/gates/GATES_REGISTRY.yaml",
        ".contract_driven/CONTRACT_SYSTEM_LAYOUT.md",
        ".contract_driven/CONTRACT_SYSTEM_RULES.md",
        ".contract_driven/CONTRACT_FILESYSTEM_REFERENCE.md",
    ]

    for rel in expected_files:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "16 módulos" not in text, rel


def test_deploy_pipeline_marks_automation_as_partial_until_assets_exist():
    text = (ROOT / "docs" / "_canon" / "DEPLOY_PIPELINE.md").read_text(encoding="utf-8")

    for expected in (
        "Dockerfile",
        "infra/docker-compose.prod.yml",
        "infra/nginx/nginx.conf",
        "staging_validated",
        "released",
        "target-state",
    ):
        assert expected in text
