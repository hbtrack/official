from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
DOC_USAGE_MANIFEST_PATH = ROOT / "docs" / "_canon" / "DOC_USAGE_MANIFEST.yaml"


def _registry_gates() -> dict[str, dict]:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {g["gate_id"]: g for g in data.get("gates", [])}


# ---------------------------------------------------------------------------
# Registry checks
# ---------------------------------------------------------------------------


def test_doc_usage_gate_in_registry():
    gates = _registry_gates()
    assert "DOC_USAGE_GATE" in gates, "DOC_USAGE_GATE deve estar em GATES_REGISTRY.yaml"
    g = gates["DOC_USAGE_GATE"]
    assert g.get("status") == "active"
    assert g.get("blocking") is True
    assert "BLOCKED_DOC_MISSING" in (g.get("blocking_codes") or [])


def test_canon_contract_driven_parity_gate_in_registry():
    gates = _registry_gates()
    assert "CANON_CONTRACT_DRIVEN_PARITY_GATE" in gates
    g = gates["CANON_CONTRACT_DRIVEN_PARITY_GATE"]
    assert g.get("status") == "active"
    assert g.get("blocking") is True
    assert "BLOCKED_CANON_DRIFT" in (g.get("blocking_codes") or [])


def test_hbtrack_canon_parity_gate_in_registry():
    gates = _registry_gates()
    assert "HBTRACK_CANON_PARITY_GATE" in gates
    g = gates["HBTRACK_CANON_PARITY_GATE"]
    assert g.get("status") == "active"
    assert g.get("blocking") is True
    assert "BLOCKED_HBTRACK_CANON_DRIFT" in (g.get("blocking_codes") or [])


# ---------------------------------------------------------------------------
# DOC_USAGE_MANIFEST structure
# ---------------------------------------------------------------------------


def test_doc_usage_manifest_exists():
    assert DOC_USAGE_MANIFEST_PATH.exists(), "DOC_USAGE_MANIFEST.yaml deve existir"


def test_doc_usage_manifest_has_entries():
    data = yaml.safe_load(DOC_USAGE_MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = (data or {}).get("entries", [])
    assert len(entries) >= 30, (
        f"DOC_USAGE_MANIFEST deve ter pelo menos 30 entradas, encontrado {len(entries)}"
    )


def test_doc_usage_manifest_entries_have_rule_id():
    data = yaml.safe_load(DOC_USAGE_MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = (data or {}).get("entries", [])
    for entry in entries:
        assert "rule_id" in entry, f"Entrada sem rule_id: {entry}"


def test_doc_usage_manifest_entries_have_paths_or_globs():
    data = yaml.safe_load(DOC_USAGE_MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = (data or {}).get("entries", [])
    for entry in entries:
        has_paths = bool(entry.get("paths"))
        has_globs = bool(entry.get("path_globs"))
        assert has_paths or has_globs, (
            f"Entrada {entry.get('rule_id')} deve ter 'paths' ou 'path_globs'"
        )


# ---------------------------------------------------------------------------
# Gate logic (unit tests with tmp_path fixtures)
# ---------------------------------------------------------------------------


def test_doc_usage_gate_skips_without_manifest(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_doc_usage(tmp_path)
    assert result["status"] == "SKIP_NOT_APPLICABLE", (
        f"Gate deve SKIP sem DOC_USAGE_MANIFEST, obteve: {result['status']}"
    )


def test_doc_usage_gate_pass_when_all_paths_exist(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    canon_dir = tmp_path / "docs" / "_canon"
    canon_dir.mkdir(parents=True)

    doc_a = tmp_path / "docs" / "_canon" / "GLOBAL_INVARIANTS.md"
    doc_b = tmp_path / "docs" / "_canon" / "DOMAIN_GLOSSARY.md"
    doc_a.write_text("# Global Invariants\n", encoding="utf-8")
    doc_b.write_text("# Domain Glossary\n", encoding="utf-8")

    manifest = {
        "entries": [
            {
                "rule_id": "TEST_EXPLICIT",
                "class": "canon_global",
                "paths": [
                    "docs/_canon/GLOBAL_INVARIANTS.md",
                    "docs/_canon/DOMAIN_GLOSSARY.md",
                ],
                "freshness_mode": "template_parity",
            }
        ]
    }
    (canon_dir / "DOC_USAGE_MANIFEST.yaml").write_text(
        yaml.dump(manifest), encoding="utf-8"
    )

    result = vc._g_doc_usage(tmp_path)
    assert result["status"] == "PASS", (
        f"Gate deve PASS quando todos os paths existem, obteve: {result['status']}"
    )


def test_doc_usage_gate_fail_when_explicit_path_missing(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    canon_dir = tmp_path / "docs" / "_canon"
    canon_dir.mkdir(parents=True)

    manifest = {
        "entries": [
            {
                "rule_id": "TEST_MISSING",
                "class": "canon_global",
                "paths": ["docs/_canon/DOES_NOT_EXIST.md"],
                "freshness_mode": "template_parity",
            }
        ]
    }
    (canon_dir / "DOC_USAGE_MANIFEST.yaml").write_text(
        yaml.dump(manifest), encoding="utf-8"
    )

    result = vc._g_doc_usage(tmp_path)
    assert result["status"] == "FAIL", (
        f"Gate deve FAIL quando path explícito está ausente, obteve: {result['status']}"
    )
    violations = result.get("violations", [])
    assert any(
        v.get("type") == "missing_explicit_path" for v in violations
    ), "Deve haver violação do tipo missing_explicit_path"


def test_doc_usage_gate_pass_when_glob_has_no_matches(tmp_path):
    """Glob sem correspondência deve gerar WARN, não FAIL."""
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    canon_dir = tmp_path / "docs" / "_canon"
    canon_dir.mkdir(parents=True)

    manifest = {
        "entries": [
            {
                "rule_id": "TEST_EMPTY_GLOB",
                "class": "module_doc",
                "path_globs": ["docs/hbtrack/modulos/*/NONEXISTENT_*.md"],
                "freshness_mode": "template_parity",
            }
        ]
    }
    (canon_dir / "DOC_USAGE_MANIFEST.yaml").write_text(
        yaml.dump(manifest), encoding="utf-8"
    )

    result = vc._g_doc_usage(tmp_path)
    # Empty globs produce warnings, not failures — gate should PASS
    assert result["status"] == "PASS", (
        f"Gate deve PASS quando glob tem 0 matches (apenas aviso), obteve: {result['status']}"
    )


# ---------------------------------------------------------------------------
# Real-world integration: manifest passes against actual repo
# ---------------------------------------------------------------------------


def test_doc_usage_gate_pass_on_real_repo():
    """DOC_USAGE_GATE deve PASS no repositório real (todos os paths explícitos existem)."""
    sys.path.insert(0, str(ROOT / "scripts" / "contracts" / "validate"))
    import validate_contracts as vc

    result = vc._g_doc_usage(ROOT)
    assert result["status"] == "PASS", (
        f"DOC_USAGE_GATE deve PASS no repositório real, obteve: {result['status']}\n"
        f"Violações: {result.get('violations', [])}"
    )
