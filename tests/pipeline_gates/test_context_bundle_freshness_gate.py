"""
test_context_bundle_freshness_gate.py
======================================
B7-002 — Gate CONTEXT_BUNDLE_FRESHNESS_GATE

Cobre:
  1. Gate retorna SKIP quando compiled_context/ ausente.
  2. Gate retorna SKIP quando não há *.json em compiled_context/.
  3. Gate retorna PASS quando todos os inputs batem com o hash registrado.
  4. Gate retorna FAIL quando um input foi alterado (hash diverge).
  5. Gate retorna FAIL quando um input referenciado está ausente no disco.
  6. Gate retorna FAIL quando o bundle é ilegível (JSON inválido).
  7. O gate está registrado no GATES_REGISTRY.yaml.
  8. O gate está implementado no executor validate_contracts.py.
  9. Gate integrado: repositório real passa com bundle fresco.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.contracts.validate.validate_contracts import _g_context_bundle_freshness  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _make_bundle(tmp_path: pathlib.Path, inputs: list[dict], module: str = "testmod") -> pathlib.Path:
    """Cria um bundle JSON mínimo em tmp_path/compiled_context/<module>/FT-001.json."""
    bundle_dir = tmp_path / "compiled_context" / module
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / "FT-001.json"
    bundle_path.write_text(
        json.dumps(
            {
                "artifact_id": "HBTRACK_MODULE_FEATURE_CONTEXT_BUNDLE",
                "module": module,
                "inputs": inputs,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return bundle_path


# ---------------------------------------------------------------------------
# Testes unitários
# ---------------------------------------------------------------------------

def test_skip_when_compiled_context_absent(tmp_path: pathlib.Path):
    result = _g_context_bundle_freshness(tmp_path)
    assert result["status"] in ("SKIP", "SKIP_NOT_APPLICABLE")
    assert result["gate_id"] == "CONTEXT_BUNDLE_FRESHNESS_GATE"


def test_skip_when_no_json_bundles(tmp_path: pathlib.Path):
    (tmp_path / "compiled_context").mkdir()
    (tmp_path / "compiled_context" / "README.md").write_text("vazio", encoding="utf-8")
    result = _g_context_bundle_freshness(tmp_path)
    assert result["status"] in ("SKIP", "SKIP_NOT_APPLICABLE")


def test_pass_when_all_inputs_fresh(tmp_path: pathlib.Path):
    # Cria um arquivo de input real
    src_file = tmp_path / "docs" / "module.yaml"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    content = b"module: testmod\nversion: 1\n"
    src_file.write_bytes(content)

    inputs = [{"relpath": "docs/module.yaml", "sha256": _sha256(content)}]
    _make_bundle(tmp_path, inputs)

    result = _g_context_bundle_freshness(tmp_path)
    assert result["status"] == "PASS", result.get("summary")
    assert result["blocking"] is True


def test_fail_when_input_hash_diverges(tmp_path: pathlib.Path):
    src_file = tmp_path / "docs" / "module.yaml"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    original_content = b"module: testmod\n"
    src_file.write_bytes(original_content)

    # Registra hash do conteúdo original, mas depois altera o arquivo
    inputs = [{"relpath": "docs/module.yaml", "sha256": _sha256(original_content)}]
    _make_bundle(tmp_path, inputs)

    # Altera o arquivo após compilar o bundle → bundle fica stale
    src_file.write_bytes(b"module: testmod\nversion: changed\n")

    result = _g_context_bundle_freshness(tmp_path)
    assert result["status"] == "FAIL"
    assert result["blocking"] is True
    violations = result.get("violations") or []
    assert any("BLOCKED_CONTEXT_BUNDLE_STALE" == v.get("blocking_code") for v in violations)
    assert any("docs/module.yaml" in v.get("message", "") for v in violations)


def test_fail_when_input_file_absent(tmp_path: pathlib.Path):
    # Referencia arquivo que não existe
    inputs = [{"relpath": "docs/missing.yaml", "sha256": "aabbcc"}]
    _make_bundle(tmp_path, inputs)

    result = _g_context_bundle_freshness(tmp_path)
    assert result["status"] == "FAIL"
    violations = result.get("violations") or []
    assert any("ausente" in v.get("message", "") for v in violations)


def test_fail_when_bundle_is_invalid_json(tmp_path: pathlib.Path):
    bundle_dir = tmp_path / "compiled_context" / "broken"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "FT-bad.json").write_text("{not_json", encoding="utf-8")

    result = _g_context_bundle_freshness(tmp_path)
    assert result["status"] == "FAIL"
    violations = result.get("violations") or []
    assert any("ilegível" in v.get("message", "") or "Bundle" in v.get("message", "") for v in violations)


# ---------------------------------------------------------------------------
# Testes normativos (registry + executor)
# ---------------------------------------------------------------------------

def test_gate_registered_in_gates_registry():
    registry_path = REPO_ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
    assert registry_path.exists(), "GATES_REGISTRY.yaml ausente"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in registry.get("gates", [])}
    assert "CONTEXT_BUNDLE_FRESHNESS_GATE" in gate_ids, (
        "CONTEXT_BUNDLE_FRESHNESS_GATE não encontrado no GATES_REGISTRY.yaml"
    )


def test_gate_registered_as_active_and_blocking():
    registry_path = REPO_ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    gate = next(
        (g for g in registry.get("gates", []) if g.get("gate_id") == "CONTEXT_BUNDLE_FRESHNESS_GATE"),
        None,
    )
    assert gate is not None
    assert gate.get("status") == "active"
    assert gate.get("blocking") is True


def test_gate_present_in_executor():
    executor_path = REPO_ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"
    text = executor_path.read_text(encoding="utf-8")
    assert "CONTEXT_BUNDLE_FRESHNESS_GATE" in text, (
        "CONTEXT_BUNDLE_FRESHNESS_GATE não encontrado em validate_contracts.py"
    )
    assert "_g_context_bundle_freshness" in text


# ---------------------------------------------------------------------------
# Teste de integração: repositório real
# ---------------------------------------------------------------------------

def test_gate_passes_against_real_repo():
    """Bundle real (compiled_context/reports/FT-039.json) deve ser fresco."""
    result = _g_context_bundle_freshness(REPO_ROOT)
    assert result["status"] in ("PASS", "SKIP", "SKIP_NOT_APPLICABLE"), (
        f"Gate falhou no repositório real: {result.get('summary')}\n"
        f"Violations: {result.get('violations')}"
    )
