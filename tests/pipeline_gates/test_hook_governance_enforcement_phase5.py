"""
tests/pipeline_gates/test_hook_governance_enforcement_phase5.py

FASE 5 — ENFORCEMENT OBRIGATÓRIO EM HOOK E CI

Testa as mudanças da Fase 5 do AGENT_COMPLIANCE_EXECUTION_PLAN.md:
  - pre-commit hook v4: GOVERNANCE_PATHS definida como constante de classe
  - pre-commit hook: get_staged_governance_files() detecta mudanças nos paths corretos
  - pre-commit hook: check_governance_integrity() existe e chama survival-suite
  - pre-commit hook: versão atualizada para v4
  - scripts/hb survival-suite inclui testes das FASEs 3 e 4
  - contract-gates.yml tem job governance-enforcement com survival-suite
  - contract-gates.yml tem path filters via dorny/paths-filter
  - contract-gates.yml tem jobs de paridade registry×executor e schema×template×skills
  - contract-gates.yml tem job de validação cruzada SESSION_HANDOFF ↔ session_start
"""

import importlib.machinery
import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent

PRE_COMMIT_HOOK = REPO_ROOT / "scripts" / "git-hooks" / "pre-commit"
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "contract-gates.yml"

# Paths de governança esperados no hook
EXPECTED_GOVERNANCE_PATHS = [
    ".contract_driven/",
    "docs/_canon/",
    ".github/copilot-instructions.md",
    ".github/skills/",
    "scripts/contracts/validate/",
    "scripts/hb",
    "contracts/schemas/shared/",
]

