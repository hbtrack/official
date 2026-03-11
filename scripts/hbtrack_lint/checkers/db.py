"""
Checkers de banco de dados — CC-001, CC-002, CC-003.

Regras de concorrência e UI duplicate submit que complementam os X-* em cross.py.
"""
from __future__ import annotations

from hbtrack_lint.engine import register_checker, RuleResult


def check_aggregates_with_concurrent_update_risk_declare_strategy(rule: dict, ctx) -> RuleResult:
    """CC-001: Todo agregado com risco de escrita concorrente deve declarar estratégia de controle."""
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}
    dbc = db.get("database_contract") or {}
    tables = dbc.get("tables") or []

    errors = []
    for tbl in tables:
        lp = tbl.get("locking_policy") or {}
        strategy = lp.get("strategy")
        if not strategy or strategy.upper() == "NONE":
            # Verificar se é tabela de leitura/projeção (sem escrita concorrente direta)
            name = tbl.get("table_name", "?")
            # Tabelas com operações de escrita devem ter estratégia declarada
            if tbl.get("write_operation_patterns"):
                errors.append(f"Tabela '{name}': locking_policy.strategy não declarado para tabela com write_patterns")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_optimistic_locking_contract_is_complete(rule: dict, ctx) -> RuleResult:
    """CC-002: Optimistic locking requer version_column + conflict_error_code + retry_policy."""
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}
    dbc = db.get("database_contract") or {}
    tables = dbc.get("tables") or []

    errors = []
    for tbl in tables:
        lp = tbl.get("locking_policy") or {}
        strategy = (lp.get("strategy") or "").lower()
        if "optimistic" in strategy:
            name = tbl.get("table_name", "?")
            if not lp.get("version_column"):
                errors.append(f"Tabela '{name}': optimistic locking sem version_column")
            if not lp.get("conflict_error_code"):
                errors.append(f"Tabela '{name}': optimistic locking sem conflict_error_code")
            if not lp.get("retry_policy"):
                errors.append(f"Tabela '{name}': optimistic locking sem retry_policy")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_ui_duplicate_submit_protection_exists(rule: dict, ctx) -> RuleResult:
    """CC-003: Fluxos de submit interativo para escritas concorrentes devem definir proteção contra double_click."""
    ui = ctx.contracts.get("14_ATLETAS_UI_CONTRACT.yaml") or {}

    errors = []
    for screen in (ui.get("screens") or []):
        states = screen.get("states") or []
        state_items = states if isinstance(states, list) else [dict([(k, v)]) for k, v in states.items()]
        for state_item in state_items:
            if not isinstance(state_item, dict):
                continue
            state_name = state_item.get("state") or state_item.get("state_name", "?")
            state_def = state_item
            if "submit" in str(state_name).lower() or state_def.get("is_submitting"):
                ctrl = state_def.get("submit_control") or {}
                if not ctrl.get("double_click_blocked") and not ctrl.get("submit_button_policy"):
                    errors.append(
                        f"Screen '{screen.get('screen_id', '?')}' estado '{state_name}': "
                        f"sem double_click_blocked ou submit_button_policy"
                    )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_aggregates_with_concurrent_update_risk_declare_strategy", check_aggregates_with_concurrent_update_risk_declare_strategy)
register_checker("check_optimistic_locking_contract_is_complete", check_optimistic_locking_contract_is_complete)
register_checker("check_ui_duplicate_submit_protection_exists", check_ui_duplicate_submit_protection_exists)
