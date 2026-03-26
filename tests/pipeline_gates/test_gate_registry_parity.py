"""
test_gate_registry_parity.py
============================
Anti-regressão FASE 1 — AGENT_COMPLIANCE_EXECUTION_PLAN.md

Garante paridade bidirecional entre:
  - docs/_canon/gates/GATES_REGISTRY.yaml (registry normativo)
  - scripts/contracts/validate/validate_contracts.py (executor real)

Falha se:
  1. Um gate for adicionado ao executor sem ser registrado no registry.
  2. Um gate ativo no registry (que deveria estar inline no executor) sumir do executor.

Exceções by-design:
  - Gates com status=deferred no registry → ignorados na verificação de presença no executor.
  - Gates com integrated_in_validate_contracts=false → são passos externos, não exigidos inline.
"""
import pathlib
import re
import sys

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).parents[2]
REGISTRY_PATH = REPO_ROOT / "docs" / "_canon" / "gates" / "GATES_REGISTRY.yaml"
EXECUTOR_PATH = REPO_ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _executor_gate_ids() -> set[str]:
    """
    Extrai gate IDs do executor via três métodos:
    1. Tuplas de gate_plan: ("GATE_NAME", lambda: ...)
    2. Dicts inline: "gate_id": "GATE_NAME" (ex: AXIOM_INTEGRITY_GATE)
    3. Atribuições diretas: gate_id = "GATE_NAME" (ex: READINESS_SUMMARY_GATE)
    """
    text = EXECUTOR_PATH.read_text(encoding="utf-8")

    # Método 1: gate_plan tuples — captura ("GATE_ID", lambda: ...)
    from_plan = set(re.findall(r'\("([A-Z_]+_GATE)",\s*lambda:', text))

    # Método 2: inline dict keys — "gate_id": "GATE_ID"
    from_inline = set(re.findall(r'"gate_id":\s*"([A-Z_]+_GATE)"', text))

    # Método 3: assignment — gate_id = "GATE_ID"
    from_assignment = set(re.findall(r'gate_id\s*=\s*"([A-Z_]+_GATE)"', text))

    return from_plan | from_inline | from_assignment


def _registry_active_ids() -> set[str]:
    """Gates ativos no registry que DEVEM estar no executor (inline CI gates)."""
    registry = _load_registry()
    result = set()
    for gate in registry.get("gates", []):
        gid = gate.get("gate_id")
        if not gid:
            continue
        status = gate.get("status", "active")
        # Ignorar deferred e external scripts
        if status == "deferred":
            continue
        if gate.get("integrated_in_validate_contracts") is False:
            continue
        result.add(gid)
    return result


def _all_registry_ids() -> set[str]:
    """Todos os gate IDs no registry (qualquer status)."""
    registry = _load_registry()
    return {g["gate_id"] for g in registry.get("gates", []) if "gate_id" in g}


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

