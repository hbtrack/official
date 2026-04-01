from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_ops_contracts import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "infra/env/.env.staging.template",
    "infra/env/.env.production.template",
    "compiled_ops/deploy/staging.env.fragment",
    "compiled_ops/deploy/production.env.fragment",
    "compiled_ops/deploy/secrets_catalog.json",
    "compiled_ops/deploy/runtime_topology.json",
    "compiled_ops/deploy/impact_report.json",
}


def test_compile_expected_ops_emits_required_outputs():
    expected = compile_expected(REPO_ROOT)
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    impact = json.loads(next(item.content for item in expected if item.relpath.endswith("impact_report.json")))
    assert impact["scope"] == "operations"
    assert impact["blocked_partial_update"] is True
    assert set(impact["outputs"]) == EXPECTED_OUTPUTS
    assert "python3 scripts/compile/compile_ops_contracts.py --check" in impact["required_tests"]
    assert impact["template_parity_hints"]

    topology = json.loads(next(item.content for item in expected if item.relpath.endswith("runtime_topology.json")))
    assert topology["artifact_id"] == "HBTRACK_OPS_RUNTIME_TOPOLOGY"
    assert {"staging", "production"} <= set(topology["deploy_contract"]["health_checks"].keys())


def test_compile_expected_ops_is_deterministic():
    first = compile_expected(REPO_ROOT)
    second = compile_expected(REPO_ROOT)
    assert first == second


def test_write_and_check_expected_ops_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT)
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_check_expected_ops_detects_drift(tmp_path: Path):
    expected = compile_expected(REPO_ROOT)
    write_expected(tmp_path, expected)

    target = tmp_path / "compiled_ops" / "deploy" / "impact_report.json"
    target.write_text(target.read_text(encoding="utf-8").replace('"scope": "operations"', '"scope": "drifted"', 1), encoding="utf-8")

    drifts = check_expected(tmp_path, expected)
    assert any(item.relpath.endswith("impact_report.json") for item in drifts)


def test_ops_compiler_cli_check_passes_against_repo():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_ops_contracts.py"),
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["scope"] == "operations"


def test_hb_cli_compile_ops_contracts_check_passes_against_repo():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "hb"),
            "compile-ops-contracts",
            "--check",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_ops_compiler_outputs_are_registered_in_authority_and_sync_manifests():
    source_graph = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SOURCE_AUTHORITY_GRAPH.yaml").read_text(encoding="utf-8"))
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))

    ops_concept = source_graph["concepts"]["operational_runtime_contracts"]
    for relpath in (
        "infra/env/.env.staging.template",
        "infra/env/.env.production.template",
        "compiled_ops/deploy/staging.env.fragment",
        "compiled_ops/deploy/production.env.fragment",
        "compiled_ops/deploy/secrets_catalog.json",
        "compiled_ops/deploy/runtime_topology.json",
        "compiled_ops/deploy/impact_report.json",
        "tests/pipeline_gates/test_ops_contract_compiler.py",
    ):
        assert relpath in ops_concept["consumers"]

    ops_sync = next(rule for rule in sync_manifest["rules"] if rule["rule_id"] == "OPS_SOURCE_GRAPH_SYNC")
    for relpath in (
        "infra/env/.env.staging.template",
        "infra/env/.env.production.template",
        "compiled_ops/deploy/staging.env.fragment",
        "compiled_ops/deploy/production.env.fragment",
        "compiled_ops/deploy/secrets_catalog.json",
        "compiled_ops/deploy/runtime_topology.json",
        "compiled_ops/deploy/impact_report.json",
    ):
        assert relpath in ops_sync["blocking_consumers"]
