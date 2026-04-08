"""B11-001 — Bundle compilado obrigatório para tarefas de implementação.

Verifica que:
1. TASK_CATALOG declara bundle_required=true para generate_code e execute_roadmap_phase
2. compiled_context/ existe para todos os 17 módulos canônicos
3. Cada módulo tem ao menos um bundle compilado
4. generate_code.prompt.md e execute_roadmap_phase.prompt.md referenciam o requisito de bundle
"""
from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_CATALOG_PATH = REPO_ROOT / ".contract_driven" / "TASK_CATALOG.yaml"
COMPILED_CONTEXT_PATH = REPO_ROOT / "compiled_context"
GENERATE_CODE_PROMPT = REPO_ROOT / ".contract_driven" / "agent_prompts" / "generate_code.prompt.md"
EXECUTE_ROADMAP_PROMPT = REPO_ROOT / ".contract_driven" / "agent_prompts" / "execute_roadmap_phase.prompt.md"

CANONICAL_MODULES = [
    "users", "seasons", "teams", "training", "wellness", "medical",
    "competitions", "matches", "scout", "exercises", "analytics",
    "reports", "ai_ingestion", "identity_access", "audit",
    "notifications", "video",
]

IMPLEMENTATION_TASK_TYPES = ["generate_code", "execute_roadmap_phase"]


def _load_catalog() -> dict:
    return yaml.safe_load(TASK_CATALOG_PATH.read_text(encoding="utf-8"))


class TestTaskCatalogBundleRequirement:
    """TASK_CATALOG deve declarar bundle_required=true para tarefas de implementação."""

    def test_generate_code_has_bundle_required(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["generate_code"]
        assert task.get("bundle_required") is True, (
            "generate_code deve ter bundle_required: true (B11-001)"
        )

    def test_execute_roadmap_phase_has_bundle_required(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["execute_roadmap_phase"]
        assert task.get("bundle_required") is True, (
            "execute_roadmap_phase deve ter bundle_required: true (B11-001)"
        )

    def test_generate_code_has_bundle_path_template(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["generate_code"]
        tmpl = task.get("bundle_path_template", "")
        assert "compiled_context" in tmpl, (
            "generate_code.bundle_path_template deve referenciar compiled_context/"
        )

    def test_execute_roadmap_phase_has_bundle_path_template(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["execute_roadmap_phase"]
        tmpl = task.get("bundle_path_template", "")
        assert "compiled_context" in tmpl, (
            "execute_roadmap_phase.bundle_path_template deve referenciar compiled_context/"
        )

    def test_generate_code_has_bundle_enforcement_text(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["generate_code"]
        enforcement = task.get("bundle_enforcement", "")
        assert enforcement, "generate_code deve ter bundle_enforcement definido"

    def test_execute_roadmap_phase_has_bundle_enforcement_text(self):
        catalog = _load_catalog()
        task = catalog["task_catalog"]["execute_roadmap_phase"]
        enforcement = task.get("bundle_enforcement", "")
        assert enforcement, "execute_roadmap_phase deve ter bundle_enforcement definido"


class TestCompiledContextCoverage:
    """compiled_context/ deve cobrir todos os 17 módulos canônicos."""

    def test_compiled_context_dir_exists(self):
        assert COMPILED_CONTEXT_PATH.is_dir(), (
            f"compiled_context/ não existe em {COMPILED_CONTEXT_PATH}"
        )

    def test_all_canonical_modules_have_context_dir(self):
        missing = [
            m for m in CANONICAL_MODULES
            if not (COMPILED_CONTEXT_PATH / m).is_dir()
        ]
        assert not missing, (
            f"Módulos sem compiled_context/: {missing}. "
            "Executar compile_context_bundle.py para gerar."
        )

    def test_all_canonical_modules_have_at_least_one_bundle(self):
        empty = [
            m for m in CANONICAL_MODULES
            if not list((COMPILED_CONTEXT_PATH / m).glob("*.json"))
        ]
        assert not empty, (
            f"Módulos com compiled_context/ vazio: {empty}. "
            "Executar compile_context_bundle.py --module <m> para popular."
        )


class TestPromptsBundleRequirement:
    """Worker prompts de implementação devem referenciar o requisito de bundle."""

    def test_generate_code_prompt_references_bundle(self):
        content = GENERATE_CODE_PROMPT.read_text(encoding="utf-8")
        assert "compiled_context" in content, (
            "generate_code.prompt.md deve mencionar compiled_context/ como pré-requisito"
        )
        assert "compile_context_bundle" in content, (
            "generate_code.prompt.md deve referenciar compile_context_bundle.py como comando de recuperação"
        )

    def test_execute_roadmap_prompt_references_bundle(self):
        content = EXECUTE_ROADMAP_PROMPT.read_text(encoding="utf-8")
        assert "compiled_context" in content, (
            "execute_roadmap_phase.prompt.md deve mencionar compiled_context/ como pré-requisito"
        )
        assert "compile_context_bundle" in content, (
            "execute_roadmap_phase.prompt.md deve referenciar compile_context_bundle.py como comando de recuperação"
        )
