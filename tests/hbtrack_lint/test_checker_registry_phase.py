"""
C8 — testes de phase filter e clear_registry em checker_registry.py
5 casos obrigatórios conforme GAP-C8 do plano canônico.
"""
from __future__ import annotations

import pytest

from hbtrack_lint import engine
from hbtrack_lint.engine import RuleResult, register_checker, clear_registry, STATUS_SKIP
import hbtrack_lint.checker_registry as cr


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ctx(rules: list[dict]):
    """Contexto mínimo: só precisa de contracts com a chave cross-linter."""
    cross = {}
    # Colocar todas as regras em document_shape_rules para simplificar
    cross["document_shape_rules"] = rules
    class _Ctx:
        contracts = {"00_ATLETAS_CROSS_LINTER_RULES.json": cross}
    return _Ctx()


def _rule(rule_id: str, checker_id: str, phase: str) -> dict:
    return {"rule_id": rule_id, "checker_id": checker_id, "execution_phase": phase}


def _setup_isolated(checkers: dict[str, callable]):
    """
    Limpa o registry global e registra apenas os checkers fornecidos.
    Marca _checkers_registered=True para evitar que _ensure_registered
    chame register_all_checkers() (que sobrescreveria nosso estado limpo).
    """
    clear_registry()
    cr._checkers_registered = True
    for cid, fn in checkers.items():
        register_checker(cid, fn)


def _dummy_pass(rule, ctx):
    return RuleResult(rule["rule_id"], rule["checker_id"], "PASS", "ok")


def _dummy_fail(rule, ctx):
    return RuleResult(rule["rule_id"], rule["checker_id"], "FAIL_ACTIONABLE", "falhou")


# ---------------------------------------------------------------------------
# Caso 1: phase=PRE_PLAN → somente resultados PRE_PLAN
# ---------------------------------------------------------------------------

def test_phase_pre_plan_only():
    rules = [
        _rule("R-PRE-001", "chk_pre", "PRE_PLAN"),
        _rule("R-POST-001", "chk_post", "POST_EXECUTION"),
        _rule("R-PLAN-001", "chk_plan", "POST_PLAN"),
    ]
    _setup_isolated({"chk_pre": _dummy_pass, "chk_post": _dummy_pass, "chk_plan": _dummy_pass})

    results = cr.run_allowed_rules(_make_ctx(rules), phase="PRE_PLAN")

    rule_ids = [r.rule_id for r in results]
    assert "R-PRE-001" in rule_ids
    assert "R-POST-001" not in rule_ids
    assert "R-PLAN-001" not in rule_ids
    assert len(results) == 1


# ---------------------------------------------------------------------------
# Caso 2: phase=POST_EXECUTION → somente resultados POST_EXECUTION
# ---------------------------------------------------------------------------

def test_phase_post_execution_only():
    rules = [
        _rule("R-PRE-002", "chk_pre2", "PRE_PLAN"),
        _rule("R-POST-002", "chk_post2", "POST_EXECUTION"),
    ]
    _setup_isolated({"chk_pre2": _dummy_pass, "chk_post2": _dummy_fail})

    results = cr.run_allowed_rules(_make_ctx(rules), phase="POST_EXECUTION")

    rule_ids = [r.rule_id for r in results]
    assert "R-POST-002" in rule_ids
    assert "R-PRE-002" not in rule_ids
    assert len(results) == 1
    assert results[0].status == "FAIL_ACTIONABLE"


# ---------------------------------------------------------------------------
# Caso 3: phase=None → todas as regras (comportamento legado)
# ---------------------------------------------------------------------------

def test_phase_none_returns_all():
    rules = [
        _rule("R-PRE-003", "chk_a", "PRE_PLAN"),
        _rule("R-POST-003", "chk_b", "POST_EXECUTION"),
        _rule("R-PLAN-003", "chk_c", "POST_PLAN"),
    ]
    _setup_isolated({"chk_a": _dummy_pass, "chk_b": _dummy_pass, "chk_c": _dummy_pass})

    results = cr.run_allowed_rules(_make_ctx(rules), phase=None)

    rule_ids = [r.rule_id for r in results]
    assert "R-PRE-003" in rule_ids
    assert "R-POST-003" in rule_ids
    assert "R-PLAN-003" in rule_ids
    assert len(results) == 3


# ---------------------------------------------------------------------------
# Caso 4: checker_id sem implementação → status SKIP, nunca FAIL
# ---------------------------------------------------------------------------

def test_missing_checker_produces_skip():
    rules = [
        _rule("R-MISSING-001", "chk_nao_existe", "PRE_PLAN"),
    ]
    # Registra nenhum checker — chk_nao_existe ausente
    _setup_isolated({})

    results = cr.run_allowed_rules(_make_ctx(rules), phase=None)

    assert len(results) == 1
    r = results[0]
    assert r.rule_id == "R-MISSING-001"
    assert r.status == STATUS_SKIP
    assert "chk_nao_existe" in r.message


# ---------------------------------------------------------------------------
# Caso 5: clear_registry() + re-register → estado limpo
# ---------------------------------------------------------------------------

def test_clear_and_re_register():
    # Registra um checker
    register_checker("chk_tmp", _dummy_pass)
    assert "chk_tmp" in engine.get_checkers()

    # Clear
    clear_registry()
    assert engine.get_checkers() == {}

    # Re-register com reset do flag para exercitar o caminho real
    cr._checkers_registered = False
    # Re-limpa para evitar side-effects de outros testes
    clear_registry()
    cr._checkers_registered = True  # isola: não chama register_all_checkers()

    register_checker("chk_fresh", _dummy_pass)
    checkers = engine.get_checkers()
    assert "chk_fresh" in checkers
    assert "chk_tmp" not in checkers
