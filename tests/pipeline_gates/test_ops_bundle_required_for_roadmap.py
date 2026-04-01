"""
test_ops_bundle_required_for_roadmap.py
========================================
B-OPS-006 — Bundles operacionais para tasks de roadmap/deploy

Cobre:
  1. compiled_context/ops/deploy.json existe e é JSON válido.
  2. compiled_context/ops/runtime.json existe e é JSON válido.
  3. deploy.json contém campos obrigatórios (artifact_id, inputs, deploy_contract, environments).
  4. runtime.json contém campos obrigatórios (artifact_id, inputs, services, endpoints).
  5. Todos os inputs referenciados existem no disco.
  6. Hashes SHA-256 dos inputs batem com os valores registrados no bundle.
  7. deploy.json referencia os artefatos canônicos de ops corretos.
  8. runtime.json referencia os artefatos canônicos de ops corretos.
  9. execute_roadmap_phase.prompt.md menciona bundles ops como pré-requisito.
  10. SKILL.md do hb-roadmap-executor menciona o bundle ops como pré-requisito.
  11. CLAUDE.md menciona bundles ops nas regras transversais.
  12. CONTEXT_BUNDLE_FRESHNESS_GATE detecta bundles ops stale corretamente.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

DEPLOY_BUNDLE = REPO_ROOT / "compiled_context" / "ops" / "deploy.json"
RUNTIME_BUNDLE = REPO_ROOT / "compiled_context" / "ops" / "runtime.json"

DEPLOY_REQUIRED_FIELDS = {"artifact_id", "inputs", "deploy_contract", "environments", "validation"}
RUNTIME_REQUIRED_FIELDS = {"artifact_id", "inputs", "services", "endpoints", "validation"}

DEPLOY_EXPECTED_INPUTS = {
    "docs/_canon/graph/ops/deploy_contract.yaml",
    "docs/_canon/graph/ops/environment_catalog.yaml",
    "docs/_canon/graph/ops/secrets_catalog.yaml",
    "docs/_canon/graph/ops/github_actions_catalog.yaml",
    "docs/_canon/SYNC_MANIFEST.yaml",
    "docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml",
}

RUNTIME_EXPECTED_INPUTS = {
    "docs/_canon/graph/ops/service_topology.yaml",
    "docs/_canon/graph/ops/runtime_endpoints.yaml",
    "docs/_canon/graph/ops/environment_catalog.yaml",
    "docs/_canon/SYNC_MANIFEST.yaml",
    "docs/_canon/SOURCE_AUTHORITY_GRAPH.yaml",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Testes de existência e validade estrutural
# ---------------------------------------------------------------------------

def test_deploy_bundle_exists():
    assert DEPLOY_BUNDLE.exists(), (
        f"compiled_context/ops/deploy.json não existe. "
        "Criar o bundle antes de executar tasks de deploy/CI-CD."
    )


def test_runtime_bundle_exists():
    assert RUNTIME_BUNDLE.exists(), (
        f"compiled_context/ops/runtime.json não existe. "
        "Criar o bundle antes de executar tasks de VPS/topologia."
    )


def test_deploy_bundle_is_valid_json():
    data = _load(DEPLOY_BUNDLE)
    assert isinstance(data, dict)


def test_runtime_bundle_is_valid_json():
    data = _load(RUNTIME_BUNDLE)
    assert isinstance(data, dict)


def test_deploy_bundle_has_required_fields():
    data = _load(DEPLOY_BUNDLE)
    missing = DEPLOY_REQUIRED_FIELDS - set(data.keys())
    assert not missing, f"deploy.json sem campos obrigatórios: {missing}"


def test_runtime_bundle_has_required_fields():
    data = _load(RUNTIME_BUNDLE)
    missing = RUNTIME_REQUIRED_FIELDS - set(data.keys())
    assert not missing, f"runtime.json sem campos obrigatórios: {missing}"


# ---------------------------------------------------------------------------
# Testes de inputs canônicos
# ---------------------------------------------------------------------------

def test_deploy_bundle_references_canonical_ops_inputs():
    data = _load(DEPLOY_BUNDLE)
    actual = {entry["relpath"] for entry in data.get("inputs", [])}
    missing = DEPLOY_EXPECTED_INPUTS - actual
    assert not missing, f"deploy.json não referencia inputs ops obrigatórios: {missing}"


def test_runtime_bundle_references_canonical_ops_inputs():
    data = _load(RUNTIME_BUNDLE)
    actual = {entry["relpath"] for entry in data.get("inputs", [])}
    missing = RUNTIME_EXPECTED_INPUTS - actual
    assert not missing, f"runtime.json não referencia inputs ops obrigatórios: {missing}"


# ---------------------------------------------------------------------------
# Testes de freshness (hashes)
# ---------------------------------------------------------------------------

def test_deploy_bundle_inputs_exist_on_disk():
    data = _load(DEPLOY_BUNDLE)
    for entry in data.get("inputs", []):
        relpath = entry["relpath"]
        full = REPO_ROOT / relpath
        assert full.exists(), f"deploy.json referencia input ausente: {relpath}"


def test_runtime_bundle_inputs_exist_on_disk():
    data = _load(RUNTIME_BUNDLE)
    for entry in data.get("inputs", []):
        relpath = entry["relpath"]
        full = REPO_ROOT / relpath
        assert full.exists(), f"runtime.json referencia input ausente: {relpath}"


def test_deploy_bundle_input_hashes_match():
    data = _load(DEPLOY_BUNDLE)
    for entry in data.get("inputs", []):
        relpath = entry["relpath"]
        stored_hash = entry.get("sha256", "")
        actual_hash = _sha256(REPO_ROOT / relpath)
        assert actual_hash == stored_hash, (
            f"deploy.json stale: input '{relpath}' foi alterado. "
            "Recompilar o bundle operacional."
        )


def test_runtime_bundle_input_hashes_match():
    data = _load(RUNTIME_BUNDLE)
    for entry in data.get("inputs", []):
        relpath = entry["relpath"]
        stored_hash = entry.get("sha256", "")
        actual_hash = _sha256(REPO_ROOT / relpath)
        assert actual_hash == stored_hash, (
            f"runtime.json stale: input '{relpath}' foi alterado. "
            "Recompilar o bundle operacional."
        )


# ---------------------------------------------------------------------------
# Testes normativos — referência nos artefatos canônicos
# ---------------------------------------------------------------------------

def test_execute_roadmap_phase_prompt_references_ops_bundles():
    prompt = REPO_ROOT / ".contract_driven" / "agent_prompts" / "execute_roadmap_phase.prompt.md"
    assert prompt.exists()
    text = prompt.read_text(encoding="utf-8")
    assert "compiled_context/ops/deploy.json" in text, (
        "execute_roadmap_phase.prompt.md não menciona compiled_context/ops/deploy.json"
    )
    assert "compiled_context/ops/runtime.json" in text, (
        "execute_roadmap_phase.prompt.md não menciona compiled_context/ops/runtime.json"
    )


def test_roadmap_executor_skill_references_ops_bundles():
    skill = REPO_ROOT / ".github" / "skills" / "hb-roadmap-executor" / "SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert "compiled_context/ops/deploy.json" in text, (
        "SKILL.md do hb-roadmap-executor não menciona compiled_context/ops/deploy.json"
    )
    assert "compiled_context/ops/runtime.json" in text, (
        "SKILL.md do hb-roadmap-executor não menciona compiled_context/ops/runtime.json"
    )


def test_claude_md_references_ops_bundles():
    claude_md = REPO_ROOT / "CLAUDE.md"
    assert claude_md.exists()
    text = claude_md.read_text(encoding="utf-8")
    assert "compiled_context/ops/deploy.json" in text, (
        "CLAUDE.md não menciona compiled_context/ops/deploy.json nas regras transversais"
    )
    assert "compiled_context/ops/runtime.json" in text, (
        "CLAUDE.md não menciona compiled_context/ops/runtime.json nas regras transversais"
    )
