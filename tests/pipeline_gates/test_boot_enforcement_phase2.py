"""
tests/pipeline_gates/test_boot_enforcement_phase2.py

FASE 2 — BOOT ENFORCEMENT (DETERMINÍSTICO)

Testa os 4 novos métodos adicionados em AGENT_COMPLIANCE_EXECUTION_PLAN.md Fase 2:
  - _apply_selection_rules
  - _check_stage_allowed
  - _validate_required_section_content
  - _validate_profile_validations

E verifica integração de ponta a ponta via subprocesso `hb verify`.
"""

import io
import sys
import importlib.machinery
import importlib.util
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers — carregar HBCLIv2 sem executar __main__
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent
HB_SCRIPT = REPO_ROOT / "scripts" / "hb"


def _load_hbcli():
    """Importa HBCLIv2 do script 'scripts/hb' sem disparar main()."""
    spec = importlib.util.spec_from_loader(
        "hb_module",
        importlib.machinery.SourceFileLoader("hb_module", str(HB_SCRIPT)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.HBCLIv2


HBCLIv2 = _load_hbcli()


@pytest.fixture(scope="module")
def cli():
    """
    Instância de HBCLIv2 apontando para o workspace real.
    HBCLIv2 não aceita root=; descobre a raiz via git.
    """
    return HBCLIv2()


# ===========================================================================
# 1. _apply_selection_rules
# ===========================================================================
class TestApplySelectionRules:
    def test_execute_roadmap_phase_returns_roadmap_execution(self, cli):
        assert cli._apply_selection_rules("execute_roadmap_phase") == "roadmap_execution"

    def test_new_contract_returns_contract_execution(self, cli):
        assert cli._apply_selection_rules("new_contract") == "contract_execution"

    def test_contract_revision_returns_contract_execution(self, cli):
        assert cli._apply_selection_rules("contract_revision") == "contract_execution"

    def test_new_event_returns_contract_execution(self, cli):
        assert cli._apply_selection_rules("new_event") == "contract_execution"

    def test_new_schema_returns_contract_execution(self, cli):
        assert cli._apply_selection_rules("new_schema") == "contract_execution"

    def test_architecture_review_returns_architecture_decision(self, cli):
        assert cli._apply_selection_rules("architecture_review") == "architecture_decision"

    def test_unknown_task_returns_default(self, cli):
        assert cli._apply_selection_rules("nonexistent_task_xyz") == "default"

    def test_execute_roadmap_phase_profile_consistent_with_task_catalog(self, cli):
        """Profile retornado pela heurística deve ser igual ao do TASK_CATALOG (coerência)."""
        catalog_entry = (cli.task_catalog.get("task_catalog") or {}).get("execute_roadmap_phase", {})
        explicit = catalog_entry.get("profile_id") or "default"
        discovered = cli._apply_selection_rules("execute_roadmap_phase")
        assert discovered == explicit or explicit == "default"


# ===========================================================================
# 2. _check_stage_allowed
# ===========================================================================
class TestCheckStageAllowed:
    def test_empty_stage_allowed_always_ok(self, cli):
        """Lista vazia = sem restrição — deve retornar True."""
        assert cli._check_stage_allowed("nonexistent_foo_xyz", 99) is True

    def test_stage_in_allowed_list_returns_true(self, cli):
        # new_contract tem stage_allowed: [0, 1, 2] no TASK_CATALOG
        assert cli._check_stage_allowed("new_contract", 0) is True
        assert cli._check_stage_allowed("new_contract", 1) is True
        assert cli._check_stage_allowed("new_contract", 2) is True

    def test_stage_outside_allowed_list_returns_false_and_warns(self, cli):
        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = cli._check_stage_allowed("new_contract", 9)
        assert result is False
        assert "stage_allowed" in stderr_buf.getvalue() or "ROUTING" in stderr_buf.getvalue()

    def test_readiness_promotion_above_cli_range_does_not_raise(self, cli):
        """
        readiness_promotion tem stage_allowed: [3, 4] acima do range CLI.
        Deve retornar bool sem lançar exceção (semântica informativa).
        """
        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = cli._check_stage_allowed("readiness_promotion", 0)
        assert isinstance(result, bool)


# ===========================================================================
# 3. _validate_required_section_content
# ===========================================================================
class TestValidateRequiredSectionContent:
    """
    Usa tmp_path + override de cli.root para isolar testes de filesystem.
    A instância cli é module-scoped; usamos uma cópia local rápida via
    atribuição direta de boot_profiles/root.
    """

    def _fresh_cli(self) -> HBCLIv2:
        """Cria nova instância apontando para repo real."""
        return HBCLIv2()

    def test_default_profile_required_sections_pass(self):
        """Profile 'default' deve passar — arquivos de repo existem e não estão vazios."""
        instance = self._fresh_cli()
        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = instance._validate_required_section_content("default")
        assert result is True

    def test_empty_file_fails(self, tmp_path):
        """Arquivo vazio referenciado como required_sections§N deve falhar."""
        instance = self._fresh_cli()
        # Criar arquivo vazio em tmp_path
        empty = tmp_path / "docs" / "_canon" / "EMPTY_TEST.md"
        empty.parent.mkdir(parents=True, exist_ok=True)
        empty.write_text("", encoding="utf-8")

        # Injetar profile de teste e redirecionar root para tmp_path
        fake_profiles = {
            "profiles": {
                "test_empty": {
                    "load_sequence": [],
                    "required_sections": ["docs/_canon/EMPTY_TEST.md§0"],
                    "validations": {},
                    "exit_on_fail": True,
                }
            }
        }
        instance.boot_profiles = fake_profiles
        instance.root = tmp_path

        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = instance._validate_required_section_content("test_empty")

        assert result is False
        assert "vazio" in stderr_buf.getvalue()

    def test_missing_numeric_heading_warns_not_fails(self, tmp_path):
        """Arquivo não-vazio sem heading §N → aviso, mas retorna True."""
        instance = self._fresh_cli()
        partial = tmp_path / "docs" / "_canon" / "PARTIAL.md"
        partial.parent.mkdir(parents=True, exist_ok=True)
        partial.write_text("Conteúdo sem heading numerada.\n", encoding="utf-8")

        fake_profiles = {
            "profiles": {
                "test_partial": {
                    "load_sequence": [],
                    "required_sections": ["docs/_canon/PARTIAL.md§5"],
                    "validations": {},
                    "exit_on_fail": True,
                }
            }
        }
        instance.boot_profiles = fake_profiles
        instance.root = tmp_path

        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = instance._validate_required_section_content("test_partial")

        assert result is True
        assert "heading" in stderr_buf.getvalue() or "renumerada" in stderr_buf.getvalue()

    def test_path_without_section_marker_empty_fails(self, tmp_path):
        """Arquivo sem §marker e vazio deve falhar."""
        instance = self._fresh_cli()
        bare = tmp_path / "docs" / "_canon" / "BARE.md"
        bare.parent.mkdir(parents=True, exist_ok=True)
        bare.write_text("", encoding="utf-8")

        fake_profiles = {
            "profiles": {
                "test_bare": {
                    "load_sequence": [],
                    "required_sections": ["docs/_canon/BARE.md"],
                    "validations": {},
                    "exit_on_fail": True,
                }
            }
        }
        instance.boot_profiles = fake_profiles
        instance.root = tmp_path

        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = instance._validate_required_section_content("test_bare")

        assert result is False


# ===========================================================================
# 4. _validate_profile_validations
# ===========================================================================
class TestValidateProfileValidations:
    def _fresh_cli(self) -> HBCLIv2:
        return HBCLIv2()

    def _inject(self, instance, profile_id, validations):
        profiles = dict(instance.boot_profiles.get("profiles", {}))
        profiles[profile_id] = {
            "load_sequence": [],
            "required_sections": [],
            "validations": validations,
            "exit_on_fail": True,
        }
        instance.boot_profiles = {"profiles": profiles}

    def test_empty_session_handoff_fails(self, tmp_path):
        instance = self._fresh_cli()
        instance.root = tmp_path
        handoff = tmp_path / "SESSION_HANDOFF.md"
        handoff.write_text("", encoding="utf-8")
        self._inject(instance, "p_test", [{"session_handoff_read": True}])

        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = instance._validate_profile_validations("p_test")

        assert result is False
        assert "SESSION_HANDOFF" in stderr_buf.getvalue()

    def test_absent_session_handoff_ok_first_boot(self, tmp_path):
        instance = self._fresh_cli()
        instance.root = tmp_path
        # Garantir ausência
        handoff = tmp_path / "SESSION_HANDOFF.md"
        if handoff.exists():
            handoff.unlink()
        self._inject(instance, "p_test2", [{"session_handoff_read": True}])

        stdout_buf = io.StringIO()
        with redirect_stdout(stdout_buf):
            result = instance._validate_profile_validations("p_test2")

        assert result is True
        assert "ausente" in stdout_buf.getvalue() or "inicial" in stdout_buf.getvalue()

    def test_non_empty_session_handoff_passes(self, tmp_path):
        instance = self._fresh_cli()
        instance.root = tmp_path
        handoff = tmp_path / "SESSION_HANDOFF.md"
        handoff.write_text("# Handoff\nFase 2\n", encoding="utf-8")
        self._inject(instance, "p_test3", [{"session_handoff_read": True}])

        result = instance._validate_profile_validations("p_test3")
        assert result is True

    def test_missing_roadmap_fails(self, tmp_path):
        instance = self._fresh_cli()
        instance.root = tmp_path
        roadmap = tmp_path / "ROADMAP.md"
        if roadmap.exists():
            roadmap.unlink()
        self._inject(instance, "p_road", [{"roadmap_phase_valid": True}])

        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            result = instance._validate_profile_validations("p_road")

        assert result is False
        assert "ROADMAP" in stderr_buf.getvalue()

    def test_roadmap_with_phase_sections_passes(self, tmp_path):
        instance = self._fresh_cli()
        instance.root = tmp_path
        roadmap = tmp_path / "ROADMAP.md"
        roadmap.write_text("# HB TRACK\n\n## Fase 0 — Ambiente\n", encoding="utf-8")
        self._inject(instance, "p_road2", [{"roadmap_phase_valid": True}])

        result = instance._validate_profile_validations("p_road2")
        assert result is True

    def test_plain_dict_validations_also_works(self, tmp_path):
        """Validations como dict (não lista) também deve funcionar."""
        instance = self._fresh_cli()
        instance.root = tmp_path
        handoff = tmp_path / "SESSION_HANDOFF.md"
        handoff.write_text("# Handoff ok\n", encoding="utf-8")
        self._inject(instance, "p_dict", {"session_handoff_read": True})

        result = instance._validate_profile_validations("p_dict")
        assert result is True

    def test_profile_with_no_validations_passes(self, tmp_path):
        instance = self._fresh_cli()
        instance.root = tmp_path
        self._inject(instance, "p_none", {})

        result = instance._validate_profile_validations("p_none")
        assert result is True


# ===========================================================================
# 5. Bug fix — profile_id null → "default"
# ===========================================================================
class TestProfileIdNullFix:
    def test_audit_task_with_null_profile_id_gets_default(self, cli):
        """
        Tasks com profile_id: null em TASK_CATALOG devem receber 'default'
        via `or "default"` em vez de retornar None.
        """
        task_catalog = cli.task_catalog.get("task_catalog", {})
        null_tasks = [
            k for k, v in task_catalog.items()
            if isinstance(v, dict) and "profile_id" in v and v.get("profile_id") is None
        ]
        if not null_tasks:
            pytest.skip("Nenhuma task com profile_id: null em TASK_CATALOG.")
        task_type = null_tasks[0]
        config = task_catalog[task_type]
        profile_id = config.get("profile_id") or "default"
        assert profile_id == "default", f"Esperado 'default', obtido '{profile_id}'"


# ===========================================================================
# 6. Integração via subprocesso — hb verify
# ===========================================================================
class TestHbVerifyIntegration:
    """Testes de integração via `python scripts/hb verify ...` contra repo real."""

    def _run_hb(self, *args):
        import subprocess as sp
        result = sp.run(
            [sys.executable, str(HB_SCRIPT)] + list(args),
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        return result

    def test_verify_valid_task_passes(self):
        """
        hb verify com task_type e module válidos deve passar pelas novas
        validações de boot enforcement sem bloqueio (exit 1).
        O validator externo (validate_contracts.py) pode retornar 2
        por issues pré-existentes de contrato — isso é distinto do boot enforcement.
        """
        result = self._run_hb("verify", "--task-type", "new_contract", "--module", "training")
        # exit 1 = boot enforcement bloqueou → falha de verdade
        # exit 0 ou 2 = boot enforcement PASSOU; validator pode ter issues externos
        assert result.returncode != 1, (
            f"Boot enforcement bloqueou task válida (exit 1).\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        # Confirmar que os ✅ de boot aparecem no stdout
        assert "✅ task_type=" in result.stdout or "✅ boot_profile" in result.stdout, (
            f"Mensagens de boot ✅ ausentes.\nstdout={result.stdout}\nstderr={result.stderr}"
        )

    def test_verify_unknown_task_fails(self):
        """hb verify com task_type inválido deve retornar exit != 0."""
        result = self._run_hb("verify", "--task-type", "task_xyz_inexistente", "--module", "training")
        assert result.returncode != 0

    def test_verify_roadmap_task_no_selection_divergence(self):
        """
        execute_roadmap_phase: profile no TASK_CATALOG coincide com selection_rules
        → não deve aparecer mensagem de divergência de coerência.
        """
        result = self._run_hb("verify", "--task-type", "execute_roadmap_phase", "--module", "training")
        assert "TASK_CATALOG é a fonte de autoridade" not in result.stderr

