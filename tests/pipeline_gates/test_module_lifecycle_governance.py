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


def test_generate_frontend_stays_frozen_until_real_workspace_exists():
    catalog = yaml.safe_load((ROOT / ".contract_driven" / "TASK_CATALOG.yaml").read_text(encoding="utf-8"))
    entry = catalog["task_catalog"]["generate_frontend"]
    condition = entry["unblock_condition"]

    assert entry["status"] == "frozen"
    for expected in (
        "frontend/",
        "package.json",
        "FRONTEND_CONTRACT_GATE",
        "SKIP_NOT_APPLICABLE",
        "sign-off",
    ):
        assert expected in condition


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
