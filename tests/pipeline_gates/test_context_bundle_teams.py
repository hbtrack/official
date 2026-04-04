from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/teams/FT-024.json",
    "compiled_context/teams/FT-025.json",
    "compiled_context/teams/FT-026.json",
    "compiled_context/teams/FT-027.json",
    "compiled_context/teams/FT-028.json",
    "compiled_context/teams/FT-029.json",
    "compiled_context/teams/FT-030.json",
    "compiled_context/teams/FT-031.json",
}


def test_compile_expected_teams_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "teams")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    # Verify FT-024 (listTeams) bundle content
    ft024_content = next(item.content for item in expected if item.relpath.endswith("FT-024.json"))
    payload = json.loads(ft024_content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "teams"
    assert payload["feature"]["id"] == "FT-024"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/teams.yaml"]
    assert payload["feature"]["endpoints"] == ["GET /teams"]
    assert [item["operation_id"] for item in payload["source_graph"]["operations"]] == ["listTeams"]
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "compiled_context/teams/FT-024.json" in payload["implementation_targets"]["derived_context"]
    assert "src/teams/api.py" in payload["implementation_targets"]["canonical_runtime"]

    # Verify all 8 FTs are present and reference the correct module
    for ft_item in expected:
        ft_payload = json.loads(ft_item.content)
        assert ft_payload["module"] == "teams"
        assert ft_payload["compiler"] == "hbtrack_context_bundle_compiler"


def test_compile_expected_teams_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "teams")
    second = compile_expected(REPO_ROOT, "teams")
    assert first == second


def test_write_and_check_expected_teams_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "teams")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_teams_and_all():
    teams_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "teams",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert teams_result.returncode == 0, teams_result.stdout + teams_result.stderr
    teams_payload = json.loads(teams_result.stdout)
    assert teams_payload["status"] == "PASS"
    assert sorted(teams_payload["features"]) == [
        "FT-024", "FT-025", "FT-026", "FT-027", "FT-028", "FT-029", "FT-030", "FT-031"
    ]

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
    assert "teams" in {batch_payload.get("module")} | set(batch_payload.get("modules", []))


def test_teams_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "TEAMS_SOURCE_GRAPH_SYNC")

    for ft_id in ["FT-024", "FT-025", "FT-026", "FT-027", "FT-028", "FT-029", "FT-030", "FT-031"]:
        assert f"compiled_context/teams/{ft_id}.json" in rule["required_consumers"]
        assert f"compiled_context/teams/{ft_id}.json" in rule["blocking_consumers"]

    assert "python3 scripts/compile/compile_context_bundle.py --module teams --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_teams_source_graph_integrity.py tests/pipeline_gates/test_source_graph_compiler_teams.py tests/pipeline_gates/test_context_bundle_teams.py -q" in rule["validation_commands"]
