"""B11-002 — Matriz de operabilidade do agente.

Verifica que o agente possui trilha fechada (task_type + prompt existente + seções mínimas)
para cada tipo de trabalho da matriz mínima obrigatória:

  1. novo módulo               → new_module
  2. nova feature em módulo    → feature_update  (B11-002: criado neste PR)
  3. alteração de regra global → contract_revision
  4. revisão de contrato       → contract_revision
  5. código derivado de cont.  → generate_code
"""
from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_CATALOG_PATH = REPO_ROOT / ".contract_driven" / "TASK_CATALOG.yaml"
PROMPTS_DIR = REPO_ROOT / ".contract_driven" / "agent_prompts"

# Mapeamento: descrição do trabalho → task_type canônico
OPERABILITY_MATRIX = {
    "novo_modulo": "new_module",
    "nova_feature_em_modulo_existente": "feature_update",
    "alteracao_de_regra_global_ou_revisao_contrato": "contract_revision",
    "mudanca_de_codigo_derivada_de_contrato": "generate_code",
}

# Seções mínimas que cada prompt deve conter
REQUIRED_PROMPT_SECTIONS = ["Pré-requisito", "Input"]


def _load_catalog() -> dict:
    return yaml.safe_load(TASK_CATALOG_PATH.read_text(encoding="utf-8"))


def _get_task(catalog: dict, task_type: str) -> dict:
    return catalog["task_catalog"][task_type]


class TestOperabilityMatrixTaskCatalog:
    """Cada tipo de trabalho da matriz deve ter entrada no TASK_CATALOG."""

    def test_new_module_in_catalog(self):
        catalog = _load_catalog()
        assert "new_module" in catalog["task_catalog"], (
            "new_module ausente do TASK_CATALOG"
        )

    def test_feature_update_in_catalog(self):
        catalog = _load_catalog()
        assert "feature_update" in catalog["task_catalog"], (
            "feature_update ausente do TASK_CATALOG — trilha para nova feature em módulo existente não definida (B11-002)"
        )

    def test_contract_revision_in_catalog(self):
        catalog = _load_catalog()
        assert "contract_revision" in catalog["task_catalog"], (
            "contract_revision ausente do TASK_CATALOG"
        )

    def test_generate_code_in_catalog(self):
        catalog = _load_catalog()
        assert "generate_code" in catalog["task_catalog"], (
            "generate_code ausente do TASK_CATALOG"
        )

    def test_all_matrix_task_types_are_active(self):
        catalog = _load_catalog()
        frozen_or_inactive = []
        for work_type, task_type in OPERABILITY_MATRIX.items():
            entry = catalog["task_catalog"].get(task_type, {})
            status = entry.get("status", "unknown")
            if status not in ("active",):
                frozen_or_inactive.append(f"{task_type} (status={status}, work={work_type})")
        assert not frozen_or_inactive, (
            f"Task types da matriz com status inativo/frozen: {frozen_or_inactive}"
        )


class TestOperabilityMatrixPrompts:
    """Cada task_type da matriz deve ter um prompt existente com seções mínimas."""

    def _prompt_path(self, task_type: str) -> Path:
        catalog = _load_catalog()
        entry = catalog["task_catalog"][task_type]
        return REPO_ROOT / entry["worker_path"]

    def test_new_module_prompt_exists(self):
        path = self._prompt_path("new_module")
        assert path.exists(), f"Prompt new_module não encontrado: {path}"

    def test_feature_update_prompt_exists(self):
        path = self._prompt_path("feature_update")
        assert path.exists(), (
            f"Prompt feature_update não encontrado: {path} — "
            "trilha para nova feature sem prompt operacional (B11-002)"
        )

    def test_contract_revision_prompt_exists(self):
        path = self._prompt_path("contract_revision")
        assert path.exists(), f"Prompt contract_revision não encontrado: {path}"

    def test_generate_code_prompt_exists(self):
        path = self._prompt_path("generate_code")
        assert path.exists(), f"Prompt generate_code não encontrado: {path}"

    def test_feature_update_prompt_has_prerequisites(self):
        path = self._prompt_path("feature_update")
        content = path.read_text(encoding="utf-8")
        assert "Pré-requisito" in content, (
            "feature_update.prompt.md não define pré-requisitos obrigatórios"
        )

    def test_feature_update_prompt_has_input_section(self):
        path = self._prompt_path("feature_update")
        content = path.read_text(encoding="utf-8")
        assert "Input" in content, (
            "feature_update.prompt.md não define seção de Input esperado"
        )

    def test_feature_update_prompt_references_bundle(self):
        path = self._prompt_path("feature_update")
        content = path.read_text(encoding="utf-8")
        assert "compiled_context" in content, (
            "feature_update.prompt.md deve exigir bundle compilado (B11-001)"
        )

    def test_feature_update_prompt_defines_change_types(self):
        path = self._prompt_path("feature_update")
        content = path.read_text(encoding="utf-8")
        for ct in ("extend", "fix", "deprecate", "new_endpoint"):
            assert ct in content, (
                f"feature_update.prompt.md não cobre change_type='{ct}'"
            )


class TestOperabilityMatrixBundleRequirement:
    """Tasks de implementação da matriz devem declarar bundle_required."""

    def test_feature_update_has_bundle_required(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["feature_update"]
        assert task.get("bundle_required") is True, (
            "feature_update deve ter bundle_required: true (B11-001 + B11-002)"
        )

    def test_generate_code_has_bundle_required(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["generate_code"]
        assert task.get("bundle_required") is True, (
            "generate_code deve ter bundle_required: true (B11-001)"
        )


class TestOperabilityMatrixWorkerPaths:
    """worker_path de cada task_type da matriz deve apontar para arquivo existente."""

    def test_all_matrix_prompts_resolvable(self):
        catalog = _load_catalog()
        missing = []
        for work_type, task_type in OPERABILITY_MATRIX.items():
            entry = catalog["task_catalog"].get(task_type, {})
            worker_path = entry.get("worker_path", "")
            if not worker_path:
                missing.append(f"{task_type}: worker_path ausente")
                continue
            full = REPO_ROOT / worker_path
            if not full.exists():
                missing.append(f"{task_type}: {worker_path} não existe")
        assert not missing, (
            f"Prompts ausentes na matriz de operabilidade:\n" + "\n".join(missing)
        )