# Testes esperados na survival-suite (FASEs 3 e 4)
EXPECTED_SURVIVAL_TESTS = [
    "test_session_state_phase3",
    "test_schema_template_parity_phase4",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_hook_class():
    """Importa HBHookValidator do hook sem disparar main()."""
    spec = importlib.util.spec_from_loader(
        "pre_commit_phase5",
        importlib.machinery.SourceFileLoader("pre_commit_phase5", str(PRE_COMMIT_HOOK)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.HBHookValidator


# ---------------------------------------------------------------------------
# Testes do pre-commit hook
# ---------------------------------------------------------------------------

class TestPreCommitGovernancePaths:
    """Hook v4: GOVERNANCE_PATHS deve cobrir todos os paths de governança relevantes."""

    def test_hook_exists(self):
        assert PRE_COMMIT_HOOK.exists(), f"Hook não encontrado: {PRE_COMMIT_HOOK}"

    def test_hook_version_v4(self):
        content = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
        assert "v4" in content, "Hook deve ser versão v4 (Governance Path Enforcement)"

    def test_governance_paths_constant_defined(self):
        """GOVERNANCE_PATHS deve estar definido como constante da classe."""
        HBHookValidator = _load_hook_class()
        assert hasattr(HBHookValidator, "GOVERNANCE_PATHS"), (
            "HBHookValidator deve ter atributo GOVERNANCE_PATHS"
        )

    def test_governance_paths_is_tuple_or_list(self):
        HBHookValidator = _load_hook_class()
        assert isinstance(HBHookValidator.GOVERNANCE_PATHS, (tuple, list, set)), (
            "GOVERNANCE_PATHS deve ser uma coleção iterável"
        )

    @pytest.mark.parametrize("expected_path", EXPECTED_GOVERNANCE_PATHS)
    def test_governance_path_present(self, expected_path):
        HBHookValidator = _load_hook_class()
        paths = list(HBHookValidator.GOVERNANCE_PATHS)
        assert expected_path in paths, (
            f"GOVERNANCE_PATHS não contém '{expected_path}' — "
            "mudanças nesse path não serão rastreadas pelo hook"
        )

    def test_contract_paths_constant_defined(self):
        """CONTRACT_PATHS deve estar definido como constante da classe."""
        HBHookValidator = _load_hook_class()
        assert hasattr(HBHookValidator, "CONTRACT_PATHS"), (
            "HBHookValidator deve ter atributo CONTRACT_PATHS"
        )


class TestPreCommitGovernanceMethods:
    """Hook v4: métodos de detecção e verificação de governança."""

    def test_hook_initializes_task_catalog(self):
        HBHookValidator = _load_hook_class()
        validator = HBHookValidator()
        assert hasattr(validator, "task_catalog"), (
            "HBHookValidator deve inicializar task_catalog para validar artefatos derivados"
        )
        assert isinstance(validator.task_catalog, dict), "task_catalog deve ser um dict"

    def test_get_staged_governance_files_method_exists(self):
        HBHookValidator = _load_hook_class()
        assert hasattr(HBHookValidator, "get_staged_governance_files"), (
            "HBHookValidator deve ter método get_staged_governance_files()"
        )

    def test_check_governance_integrity_method_exists(self):
        HBHookValidator = _load_hook_class()
        assert hasattr(HBHookValidator, "check_governance_integrity"), (
            "HBHookValidator deve ter método check_governance_integrity()"
        )

    def test_governance_integrity_calls_survival_suite(self):
        """check_governance_integrity deve mencionar 'survival-suite' na sua implementação."""
        content = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
        # Verificar que o método existe e menciona survival-suite
        assert "survival-suite" in content, (
            "pre-commit hook não menciona 'survival-suite' — "
            "check_governance_integrity deve chamar scripts/hb survival-suite"
        )

    def test_governance_integrity_calls_parity_test(self):
        """check_governance_integrity deve chamar teste de paridade schema/template/skills."""
        content = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
        assert "test_schema_template_parity_phase4" in content, (
            "pre-commit hook não menciona 'test_schema_template_parity_phase4' — "
            "check_governance_integrity deve rodar testes de paridade"
        )

    def test_governance_integrity_calls_session_crossval(self):
        """check_governance_integrity deve chamar validação cruzada SESSION_HANDOFF ↔ session_start."""
        content = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
        assert "test_session_state_phase3" in content, (
            "pre-commit hook não menciona 'test_session_state_phase3' — "
            "check_governance_integrity deve rodar validação cruzada de sessão"
        )

    def test_run_method_calls_governance_integrity(self):
        """run() deve chamar check_governance_integrity após Fase 5 (SESSION_HANDOFF)."""
        content = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
        assert "check_governance_integrity" in content, (
            "run() deve chamar check_governance_integrity() para mudanças de governança"
        )

    def test_get_staged_governance_files_filters_correctly(self):
        """get_staged_governance_files deve filtrar por GOVERNANCE_PATHS."""
        content = PRE_COMMIT_HOOK.read_text(encoding="utf-8")
        assert "get_staged_governance_files" in content, (
            "pre-commit hook deve ter método get_staged_governance_files"
        )
        assert "GOVERNANCE_PATHS" in content, (
            "get_staged_governance_files deve usar GOVERNANCE_PATHS para filtrar"
        )


# ---------------------------------------------------------------------------
# Testes do scripts/hb survival-suite
# ---------------------------------------------------------------------------

class TestSurvivalSuitePhase5:
    """survival-suite em scripts/hb deve incluir testes das FASEs 3 e 4."""

    def test_hb_exists(self):
        assert HB_SCRIPT.exists()

    @pytest.mark.parametrize("test_module", EXPECTED_SURVIVAL_TESTS)
    def test_survival_suite_includes_test(self, test_module):
        content = HB_SCRIPT.read_text(encoding="utf-8")
        # Encontrar a função cmd_survival_suite e verificar se menciona o módulo
        assert test_module in content, (
            f"scripts/hb survival-suite não inclui '{test_module}' — "
            "testes das FASEs 3 e 4 devem ser obrigatórios na survival-suite"
        )

    def test_survival_suite_description_mentions_bridge_docs(self):
        """A docstring de cmd_survival_suite deve mencionar bridge docs e prompts."""
        content = HB_SCRIPT.read_text(encoding="utf-8")
        assert "bridge" in content.lower() or "bridge-docs" in content.lower(), (
            "Docstring de cmd_survival_suite deve mencionar bridge docs no escopo de mudanças"
        )


# ---------------------------------------------------------------------------
# Testes do workflow .github/workflows/contract-gates.yml
# ---------------------------------------------------------------------------

class TestContractGatesWorkflow:
    """contract-gates.yml deve ter path filters, survival-suite e jobs de paridade."""

    def test_workflow_exists(self):
        assert WORKFLOW_PATH.exists(), f"Workflow não encontrado: {WORKFLOW_PATH}"

    def test_workflow_has_path_filter_action(self):
        """Workflow deve usar dorny/paths-filter para detectar mudanças de governança."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert "dorny/paths-filter" in content, (
            "contract-gates.yml não usa 'dorny/paths-filter' — "
            "path filters são necessários para evitar custo extra em PRs sem mudança de governança"
        )

    def test_workflow_has_governance_enforcement_job(self):
        """Workflow deve ter job governance-enforcement."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert "governance-enforcement" in content, (
            "contract-gates.yml não tem job 'governance-enforcement' — "
            "esse job deve rodar survival-suite em mudanças de governança"
        )

    def test_workflow_governance_enforcement_calls_survival_suite(self):
        """Job governance-enforcement deve chamar 'scripts/hb survival-suite'."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert "survival-suite" in content, (
            "contract-gates.yml não menciona 'survival-suite' em nenhum job"
        )

    def test_workflow_has_registry_executor_parity_job(self):
        """Workflow deve ter job de paridade registry × executor."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert "registry-executor-parity" in content or "test_gate_registry_parity" in content, (
            "contract-gates.yml não tem job de paridade registry × executor"
        )

    def test_workflow_has_schema_template_parity_job(self):
        """Workflow deve ter job de paridade schema × template × skills."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert (
            "schema-template-skills-parity" in content
            or "test_schema_template_parity_phase4" in content
        ), (
            "contract-gates.yml não tem job de paridade schema × template × skills"
        )

    def test_workflow_has_session_crossval_job(self):
        """Workflow deve ter job de validação cruzada SESSION_HANDOFF ↔ session_start."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert (
            "session-handoff-crossval" in content
            or "test_session_state_phase3" in content
        ), (
            "contract-gates.yml não tem job de validação cruzada SESSION_HANDOFF ↔ session_start"
        )

    def test_workflow_governance_jobs_conditioned_on_filter(self):
        """Jobs de governança devem ser condicionais (if:) baseados em path filter."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        # deve existir condição baseada no output do detect-governance-change
        assert "governance_changed" in content, (
            "Jobs de governança não são condicionais ao path filter — "
            "use 'if: needs.detect-governance-change.outputs.governance_changed == true'"
        )

    def test_workflow_governance_enforcement_has_if_condition(self):
        """Job governance-enforcement deve depender do detect-governance-change."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert "detect-governance-change" in content, (
            "contract-gates.yml não tem job 'detect-governance-change' para detectar mudanças"
        )

    def test_workflow_governance_paths_filter_covers_all_critical_paths(self):
        """Path filter no workflow deve cobrir todos os GOVERNANCE_PATHS."""
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        critical_paths_in_filter = [
            ".contract_driven/**",
            "docs/_canon/**",
            ".github/copilot-instructions.md",
            ".github/skills/**",
            "scripts/contracts/validate/**",
            "scripts/hb",
            "contracts/schemas/shared/**",
        ]
        for path in critical_paths_in_filter:
            assert path in content, (
                f"Workflow path filter não cobre '{path}' — "
                "mudanças nesse path não ativarão os jobs de enforcement"
            )
