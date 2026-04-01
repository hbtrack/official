from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_source_graph import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "generated/source_graph/reports/reports.bundle.yaml",
    "generated/source_graph/reports/reports.schema_contract_view.yaml",
    "generated/source_graph/reports/reports.openapi_contract_view.yaml",
    "generated/source_graph/reports/impact_report.json",
}


def test_compile_expected_reports_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "reports")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    bundle = yaml.safe_load(next(item.content for item in expected if item.relpath.endswith(".bundle.yaml")))
    assert bundle["module"] == "reports"
    assert bundle["compiler"] == "hbtrack_source_graph_compiler"
    assert bundle["entities"]["ReportJob"]["schema_ref"].endswith("report_job.schema.json")

    impact = json.loads(next(item.content for item in expected if item.relpath.endswith("impact_report.json")))
    assert impact["module"] == "reports"
    assert impact["blocked_partial_update"] is True
    assert set(impact["outputs"]) == EXPECTED_OUTPUTS


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

    target = tmp_path / "generated" / "source_graph" / "reports" / "impact_report.json"
    target.write_text(target.read_text(encoding="utf-8").replace('"module": "reports"', '"module": "drifted"', 1), encoding="utf-8")

    drifts = check_expected(tmp_path, expected)
    assert any(item.relpath.endswith("impact_report.json") for item in drifts)


def test_compile_source_graph_cli_check_passes_against_repo():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_source_graph.py"),
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
    assert payload["module"] == "reports"


def test_hb_cli_compile_source_graph_check_passes_against_repo():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "hb"),
            "compile-source-graph",
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
