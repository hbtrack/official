"""
Checkers de invariants — TIME-001.
(Os demais invariants X-007, X-008 estão em cross.py)
"""
from __future__ import annotations

from hbtrack_lint.engine import register_checker, RuleResult


def check_temporal_invariants_require_reference_inputs(rule: dict, ctx) -> RuleResult:
    """TIME-001: Todo invariant temporal deve declarar required_inputs e data/ano de referência canônico."""
    invariants_doc = ctx.contracts.get("15_ATLETAS_INVARIANTS.yaml") or {}
    test_scenarios = ctx.contracts.get("19_ATLETAS_TEST_SCENARIOS.yaml") or {}

    errors = []
    for inv in (invariants_doc.get("invariants") or []):
        # Verificar se o invariant depende de contexto temporal
        predicate = inv.get("formal_predicate") or ""
        terms = inv.get("domain_terms") or []
        uses_time = (
            any(kw in predicate.lower() for kw in ["year", "date", "ano", "data", "birth", "nasc"])
            or any(t.get("term", "").lower() in ["year", "birth_year", "age"] for t in terms if isinstance(t, dict))
        )
        if not uses_time:
            continue

        inv_id = inv.get("invariant_id", "?")
        eb = inv.get("enforcement_bindings") or {}

        # Verificar required_inputs declarados
        required_inputs = eb.get("required_inputs") or []
        if not required_inputs:
            errors.append(f"{inv_id}: invariant temporal sem required_inputs declarados")
            continue

        # Verificar se fonte de ano/data de referência está declarada
        has_year_source = any(
            "year" in inp.lower() or "date" in inp.lower() or "config" in inp.lower()
            for inp in required_inputs
        )
        if not has_year_source:
            errors.append(f"{inv_id}: required_inputs sem fonte de ano/data canônica")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_temporal_invariants_require_reference_inputs", check_temporal_invariants_require_reference_inputs)
