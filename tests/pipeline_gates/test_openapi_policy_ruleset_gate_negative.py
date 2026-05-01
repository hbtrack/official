"""
Negative enforcement tests for OPENAPI_POLICY_RULESET_GATE (issue #108).

Cada teste injeta a violação de uma regra `error` em `.spectral.yaml`,
roda `_g6_openapi_policy_ruleset(tmp_path)` e asserta que o gate falhou
com a regra correspondente listada em `violations[]`.

Pattern: tmp_path com .spectral.yaml + node_modules symlink + openapi.yaml mutado.
"""
from __future__ import annotations

import os
import pathlib
import shutil

import pytest
import yaml

from scripts.contracts.validate import validate_contracts as gates

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SPECTRAL_CFG = REPO_ROOT / ".spectral.yaml"
NODE_MODULES = REPO_ROOT / "node_modules"


def _ensure_spectral_available() -> None:
    if not SPECTRAL_CFG.exists():
        pytest.skip(".spectral.yaml ausente no repo")
    if not NODE_MODULES.exists():
        pytest.skip("node_modules ausente — rode `npm ci` para habilitar spectral")
    if not (NODE_MODULES / ".bin" / "spectral").exists():
        pytest.skip("spectral CLI não encontrada em node_modules/.bin")


def _seed_workspace(tmp_path: pathlib.Path, openapi_doc: dict) -> pathlib.Path:
    """Monta um workspace mínimo em tmp_path para o gate consumir."""
    (tmp_path / "contracts" / "openapi").mkdir(parents=True, exist_ok=True)
    openapi_file = tmp_path / "contracts" / "openapi" / "openapi.yaml"
    openapi_file.write_text(yaml.safe_dump(openapi_doc, sort_keys=False), encoding="utf-8")
    shutil.copy2(SPECTRAL_CFG, tmp_path / ".spectral.yaml")
    nm_link = tmp_path / "node_modules"
    if not nm_link.exists():
        os.symlink(NODE_MODULES, nm_link, target_is_directory=True)
    return openapi_file


def _valid_openapi_doc() -> dict:
    """Documento OpenAPI 3.1 mínimo que satisfaz todas as regras `error`."""
    return {
        "openapi": "3.1.0",
        "info": {"title": "Negative Test API", "version": "0.0.1"},
        "servers": [{"url": "https://api.example.com"}],
        "tags": [{"name": "training", "description": "Training module"}],
        "security": [],
        "paths": {
            "/training-sessions": {
                "get": {
                    "operationId": "listTrainingSessions",
                    "tags": ["training"],
                    "responses": {
                        "200": {"description": "OK"},
                        "500": {
                            "description": "Server error",
                            "content": {
                                "application/problem+json": {
                                    "schema": {"$ref": "#/components/schemas/problem"}
                                }
                            },
                        },
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "problem": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "title": {"type": "string"},
                        "status": {"type": "integer"},
                        "detail": {"type": "string"},
                    },
                    "required": ["type", "title", "status"],
                }
            }
        },
    }


def _has_violation_with_code(result: dict, code_substring: str) -> bool:
    for v in result.get("violations", []):
        msg = v.get("message", "")
        if code_substring.lower() in msg.lower():
            return True
    return False


def _is_error_infra(result: dict) -> bool:
    return result.get("blocking_code") == "ERROR_INFRA"


def _assert_gate_blocked(result: dict, expected_rule: str) -> None:
    if _is_error_infra(result):
        pytest.skip(f"Spectral ERROR_INFRA: {result.get('reason')}")
    assert result["status"] == "FAIL", f"esperava FAIL, recebeu {result['status']}: {result}"
    assert _has_violation_with_code(result, expected_rule), (
        f"violação esperada para '{expected_rule}' não encontrada. "
        f"violations={[v.get('message') for v in result.get('violations', [])]}"
    )


# ---------------------------------------------------------------------------
# Sanidade: documento válido deve PASSAR (controle positivo)
# ---------------------------------------------------------------------------

def test_baseline_valid_doc_passes(tmp_path: pathlib.Path) -> None:
    _ensure_spectral_available()
    _seed_workspace(tmp_path, _valid_openapi_doc())
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    if _is_error_infra(result):
        pytest.skip(f"Spectral ERROR_INFRA: {result.get('reason')}")
    errors = [v for v in result.get("violations", []) if v.get("severity") == "error"]
    assert not errors, (
        "documento de baseline deveria passar sem erros — "
        "investigue se a fixture _valid_openapi_doc() viola alguma regra. "
        f"errors={[v.get('message') for v in errors]}"
    )


# ---------------------------------------------------------------------------
# Negativos — uma regra error por teste
# ---------------------------------------------------------------------------

def test_fail_when_openapi_version_violated(tmp_path: pathlib.Path) -> None:
    """hbtrack-openapi-version: openapi deve ser 3.1.x"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    doc["openapi"] = "3.0.3"
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-openapi-version")


def test_fail_when_operation_id_missing(tmp_path: pathlib.Path) -> None:
    """hbtrack-operation-id-required: toda operação deve ter operationId"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    del doc["paths"]["/training-sessions"]["get"]["operationId"]
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-operation-id-required")


def test_fail_when_tag_description_missing(tmp_path: pathlib.Path) -> None:
    """hbtrack-tag-description: toda tag deve ter description"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    doc["tags"] = [{"name": "training"}]
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-tag-description")


def test_fail_when_uri_versioning_present(tmp_path: pathlib.Path) -> None:
    """hbtrack-no-uri-versioning: paths com /v1/ são proibidos"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    doc["paths"] = {
        "/v1/training-sessions": doc["paths"].pop("/training-sessions"),
    }
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-no-uri-versioning")


def test_fail_when_info_title_missing(tmp_path: pathlib.Path) -> None:
    """hbtrack-info-title: info.title obrigatório"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    del doc["info"]["title"]
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-info-title")


def test_fail_when_info_version_missing(tmp_path: pathlib.Path) -> None:
    """hbtrack-info-version: info.version obrigatório"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    del doc["info"]["version"]
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-info-version")


def test_fail_when_servers_missing(tmp_path: pathlib.Path) -> None:
    """hbtrack-servers-defined: servers deve existir"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    del doc["servers"]
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-servers-defined")


def test_fail_when_problem_schema_undeclared(tmp_path: pathlib.Path) -> None:
    """hbtrack-problem-schema-declared: components.schemas.problem obrigatório"""
    _ensure_spectral_available()
    doc = _valid_openapi_doc()
    doc["components"]["schemas"].pop("problem")
    _seed_workspace(tmp_path, doc)
    result = gates._g6_openapi_policy_ruleset(tmp_path)
    _assert_gate_blocked(result, "hbtrack-problem-schema-declared")
