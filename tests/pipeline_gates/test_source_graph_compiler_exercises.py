from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_source_graph import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "generated/source_graph/exercises/exercises.bundle.yaml",
    "generated/source_graph/exercises/exercises.schema_contract_view.yaml",
    "generated/source_graph/exercises/exercises.openapi_contract_view.yaml",
    "generated/source_graph/exercises/impact_report.json",
}


def test_compile_expected_exercises_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "exercises")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    bundle = yaml.safe_load(next(item.content for item in expected if item.relpath.endswith(".bundle.yaml")))
    assert bundle["module"] == "exercises"
    assert bundle["compiler"] == "hbtrack_source_graph_compiler"
    assert set(bundle["entities"]) == {"Exercise", "ExerciseVersion", "ExerciseRelation", "ExerciseAcl"}

    schema_view = yaml.safe_load(next(item.content for item in expected if item.relpath.endswith(".schema_contract_view.yaml")))
    assert schema_view["primary_entity"] == "Exercise"
    assert set(schema_view["entities"]) == {"Exercise", "ExerciseVersion", "ExerciseRelation", "ExerciseAcl"}

    impact = json.loads(next(item.content for item in expected if item.relpath.endswith("impact_report.json")))
    assert impact["module"] == "exercises"
    assert impact["blocked_partial_update"] is True
    assert set(impact["outputs"]) == EXPECTED_OUTPUTS


def test_compile_expected_exercises_is_deterministic():
    first = compile_expected(REPO_ROOT, "exercises")
    second = compile_expected(REPO_ROOT, "exercises")
    assert first == second


def test_write_and_check_expected_exercises_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "exercises")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_compile_source_graph_cli_check_passes_for_exercises_and_all():
    exercises_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_source_graph.py"),
            "--module",
            "exercises",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert exercises_result.returncode == 0, exercises_result.stdout + exercises_result.stderr
    exercises_payload = json.loads(exercises_result.stdout)
    assert exercises_payload["status"] == "PASS"
    assert exercises_payload["module"] == "exercises"

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
    assert {"reports", "analytics", "exercises"} <= set(batch_payload["modules"])


def test_hb_cli_compile_source_graph_check_passes_for_all_modules():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "hb"),
            "compile-source-graph",
            "--all",
            "--check",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
