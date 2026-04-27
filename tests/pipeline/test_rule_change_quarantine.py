"""Testes adversariais para RULE_CHANGE_QUARANTINE_GATE.

Conteção 2 do HBCONTROL.md — impede que arquivos de enforcement sejam
misturados com arquivos de produto no mesmo commit/PR.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import pathlib
import subprocess
import sys
import textwrap
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "contracts" / "validate" / "validate_contracts.py"


def _load_validate_module():
    module_name = "validate_contracts_rcq"
    loader = importlib.machinery.SourceFileLoader(module_name, str(VALIDATE_SCRIPT))
    spec = importlib.util.spec_from_loader(module_name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


vc = _load_validate_module()

_classify = vc._classify_changed_file
_g_rule = vc._g_rule_change_quarantine
_get_changeset = vc._get_pr_changeset


# ── Testes de classificação de arquivos ──────────────────────────────────────

class TestClassifyChangedFile:
    def test_hb_script_is_enforcement(self):
        assert _classify("scripts/hb") == "enforcement"

    def test_validate_contracts_is_enforcement(self):
        assert _classify("scripts/contracts/validate/validate_contracts.py") == "enforcement"

    def test_audit_script_is_enforcement(self):
        assert _classify("scripts/audit/check_architecture_docs.py") == "enforcement"

    def test_gates_registry_is_enforcement(self):
        assert _classify("docs/_canon/gates/GATES_REGISTRY.yaml") == "enforcement"

    def test_merge_readiness_is_enforcement(self):
        assert _classify("merge-readiness.json") == "enforcement"

    def test_domain_axioms_is_enforcement(self):
        assert _classify(".contract_driven/DOMAIN_AXIOMS.json") == "enforcement"

    def test_task_catalog_is_enforcement(self):
        assert _classify(".contract_driven/TASK_CATALOG.yaml") == "enforcement"

    def test_src_is_product(self):
        assert _classify("src/modules/training/api.py") == "product"

    def test_frontend_is_product(self):
        assert _classify("frontend/src/components/Roster.tsx") == "product"

    def test_migrations_is_product(self):
        assert _classify("migrations/0042_training_session.py") == "product"

    def test_openapi_contracts_is_product(self):
        assert _classify("contracts/openapi/paths/training.yaml") == "product"

    def test_asyncapi_contracts_is_product(self):
        assert _classify("contracts/asyncapi/events/training.yaml") == "product"

    def test_json_schemas_is_product(self):
        assert _classify("contracts/schemas/training/session.schema.json") == "product"

    def test_session_handoff_is_other(self):
        assert _classify("SESSION_HANDOFF.md") == "other"

    def test_readme_is_other(self):
        assert _classify("README.md") == "other"

    def test_tests_is_other(self):
        assert _classify("tests/pipeline/test_rule_change_quarantine.py") == "other"

    def test_docs_canon_readme_is_other(self):
        # docs/_canon/ que não seja gates/ é "other"
        assert _classify("docs/_canon/CI_CONTRACT_GATES.md") == "other"

    def test_gates_subdir_is_enforcement(self):
        assert _classify("docs/_canon/gates/README.md") == "enforcement"


# ── Testes do gate com git mockado ───────────────────────────────────────────

class TestRuleChangeQuarantineGatePass:
    """Gate deve retornar PASS para changesets homogêneos."""

    def _run_with_files(self, files: list[str]) -> dict:
        with mock.patch.object(vc, "_get_pr_changeset", return_value=(files, "pr_diff")):
            return vc._g_rule_change_quarantine(REPO_ROOT)

    def test_enforcement_only_passes(self):
        result = self._run_with_files([
            "scripts/contracts/validate/validate_contracts.py",
            "docs/_canon/gates/GATES_REGISTRY.yaml",
            "tests/pipeline/test_rule_change_quarantine.py",
        ])
        assert result["status"] == "PASS", result

    def test_product_only_passes(self):
        result = self._run_with_files([
            "src/modules/training/api.py",
            "contracts/openapi/paths/training.yaml",
            "migrations/0042_add_session_field.py",
        ])
        assert result["status"] == "PASS", result

    def test_neutral_only_passes(self):
        result = self._run_with_files([
            "SESSION_HANDOFF.md",
            "README.md",
            "ROADMAP.md",
        ])
        assert result["status"] == "PASS", result

    def test_empty_changeset_passes(self):
        result = self._run_with_files([])
        assert result["status"] == "PASS", result

    def test_enforcement_plus_neutral_passes(self):
        """Enforcement + SESSION_HANDOFF.md deve ser PASS (sem produto)."""
        result = self._run_with_files([
            "scripts/hb",
            "docs/_canon/gates/GATES_REGISTRY.yaml",
            "SESSION_HANDOFF.md",
            "tests/pipeline/test_rule_change_quarantine.py",
        ])
        assert result["status"] == "PASS", result


class TestRuleChangeQuarantineGateFail:
    """Gate deve retornar FAIL para changesets mistos (enforcement + produto)."""

    def _run_with_files(self, files: list[str]) -> dict:
        with mock.patch.object(vc, "_get_pr_changeset", return_value=(files, "pr_diff")):
            return vc._g_rule_change_quarantine(REPO_ROOT)

    def test_enforcement_plus_src_fails(self):
        result = self._run_with_files([
            "scripts/contracts/validate/validate_contracts.py",
            "src/modules/training/api.py",
        ])
        assert result["status"] == "FAIL", result
        assert result["blocking"] is True
        assert result["blocking_code"] == "BLOCKED_RULE_CHANGE_QUARANTINE"

    def test_hb_script_plus_openapi_fails(self):
        result = self._run_with_files([
            "scripts/hb",
            "contracts/openapi/paths/training.yaml",
        ])
        assert result["status"] == "FAIL", result
        assert result["blocking_code"] == "BLOCKED_RULE_CHANGE_QUARANTINE"

    def test_gates_registry_plus_migrations_fails(self):
        result = self._run_with_files([
            "docs/_canon/gates/GATES_REGISTRY.yaml",
            "migrations/0042_add_session_field.py",
        ])
        assert result["status"] == "FAIL", result

    def test_merge_readiness_plus_frontend_fails(self):
        result = self._run_with_files([
            "merge-readiness.json",
            "frontend/src/components/Dashboard.tsx",
        ])
        assert result["status"] == "FAIL", result

    def test_violation_details_contain_both_lists(self):
        """Violation details devem listar arquivos de enforcement e produto separadamente."""
        result = self._run_with_files([
            "scripts/hb",
            "src/modules/training/api.py",
            "SESSION_HANDOFF.md",  # este é "other", não deve aparecer em nenhuma lista
        ])
        assert result["status"] == "FAIL"
        violation = result["violations"][0]
        details = violation["details"]
        assert "scripts/hb" in details["enforcement_files"]
        assert "src/modules/training/api.py" in details["product_files"]
        assert "SESSION_HANDOFF.md" not in details["enforcement_files"]
        assert "SESSION_HANDOFF.md" not in details["product_files"]

    def test_task_catalog_plus_json_schema_fails(self):
        result = self._run_with_files([
            ".contract_driven/TASK_CATALOG.yaml",
            "contracts/schemas/training/session.schema.json",
        ])
        assert result["status"] == "FAIL", result


class TestRuleChangeQuarantineGateSkip:
    """Gate deve SKIP quando changeset não pode ser determinado."""

    def test_skip_when_git_unavailable(self):
        with mock.patch.object(
            vc, "_get_pr_changeset", return_value=(None, "git_unavailable_or_no_changeset")
        ):
            result = vc._g_rule_change_quarantine(REPO_ROOT)
        assert result["status"] == "SKIP_NOT_APPLICABLE", result


class TestRuleChangeQuarantineGateLive:
    """Testes contra o repositório real (PR atual)."""

    def test_current_pr_is_enforcement_only(self):
        """O PR atual (feat/rule-change-quarantine) deve ser enforcement-only ou neutral."""
        result = vc._g_rule_change_quarantine(REPO_ROOT)
        # Aceitar PASS ou SKIP (em caso de git indisponível ou sem origin/main)
        assert result["status"] in ("PASS", "SKIP_NOT_APPLICABLE"), (
            f"Gate falhou no PR atual — changeset misto detectado: {result}"
        )
