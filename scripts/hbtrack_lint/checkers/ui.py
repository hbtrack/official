"""
Checkers de UI State — UIST-001, UIST-002, UIST-003.
"""
from __future__ import annotations

from hbtrack_lint.engine import register_checker, RuleResult


def check_submit_states_define_control_policy(rule: dict, ctx) -> RuleResult:
    """UIST-001: Todo estado de submissão deve definir política de controle (disabled/loading/double_click_blocked)."""
    ui = ctx.contracts.get("14_ATLETAS_UI_CONTRACT.yaml") or {}
    errors = []
    required_values = rule.get("required_values") or ["disabled", "loading", "double_click_blocked"]

    for screen in (ui.get("screens") or []):
        states = screen.get("states") or []
        # states pode ser lista [{state: 'submitting', ...}] ou dict {state_name: {...}}
        state_items = states if isinstance(states, list) else [dict([(k, v)]) for k, v in states.items()]
        for state_item in state_items:
            if not isinstance(state_item, dict):
                continue
            state_name = state_item.get("state") or state_item.get("state_name", "?")
            state_def = state_item
            if "submit" in str(state_name).lower() or state_def.get("is_submitting"):
                ctrl = state_def.get("submit_control") or {}
                missing = [v for v in required_values if not ctrl.get(v)]
                if missing:
                    errors.append(
                        f"Screen '{screen.get('screen_id', '?')}' estado '{state_name}': "
                        f"submit_control faltando {missing}"
                    )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_success_and_error_states_define_feedback_selector(rule: dict, ctx) -> RuleResult:
    """UIST-002: Todo estado de sucesso/erro deve definir selector de feedback visível."""
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
            if any(kw in str(state_name).lower() for kw in ["success", "error", "sucesso", "erro"]):
                if not state_def.get("feedback_selector") and not state_def.get("selector"):
                    errors.append(
                        f"Screen '{screen.get('screen_id', '?')}' estado '{state_name}': "
                        f"feedback_selector ausente"
                    )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_required_selectors_use_primary_strategy(rule: dict, ctx) -> RuleResult:
    """UIST-003: Selectors requeridos devem usar data-testid como superfície de automação primária."""
    ui = ctx.contracts.get("14_ATLETAS_UI_CONTRACT.yaml") or {}

    # Verificar estratégia configurada
    selector_strategy = (ui.get("selector_strategy") or {})
    primary = selector_strategy.get("primary")

    if primary and primary != "data-testid":
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"selector_strategy.primary='{primary}' mas deve ser 'data-testid'",
        )

    errors = []
    for screen in (ui.get("screens") or []):
        for sel in (screen.get("selectors") or screen.get("test_selectors") or []):
            if not isinstance(sel, dict):
                continue
            if sel.get("required"):
                strategy = sel.get("strategy") or sel.get("selector_type")
                if strategy and strategy != "data-testid":
                    errors.append(
                        f"Screen '{screen.get('screen_id', '?')}' selector '{sel.get('id', '?')}': "
                        f"strategy='{strategy}' mas deve ser 'data-testid'"
                    )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_submit_states_define_control_policy", check_submit_states_define_control_policy)
register_checker("check_success_and_error_states_define_feedback_selector", check_success_and_error_states_define_feedback_selector)
register_checker("check_required_selectors_use_primary_strategy", check_required_selectors_use_primary_strategy)
