from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/reports/FT-039.json",
}


def test_compile_expected_reports_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "reports")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    payload = json.loads(expected[0].content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "reports"
    assert payload["feature"]["id"] == "FT-039"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/reports.yaml"]
    assert payload["feature"]["endpoints"] == [
        "GET /reports/jobs",
        "POST /reports/jobs",
        "GET /reports/jobs/{jobId}",
        "GET /reports/jobs/{jobId}/download",
    ]
    assert [item["operation_id"] for item in payload["source_graph"]["operations"]] == [
        "listReportJobs",
        "createReportJob",
        "getReportJob",
        "downloadReportArtifact",
    ]
    assert "updateReportJob" not in {
        item["operation_id"] for item in payload["source_graph"]["operations"]
    }
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert payload["module_state"]["expected_surfaces"] == [
        "module_docs_minimum",
        "openapi_sync",
        "json_schema",
        "test_matrix",
    ]
    assert "compiled_context/reports/FT-039.json" in payload["implementation_targets"]["derived_context"]
    assert "src/reports/generated/api.py" in payload["implementation_targets"]["generated_runtime"]
    assert "src/reports/api.py" in payload["implementation_targets"]["canonical_runtime"]
    assert "python3 scripts/compile/compile_context_bundle.py --module reports --check --format json" in payload["validation"]["required_commands"]


def test_compile_expected_reports_is_deterministic():
    first = compile_expected(REPO_ROOT, "reports")
    second = compile_expected(REPO_ROOT, "reports")
    assert first == second


def test_write_and_check_expected_reports_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "reports")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_check_expected_reports_detects_drift(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "reports")
    write_expected(tmp_path, expected)

    target = tmp_path / "compiled_context" / "reports" / "FT-039.json"
    target.write_text(
        target.read_text(encoding="utf-8").replace('"module": "reports"', '"module": "drifted"', 1),
        encoding="utf-8",
    )

    drifts = check_expected(tmp_path, expected)
    assert any(item.relpath == "compiled_context/reports/FT-039.json" for item in drifts)


def test_context_bundle_cli_check_passes_against_repo():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "reports",
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
    assert payload["features"] == ["FT-039"]


def test_hb_cli_compile_context_bundle_check_passes_against_repo():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "hb"),
            "compile-context-bundle",
            "--module",
            "reports",
            "--check",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_reports_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "REPORTS_SOURCE_GRAPH_SYNC")

    assert "compiled_context/reports/FT-039.json" in rule["required_consumers"]
    assert "compiled_context/reports/FT-039.json" in rule["blocking_consumers"]
    assert "python3 scripts/compile/compile_context_bundle.py --module reports --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_context_bundle_reports.py -q" in rule["validation_commands"]


def test_contract_gates_workflow_checks_context_bundle():
    workflow = (REPO_ROOT / ".github" / "workflows" / "contract-gates.yml").read_text(encoding="utf-8")
    assert "compile_context_bundle.py --module reports --check" in workflow
