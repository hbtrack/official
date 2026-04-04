from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/competitions/FT-034.json",
}


def test_compile_expected_competitions_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "competitions")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    # Verify FT-034 (competitions) bundle content
    ft034_content = next(item.content for item in expected if item.relpath.endswith("FT-034.json"))
    payload = json.loads(ft034_content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "competitions"
    assert payload["feature"]["id"] == "FT-034"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/competitions.yaml"]
    assert "GET /competitions" in payload["feature"]["endpoints"]
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "compiled_context/competitions/FT-034.json" in payload["implementation_targets"]["derived_context"]
    assert "src/competitions/api.py" in payload["implementation_targets"]["canonical_runtime"]

    # Verify all FTs reference the correct module
    for ft_item in expected:
        ft_payload = json.loads(ft_item.content)
        assert ft_payload["module"] == "competitions"
        assert ft_payload["compiler"] == "hbtrack_context_bundle_compiler"


def test_compile_expected_competitions_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "competitions")
    second = compile_expected(REPO_ROOT, "competitions")
    assert first == second


def test_write_and_check_expected_competitions_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "competitions")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_competitions_and_all():
    competitions_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "competitions",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert competitions_result.returncode == 0, competitions_result.stdout + competitions_result.stderr
    competitions_payload = json.loads(competitions_result.stdout)
    assert competitions_payload["status"] == "PASS"
    assert sorted(competitions_payload["features"]) == ["FT-034"]

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
    assert "competitions" in {batch_payload.get("module")} | set(batch_payload.get("modules", []))


def test_competitions_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "COMPETITIONS_SOURCE_GRAPH_SYNC")

    assert "compiled_context/competitions/FT-034.json" in rule["required_consumers"]
    assert "compiled_context/competitions/FT-034.json" in rule["blocking_consumers"]

    assert "python3 scripts/compile/compile_context_bundle.py --module competitions --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_competitions_source_graph_integrity.py tests/pipeline_gates/test_source_graph_compiler_competitions.py tests/pipeline_gates/test_context_bundle_competitions.py -q" in rule["validation_commands"]
