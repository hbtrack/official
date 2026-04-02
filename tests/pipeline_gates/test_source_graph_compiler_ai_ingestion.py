from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_source_graph import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "generated/source_graph/ai_ingestion/ai_ingestion.bundle.yaml",
    "generated/source_graph/ai_ingestion/ai_ingestion.schema_contract_view.yaml",
    "generated/source_graph/ai_ingestion/ai_ingestion.openapi_contract_view.yaml",
    "generated/source_graph/ai_ingestion/impact_report.json",
}


def test_compile_expected_ai_ingestion_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "ai_ingestion")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    bundle = yaml.safe_load(next(item.content for item in expected if item.relpath.endswith(".bundle.yaml")))
    assert bundle["module"] == "ai_ingestion"
    assert bundle["compiler"] == "hbtrack_source_graph_compiler"
    assert set(bundle["entities"]) == {"IngestionJob"}

    schema_view = yaml.safe_load(next(item.content for item in expected if item.relpath.endswith(".schema_contract_view.yaml")))
    assert schema_view["primary_entity"] == "IngestionJob"
    assert set(schema_view["entities"]) == {"IngestionJob"}

    impact = json.loads(next(item.content for item in expected if item.relpath.endswith("impact_report.json")))
    assert impact["module"] == "ai_ingestion"
    assert impact["blocked_partial_update"] is True
    assert set(impact["outputs"]) == EXPECTED_OUTPUTS


def test_compile_expected_ai_ingestion_is_deterministic():
    first = compile_expected(REPO_ROOT, "ai_ingestion")
    second = compile_expected(REPO_ROOT, "ai_ingestion")
    assert first == second


def test_write_and_check_expected_ai_ingestion_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "ai_ingestion")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_compile_source_graph_cli_check_passes_for_ai_ingestion_and_all():
    ai_ingestion_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_source_graph.py"),
            "--module",
            "ai_ingestion",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ai_ingestion_result.returncode == 0, ai_ingestion_result.stdout + ai_ingestion_result.stderr
    ai_ingestion_payload = json.loads(ai_ingestion_result.stdout)
    assert ai_ingestion_payload["status"] == "PASS"
    assert ai_ingestion_payload["module"] == "ai_ingestion"

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
    assert {"reports", "analytics", "exercises", "notifications", "wellness", "medical", "ai_ingestion"} <= set(batch_payload["modules"])


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
