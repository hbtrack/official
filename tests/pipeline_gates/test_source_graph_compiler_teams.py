from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_source_graph import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "generated/source_graph/teams/teams.bundle.yaml",
    "generated/source_graph/teams/teams.schema_contract_view.yaml",
    "generated/source_graph/teams/teams.openapi_contract_view.yaml",
    "generated/source_graph/teams/impact_report.json",
}


def test_compile_expected_teams_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "teams")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    bundle = yaml.safe_load(next(item.content for item in expected if item.relpath.endswith(".bundle.yaml")))
    assert bundle["module"] == "teams"
    assert bundle["compiler"] == "hbtrack_source_graph_compiler"
    assert set(bundle["entities"]) == {"Team"}

    schema_view = yaml.safe_load(next(item.content for item in expected if item.relpath.endswith(".schema_contract_view.yaml")))
    assert schema_view["primary_entity"] == "Team"
    assert set(schema_view["entities"]) == {"Team"}

    impact = json.loads(next(item.content for item in expected if item.relpath.endswith("impact_report.json")))
    assert impact["module"] == "teams"
    assert impact["blocked_partial_update"] is True
    assert set(impact["outputs"]) == EXPECTED_OUTPUTS


def test_compile_expected_teams_is_deterministic():
    first = compile_expected(REPO_ROOT, "teams")
    second = compile_expected(REPO_ROOT, "teams")
    assert first == second


def test_write_and_check_expected_teams_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "teams")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_compile_source_graph_cli_check_passes_for_teams_and_all():
    teams_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_source_graph.py"),
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
    assert teams_payload["module"] == "teams"

    batch_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_source_graph.py"),
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
