from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/analytics/FT-038.json",
}


def test_compile_expected_analytics_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "analytics")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    payload = json.loads(expected[0].content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "analytics"
    assert payload["feature"]["id"] == "FT-038"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/analytics.yaml"]
    assert payload["feature"]["endpoints"] == [
        "GET /analytics/snapshots",
        "POST /analytics/snapshots",
        "GET /analytics/dashboards",
    ]
    assert [item["operation_id"] for item in payload["source_graph"]["operations"]] == [
        "listAnalyticsSnapshots",
        "createAnalyticsSnapshot",
        "listAnalyticsDashboards",
    ]
    assert "queryAnalyticsData" not in {
        item["operation_id"] for item in payload["source_graph"]["operations"]
    }
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "compiled_context/analytics/FT-038.json" in payload["implementation_targets"]["derived_context"]
    assert "src/analytics/api.py" in payload["implementation_targets"]["canonical_runtime"]
    assert "python3 scripts/compile/compile_context_bundle.py --module analytics --check --format json" in payload["validation"]["required_commands"]


def test_compile_expected_analytics_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "analytics")
    second = compile_expected(REPO_ROOT, "analytics")
    assert first == second


def test_write_and_check_expected_analytics_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "analytics")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_analytics_and_all():
    analytics_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "analytics",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert analytics_result.returncode == 0, analytics_result.stdout + analytics_result.stderr
    analytics_payload = json.loads(analytics_result.stdout)
    assert analytics_payload["status"] == "PASS"
    assert analytics_payload["features"] == ["FT-038"]

    batch_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--all",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert batch_result.returncode == 0, batch_result.stdout + batch_result.stderr
    batch_payload = json.loads(batch_result.stdout)
    assert batch_payload["status"] == "PASS"
    assert {"reports", "analytics"} <= set(batch_payload["modules"])


def test_hb_cli_compile_context_bundle_check_passes_for_all_modules():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "hb"),
            "compile-context-bundle",
            "--all",
            "--check",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_analytics_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "ANALYTICS_SOURCE_GRAPH_SYNC")

    assert "compiled_context/analytics/FT-038.json" in rule["required_consumers"]
    assert "compiled_context/analytics/FT-038.json" in rule["blocking_consumers"]
    assert "python3 scripts/compile/compile_context_bundle.py --module analytics --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_analytics_source_graph_integrity.py tests/pipeline_gates/test_source_graph_compiler_analytics.py tests/pipeline_gates/test_context_bundle_analytics.py -q" in rule["validation_commands"]
