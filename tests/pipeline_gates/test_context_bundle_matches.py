from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/matches/FT-035.json",
}


def test_compile_expected_matches_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "matches")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    ft035_content = next(item.content for item in expected if item.relpath.endswith("FT-035.json"))
    payload = json.loads(ft035_content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "matches"
    assert payload["feature"]["id"] == "FT-035"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/matches.yaml"]
    assert "GET /matches" in payload["feature"]["endpoints"]
    assert "PUT /matches/{matchId}/lineup/{userId}" in payload["feature"]["endpoints"]
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "src/matches/api.py" in payload["implementation_targets"]["canonical_runtime"]


def test_compile_expected_matches_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "matches")
    second = compile_expected(REPO_ROOT, "matches")
    assert first == second


def test_write_and_check_expected_matches_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "matches")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_matches_and_all():
    matches_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "matches",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert matches_result.returncode == 0, matches_result.stdout + matches_result.stderr
    matches_payload = json.loads(matches_result.stdout)
    assert matches_payload["status"] == "PASS"
    assert sorted(matches_payload["features"]) == ["FT-035"]

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
    assert "matches" in {batch_payload.get("module")} | set(batch_payload.get("modules", []))


def test_matches_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "MATCHES_SOURCE_GRAPH_SYNC")

    assert "compiled_context/matches/FT-035.json" in rule["required_consumers"]
    assert "python3 scripts/compile/compile_context_bundle.py --module matches --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_matches_source_graph_integrity.py tests/pipeline_gates/test_source_graph_compiler_matches.py tests/pipeline_gates/test_context_bundle_matches.py -q" in rule["validation_commands"]
