from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/seasons/FT-018.json",
    "compiled_context/seasons/FT-019.json",
    "compiled_context/seasons/FT-020.json",
    "compiled_context/seasons/FT-021.json",
    "compiled_context/seasons/FT-022.json",
    "compiled_context/seasons/FT-023.json",
}


def test_compile_expected_seasons_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "seasons")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    # Verify FT-018 (listSeasons) bundle content
    ft018_content = next(item.content for item in expected if item.relpath.endswith("FT-018.json"))
    payload = json.loads(ft018_content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "seasons"
    assert payload["feature"]["id"] == "FT-018"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/seasons.yaml"]
    assert payload["feature"]["endpoints"] == ["GET /seasons"]
    assert [item["operation_id"] for item in payload["source_graph"]["operations"]] == ["listSeasons"]
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "compiled_context/seasons/FT-018.json" in payload["implementation_targets"]["derived_context"]
    assert "src/seasons/api.py" in payload["implementation_targets"]["canonical_runtime"]

    # Verify all 6 FTs are present and reference the correct module
    for ft_item in expected:
        ft_payload = json.loads(ft_item.content)
        assert ft_payload["module"] == "seasons"
        assert ft_payload["compiler"] == "hbtrack_context_bundle_compiler"


def test_compile_expected_seasons_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "seasons")
    second = compile_expected(REPO_ROOT, "seasons")
    assert first == second


def test_write_and_check_expected_seasons_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "seasons")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_seasons_and_all():
    seasons_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "seasons",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert seasons_result.returncode == 0, seasons_result.stdout + seasons_result.stderr
    seasons_payload = json.loads(seasons_result.stdout)
    assert seasons_payload["status"] == "PASS"
    assert sorted(seasons_payload["features"]) == ["FT-018", "FT-019", "FT-020", "FT-021", "FT-022", "FT-023"]

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
    assert "seasons" in {batch_payload.get("module")} | set(batch_payload.get("modules", []))


def test_seasons_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "SEASONS_SOURCE_GRAPH_SYNC")

    for ft_id in ["FT-018", "FT-019", "FT-020", "FT-021", "FT-022", "FT-023"]:
        assert f"compiled_context/seasons/{ft_id}.json" in rule["required_consumers"]
        assert f"compiled_context/seasons/{ft_id}.json" in rule["blocking_consumers"]

    assert "python3 scripts/compile/compile_context_bundle.py --module seasons --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_seasons_source_graph_integrity.py tests/pipeline_gates/test_source_graph_compiler_seasons.py tests/pipeline_gates/test_context_bundle_seasons.py -q" in rule["validation_commands"]
