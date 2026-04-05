from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    f"compiled_context/training/FT-{n:03d}.json"
    for n in range(1, 11)
}


def test_compile_expected_training_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "training")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    ft001_content = next(item.content for item in expected if item.relpath.endswith("FT-001.json"))
    payload = json.loads(ft001_content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "training"
    assert payload["feature"]["id"] == "FT-001"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/training.yaml"]
    assert "POST /training-sessions" in payload["feature"]["endpoints"]
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "src/training/api.py" in payload["implementation_targets"]["canonical_runtime"]


def test_compile_expected_training_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "training")
    second = compile_expected(REPO_ROOT, "training")
    assert first == second


def test_write_and_check_expected_training_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "training")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_training_and_all():
    training_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
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
    assert sorted(training_payload["features"]) == [f"FT-{n:03d}" for n in range(1, 11)]

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
    assert "training" in {batch_payload.get("module")} | set(batch_payload.get("modules", []))


def test_training_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "TRAINING_SOURCE_GRAPH_SYNC")

    for n in range(1, 11):
        assert f"compiled_context/training/FT-{n:03d}.json" in rule["required_consumers"]
    assert "python3 scripts/compile/compile_context_bundle.py --module training --check --format json" in rule["validation_commands"]
