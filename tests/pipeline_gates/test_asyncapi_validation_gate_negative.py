"""
Negative enforcement tests for ASYNCAPI_VALIDATION_GATE (issue #108).

Cada teste injeta uma violação no asyncapi.yaml, roda
`_g12_asyncapi_validation(tmp_path)` e asserta que o gate falhou
com `BLOCKED_ASYNCAPI_INVALID`.

Pattern: tmp_path com node_modules symlink + asyncapi.yaml mutado.
"""
from __future__ import annotations

import os
import pathlib

import pytest
import yaml

from scripts.contracts.validate import validate_contracts as gates

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
NODE_MODULES = REPO_ROOT / "node_modules"


def _ensure_asyncapi_available() -> None:
    if not NODE_MODULES.exists():
        pytest.skip("node_modules ausente — rode `npm ci`")
    if not (NODE_MODULES / ".bin" / "asyncapi").exists():
        pytest.skip("asyncapi CLI não encontrada em node_modules/.bin")


def _seed_workspace(tmp_path: pathlib.Path, doc: dict | str) -> pathlib.Path:
    (tmp_path / "contracts" / "asyncapi").mkdir(parents=True, exist_ok=True)
    target = tmp_path / "contracts" / "asyncapi" / "asyncapi.yaml"
    if isinstance(doc, str):
        target.write_text(doc, encoding="utf-8")
    else:
        target.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    nm_link = tmp_path / "node_modules"
    if not nm_link.exists():
        os.symlink(NODE_MODULES, nm_link, target_is_directory=True)
    return target


def _valid_asyncapi_doc() -> dict:
    """Documento AsyncAPI 2.6 mínimo válido."""
    return {
        "asyncapi": "2.6.0",
        "info": {"title": "Negative Test Async API", "version": "0.0.1"},
        "channels": {
            "training.session.created": {
                "publish": {
                    "operationId": "publishTrainingSessionCreated",
                    "message": {
                        "name": "TrainingSessionCreated",
                        "payload": {
                            "type": "object",
                            "properties": {
                                "training_session_id": {"type": "string"},
                            },
                            "required": ["training_session_id"],
                        },
                    },
                }
            }
        },
    }


def _is_error_infra(result: dict) -> bool:
    return result.get("blocking_code") == "ERROR_INFRA"


def _assert_gate_blocked(result: dict, code: str = "BLOCKED_ASYNCAPI_INVALID") -> None:
    if _is_error_infra(result):
        pytest.skip(f"AsyncAPI ERROR_INFRA: {result.get('reason')}")
    assert result["status"] == "FAIL", (
        f"esperava FAIL, recebeu {result['status']}: {result.get('reason')}"
    )
    assert result.get("blocking_code") == code, (
        f"esperava blocking_code={code}, recebeu {result.get('blocking_code')}"
    )
    assert result.get("violations"), "esperava violations não-vazio"


# ---------------------------------------------------------------------------
# Sanidade
# ---------------------------------------------------------------------------

def test_baseline_valid_doc_passes(tmp_path: pathlib.Path) -> None:
    _ensure_asyncapi_available()
    _seed_workspace(tmp_path, _valid_asyncapi_doc())
    result = gates._g12_asyncapi_validation(tmp_path)
    if _is_error_infra(result):
        pytest.skip(f"AsyncAPI ERROR_INFRA: {result.get('reason')}")
    assert result["status"] == "PASS", (
        f"baseline deveria passar — {result.get('reason')} | "
        f"violations={[v.get('message') for v in result.get('violations', [])]}"
    )


# ---------------------------------------------------------------------------
# Negativos
# ---------------------------------------------------------------------------

def test_fail_when_asyncapi_version_field_missing(tmp_path: pathlib.Path) -> None:
    """Campo top-level 'asyncapi' obrigatório."""
    _ensure_asyncapi_available()
    doc = _valid_asyncapi_doc()
    del doc["asyncapi"]
    _seed_workspace(tmp_path, doc)
    result = gates._g12_asyncapi_validation(tmp_path)
    _assert_gate_blocked(result)


def test_fail_when_asyncapi_version_unsupported(tmp_path: pathlib.Path) -> None:
    """Versão AsyncAPI inexistente deve ser rejeitada."""
    _ensure_asyncapi_available()
    doc = _valid_asyncapi_doc()
    doc["asyncapi"] = "9.9.9"
    _seed_workspace(tmp_path, doc)
    result = gates._g12_asyncapi_validation(tmp_path)
    _assert_gate_blocked(result)


def test_fail_when_asyncapi_info_title_missing(tmp_path: pathlib.Path) -> None:
    """info.title é obrigatório por schema AsyncAPI."""
    _ensure_asyncapi_available()
    doc = _valid_asyncapi_doc()
    del doc["info"]["title"]
    _seed_workspace(tmp_path, doc)
    result = gates._g12_asyncapi_validation(tmp_path)
    _assert_gate_blocked(result)


def test_fail_when_asyncapi_info_version_missing(tmp_path: pathlib.Path) -> None:
    """info.version é obrigatório por schema AsyncAPI."""
    _ensure_asyncapi_available()
    doc = _valid_asyncapi_doc()
    del doc["info"]["version"]
    _seed_workspace(tmp_path, doc)
    result = gates._g12_asyncapi_validation(tmp_path)
    _assert_gate_blocked(result)


def test_fail_when_yaml_is_malformed(tmp_path: pathlib.Path) -> None:
    """YAML sintaticamente inválido deve ser rejeitado."""
    _ensure_asyncapi_available()
    bad_yaml = "asyncapi: 2.6.0\ninfo: { title: 'broken\n  invalid: yaml: here\n"
    _seed_workspace(tmp_path, bad_yaml)
    result = gates._g12_asyncapi_validation(tmp_path)
    _assert_gate_blocked(result)


def test_fail_when_channels_field_missing(tmp_path: pathlib.Path) -> None:
    """channels é obrigatório em AsyncAPI 2.x."""
    _ensure_asyncapi_available()
    doc = _valid_asyncapi_doc()
    del doc["channels"]
    _seed_workspace(tmp_path, doc)
    result = gates._g12_asyncapi_validation(tmp_path)
    _assert_gate_blocked(result)
