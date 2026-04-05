from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_source_graph import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "generated/source_graph/training/training.bundle.yaml",
    "generated/source_graph/training/training.schema_contract_view.yaml",
    "generated/source_graph/training/training.openapi_contract_view.yaml",
    "generated/source_graph/training/impact_report.json",
}


def test_compile_expected_training_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "training")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    bundle = next(item for item in expected if item.relpath.endswith("training.bundle.yaml"))
    bundle_data = yaml.safe_load(bundle.content)
    assert set(bundle_data["entities"].keys()) == {"TrainingSession"}

    schema_view = next(item for item in expected if item.relpath.endswith("training.schema_contract_view.yaml"))
    schema_data = yaml.safe_load(schema_view.content)
    assert schema_data["primary_entity"] == "TrainingSession"

    impact = next(item for item in expected if item.relpath.endswith("impact_report.json"))
    impact_data = json.loads(impact.content)
    assert impact_data["blocked_partial_update"] is True


def test_compile_expected_training_is_deterministic():
    first = compile_expected(REPO_ROOT, "training")
    second = compile_expected(REPO_ROOT, "training")
    assert first == second


def test_write_and_check_expected_training_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "training")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_compile_source_graph_cli_check_passes_for_training_and_all():
    training_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_source_graph.py"),
            "--module",
            "training",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert training_result.returncode == 0, training_result.stdout + training_result.stderr
    training_payload = json.loads(training_result.stdout)
    assert training_payload["status"] == "PASS"
    assert training_payload["module"] == "training"

    all_result = subprocess.run(
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
    assert all_result.returncode == 0, all_result.stdout + all_result.stderr
    all_payload = json.loads(all_result.stdout)
    assert all_payload["status"] == "PASS"
    assert "training" in all_payload.get("modules", [])
