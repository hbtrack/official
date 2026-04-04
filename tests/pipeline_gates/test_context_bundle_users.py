from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.compile.compile_context_bundle import check_expected, compile_expected, write_expected


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OUTPUTS = {
    "compiled_context/users/FT-014.json",
    "compiled_context/users/FT-015.json",
    "compiled_context/users/FT-016.json",
    "compiled_context/users/FT-017.json",
}


def test_compile_expected_users_context_bundle_emits_required_outputs():
    expected = compile_expected(REPO_ROOT, "users")
    assert {item.relpath for item in expected} == EXPECTED_OUTPUTS

    # Verificar FT-014 (listUsers) bundle content
    ft014_content = next(item.content for item in expected if item.relpath.endswith("FT-014.json"))
    payload = json.loads(ft014_content)
    assert payload["artifact_id"] == "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE"
    assert payload["compiler"] == "hbtrack_context_bundle_compiler"
    assert payload["module"] == "users"
    assert payload["feature"]["id"] == "FT-014"
    assert payload["feature"]["status"] == "implemented"
    assert payload["feature"]["contracts"] == ["contracts/openapi/paths/users.yaml"]
    assert "GET /users" in payload["feature"]["endpoints"]
    assert payload["source_graph"]["impact_report"]["blocked_partial_update"] is True
    assert "src/users/api.py" in payload["implementation_targets"]["canonical_runtime"]

    # Verificar que todos os FTs pertencem ao módulo users
    for ft_item in expected:
        ft_payload = json.loads(ft_item.content)
        assert ft_payload["module"] == "users"
        assert ft_payload["compiler"] == "hbtrack_context_bundle_compiler"


def test_compile_expected_users_context_bundle_is_deterministic():
    first = compile_expected(REPO_ROOT, "users")
    second = compile_expected(REPO_ROOT, "users")
    assert first == second


def test_write_and_check_expected_users_context_bundle_roundtrip(tmp_path: Path):
    expected = compile_expected(REPO_ROOT, "users")
    written = write_expected(tmp_path, expected)

    assert set(written) == EXPECTED_OUTPUTS
    assert check_expected(tmp_path, expected) == []


def test_context_bundle_cli_check_passes_for_users_and_all():
    users_result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "compile" / "compile_context_bundle.py"),
            "--module",
            "users",
            "--check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert users_result.returncode == 0, users_result.stdout + users_result.stderr
    users_payload = json.loads(users_result.stdout)
    assert users_payload["status"] == "PASS"
    assert sorted(users_payload["features"]) == ["FT-014", "FT-015", "FT-016", "FT-017"]

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
    assert "users" in {batch_payload.get("module")} | set(batch_payload.get("modules", []))


def test_users_sync_manifest_requires_context_bundle():
    sync_manifest = yaml.safe_load((REPO_ROOT / "docs" / "_canon" / "SYNC_MANIFEST.yaml").read_text(encoding="utf-8"))
    rule = next(item for item in sync_manifest["rules"] if item["rule_id"] == "USERS_SOURCE_GRAPH_SYNC")

    for ft in ("FT-014", "FT-015", "FT-016", "FT-017"):
        assert f"compiled_context/users/{ft}.json" in rule["required_consumers"]

    assert "python3 scripts/compile/compile_context_bundle.py --module users --check --format json" in rule["validation_commands"]
    assert "python3 -m pytest tests/pipeline_gates/test_users_source_graph_integrity.py tests/pipeline_gates/test_source_graph_compiler_users.py tests/pipeline_gates/test_context_bundle_users.py -q" in rule["validation_commands"]
