"""
Carregador canônico do contract pack do módulo ATLETAS.

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml


# Documentos obrigatórios do módulo ATLETAS
REQUIRED_DOCS = [
    "00_ATLETAS_CROSS_LINTER_RULES.json",
    "01_ATLETAS_OPENAPI.yaml",
    "08_ATLETAS_TRACEABILITY.yaml",
    "12_ATLETAS_EXECUTION_BINDINGS.yaml",
    "13_ATLETAS_DB_CONTRACT.yaml",
    "14_ATLETAS_UI_CONTRACT.yaml",
    "15_ATLETAS_INVARIANTS.yaml",
    "17_ATLETAS_PROJECTIONS.yaml",
    "18_ATLETAS_SIDE_EFFECTS.yaml",
    "19_ATLETAS_TEST_SCENARIOS.yaml",
    "20_ATLETAS_EXECUTOR_RESTRICTION_PROMPT.md",
]

OPTIONAL_DOCS = [
    "05_ATLETAS_EVENTS.asyncapi.yaml",
    "16_ATLETAS_AGENT_HANDOFF.json",
]


def _load_file(path: Path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")


def load_contract_pack(module_root: Path) -> dict[str, object]:
    """Carrega todos os documentos do contract pack por nome canônico."""
    contracts: dict[str, object] = {}

    for name in REQUIRED_DOCS + OPTIONAL_DOCS:
        path = module_root / name
        if path.exists():
            contracts[name] = _load_file(path)

    return contracts


# ─── Governance v2 ────────────────────────────────────────────────────────────

import pathlib as _pathlib
import json as _json


def load_engine_and_module_contracts(
    constitution_path,
    module_rules_path,
):
    """Carrega ENGINE_CONSTITUTION.json e 00_*_MODULE_RULES.json sem merge."""
    constitution = _json.loads(
        _pathlib.Path(constitution_path).read_text(encoding="utf-8")
    )
    module_rules = _json.loads(
        _pathlib.Path(module_rules_path).read_text(encoding="utf-8")
    )
    return constitution, module_rules


# REGRA DE NOMENCLATURA (VERIFIQUE 2 fechado):
# module_id em UPPER-CASE no contrato (meta.module_id = "ATLETAS")
# module_id em lower-case APENAS no path de filesystem (".../modulos/atletas/...")
# Essa assimetria e intencional e deve ser mantida em todos os pontos do codigo.
def resolve_governance_paths(repo_root, module_id):
    """Retorna (constitution_path, module_rules_path) para um module_id."""
    root = _pathlib.Path(repo_root)
    const_path = (
        root / "docs" / "hbtrack" / "_governance" / "ENGINE_CONSTITUTION.json"
    )
    module_path = (
        root
        / "docs"
        / "hbtrack"
        / "modulos"
        / module_id.lower()
        / f"00_{module_id.upper()}_MODULE_RULES.json"
    )
    if not const_path.exists():
        raise FileNotFoundError(
            f"ENGINE_CONSTITUTION.json not found: {const_path}"
        )
    if not module_path.exists():
        raise FileNotFoundError(f"Module rules not found: {module_path}")
    return const_path, module_path
