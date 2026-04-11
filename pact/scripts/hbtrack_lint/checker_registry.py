"""
Registro central de checkers e runner de regras permitidas.

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

from hbtrack_lint.engine import run_rule, get_checkers, RuleResult


_ALL_RULE_SECTIONS = [
    "document_shape_rules",
    "cross_rules",
    "event_rules",
    "projection_rules",
    "side_effect_rules",
    "concurrency_rules",
    "ui_state_rules",
    "time_determinism_rules",
    "test_scenario_rules",
    "stub_anchor_rules",
    "handoff_rules",
    "restriction_prompt_rules",
    "diff_validation_rules",
]

# Cache de inicialização
_checkers_registered = False


def _ensure_registered() -> None:
    global _checkers_registered
    if _checkers_registered:
        return
    from hbtrack_lint.checkers import register_all_checkers
    register_all_checkers()
    _checkers_registered = True


def run_allowed_rules(ctx, phase=None) -> list[RuleResult]:
    """
    Executa todas as regras declaradas no meta-contrato (00_ATLETAS_CROSS_LINTER_RULES.json)
    cujos checker_id estejam registrados.

    phase=None  -> comportamento legado (sem filtro, retrocompativel).
    phase=str   -> apenas regras com execution_phase == phase.
    """
    _ensure_registered()

    cross_rules = ctx.contracts.get("00_ATLETAS_CROSS_LINTER_RULES.json") or {}
    registered = get_checkers()
    results: list[RuleResult] = []

    def _dispatch_rule_list(rules: list) -> None:
        for rule in rules:
            # Filtro de phase (C4 item 3)
            if phase is not None and rule.get("execution_phase") != phase:
                continue

            checker_id = rule.get("checker_id", "")
            rule_id = rule.get("rule_id", checker_id)

            # REGRA EXPLICITA (C4 item 4): checker_id ausente vira SKIP, nunca FAIL
            if checker_id not in registered:
                results.append(
                    RuleResult(rule_id, checker_id or "?", "SKIP",
                               f"No implementation for checker_id={checker_id}")
                )
                continue

            result = run_rule(rule, ctx)
            results.append(result)

    # Seções planas
    for section in _ALL_RULE_SECTIONS:
        _dispatch_rule_list(cross_rules.get(section, []))

    # global_type_system.rules (seção aninhada com TYPE-001..006)
    gts = cross_rules.get("global_type_system", {})
    if isinstance(gts, dict):
        _dispatch_rule_list(gts.get("rules", []))

    return results
