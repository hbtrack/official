from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/scout/FT-036.json",
}


def test_compile_expected_scout_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "scout")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    ft036_content = next(item.content for item in expected if item.relpath.endswith("FT-036.json"))
    payload = json.loads(ft036_content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "scout"
    assert payload["feature"]["id"] == "FT-036"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/scout.yaml"]
    assert "GET /scout/events" in payload["feature"]["endpoints"]
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "src/scout/api.py" in payload["implementation_targets"]["canonical_runtime"]

    for ft_item in expected:
        ft_payload = json.loads(ft_item.content)
        assert ft_payload["module"] == "scout"
        assert ft_payload["compiler"] == "hbtrack_context_bundle_compiler"


def test_compile_expected_scout_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "scout")
    second = compile_expected(REPO_ROOT, "scout")
    assert first == second


def test_write_and_check_expected_scout_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "scout")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_scout_and_all():
    scout_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "scout",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert scout_result.returncode == 0, scout_result.stdout + scout_result.stderr
    scout_payload = json.loads(scout_result.stdout)
    assert scout_payload["status"] == "PASS"
    assert sorted(scout_payload["features"]) == ["FT-036"]

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
    assert "scout" in {batch_payload.get("module")} | set(batch_payload.get("modules", []))


def test_scout_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "SCOUT_SOURCE_GRAPH_SYNC")

    assert "compiled_context/scout/FT-036.json" in rule["required_consumers"]

    assert "python3 scripts/compile/compile_context_bundle.py --module scout --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_scout_source_graph_integrity.py tests/pipeline_gates/test_source_graph_compiler_scout.py tests/pipeline_gates/test_context_bundle_scout.py -q" in rule["validation_commands"]