class TestGateRegistryParity:

    def test_registry_is_loadable_yaml(self):
        """Registry deve ser YAML válido e ter chave 'gates'."""
        registry = _load_registry()
        assert "gates" in registry, "GATES_REGISTRY.yaml deve ter chave 'gates'"
        assert isinstance(registry["gates"], list), "'gates' deve ser uma lista"
        assert len(registry["gates"]) > 0, "Registry não pode estar vazio"

    def test_executor_gates_all_in_registry(self):
        """
        Todo gate executado inline em validate_contracts.py deve estar no registry.
        Falha com lista dos gates faltando para forçar registro antes de execução.
        """
        executor_ids = _executor_gate_ids()
        registry_ids = _all_registry_ids()

        missing_from_registry = executor_ids - registry_ids

        assert not missing_from_registry, (
            f"Gates executados em validate_contracts.py mas AUSENTES do GATES_REGISTRY.yaml:\n"
            + "\n".join(f"  - {g}" for g in sorted(missing_from_registry))
            + "\n\nAdicione esses gates ao registro antes de continuar."
        )

    def test_active_registry_gates_all_in_executor(self):
        """
        Todo gate com status=active e integrated_in_validate_contracts != false
        deve estar presente no executor.
        Gates deferred e external scripts são explicitamente excluídos.
        """
        executor_ids = _executor_gate_ids()
        active_inline_ids = _registry_active_ids()

        missing_from_executor = active_inline_ids - executor_ids

        assert not missing_from_executor, (
            f"Gates ATIVOS no GATES_REGISTRY.yaml mas AUSENTES de validate_contracts.py:\n"
            + "\n".join(f"  - {g}" for g in sorted(missing_from_executor))
            + "\n\nDecida: implementar no executor OU marcar como status=deferred "
            + "OU adicionar integrated_in_validate_contracts: false no registry."
        )

    def test_deferred_gates_not_in_executor(self):
        """
        Gates marcados como status=deferred não devem estar no executor.
        Se foram implementados, o status deve ser atualizado para active.
        """
        executor_ids = _executor_gate_ids()
        registry = _load_registry()

        deferred_ids = {
            g["gate_id"]
            for g in registry.get("gates", [])
            if g.get("status") == "deferred" and "gate_id" in g
        }

        implemented_but_deferred = deferred_ids & executor_ids

        assert not implemented_but_deferred, (
            f"Gates marcados como status=deferred no registry mas ENCONTRADOS no executor:\n"
            + "\n".join(f"  - {g}" for g in sorted(implemented_but_deferred))
            + "\n\nAtualize o status desses gates para 'active' no GATES_REGISTRY.yaml."
        )

    def test_external_gates_not_in_executor_inline(self):
        """
        Gates com integrated_in_validate_contracts=false não devem estar
        no gate_plan inline do executor (podem aparecer em comentários/referências).
        """
        text = EXECUTOR_PATH.read_text(encoding="utf-8")
        # Apenas tuplas do gate_plan (não comentários ou strings de referência)
        from_plan = set(re.findall(r'\("([A-Z_]+_GATE)",\s*lambda:', text))

        registry = _load_registry()
        external_ids = {
            g["gate_id"]
            for g in registry.get("gates", [])
            if g.get("integrated_in_validate_contracts") is False and "gate_id" in g
        }

        external_in_plan = external_ids & from_plan

        assert not external_in_plan, (
            f"Gates marcados como external (integrated_in_validate_contracts=false) "
            f"foram encontrados NO gate_plan do executor:\n"
            + "\n".join(f"  - {g}" for g in sorted(external_in_plan))
            + "\n\nSe o gate foi integrado ao executor, remova integrated_in_validate_contracts: false."
        )

    def test_all_registry_entries_have_required_fields(self):
        """Todo gate no registry deve ter gate_id, status e description."""
        registry = _load_registry()
        problems = []
        for gate in registry.get("gates", []):
            gid = gate.get("gate_id", "<sem gate_id>")
            missing = [f for f in ["gate_id", "status", "description"] if f not in gate]
            if missing:
                problems.append(f"{gid}: campos ausentes = {missing}")
        assert not problems, (
            "Entradas do registry sem campos obrigatórios:\n"
            + "\n".join(f"  - {p}" for p in problems)
        )

    def test_registry_version_is_current(self):
        """Registry deve ter campo version (para rastreabilidade de mudanças)."""
        registry = _load_registry()
        assert "version" in registry, "GATES_REGISTRY.yaml deve ter campo 'version'"
        assert registry["version"], "Campo 'version' não pode estar vazio"

    def test_no_duplicate_gate_ids_in_registry(self):
        """Não pode haver gate_id duplicado no registry."""
        registry = _load_registry()
        ids = [g["gate_id"] for g in registry.get("gates", []) if "gate_id" in g]
        seen = set()
        duplicates = []
        for gid in ids:
            if gid in seen:
                duplicates.append(gid)
            seen.add(gid)
        assert not duplicates, (
            f"gate_ids duplicados no GATES_REGISTRY.yaml: {duplicates}"
        )
