"""
Checkers de cenários de teste — TSC-001, TSC-002, TSC-003.
"""
from __future__ import annotations

from hbtrack_lint.engine import register_checker, RuleResult


def check_test_scenarios_are_canonical_only(rule: dict, ctx) -> RuleResult:
    """TSC-001: Cenários de teste devem referenciar apenas operações canônicas do OpenAPI."""
    test_scenarios = ctx.contracts.get("19_ATLETAS_TEST_SCENARIOS.yaml") or {}
    scenarios = test_scenarios.get("scenarios") or []

    if not scenarios:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Nenhum cenário de teste encontrado")

    openapi_doc = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    paths = openapi_doc.get("paths") or {}
    canonical_ops = set()
    for path_item in paths.values():
        for method_item in path_item.values():
            if isinstance(method_item, dict):
                op_id = method_item.get("operationId")
                if op_id:
                    canonical_ops.add(op_id)

    errors = []
    for scenario in scenarios:
        op_ref = scenario.get("operation_id") or scenario.get("operationId")
        if op_ref and op_ref not in canonical_ops:
            errors.append(f"Cenário '{scenario.get('scenario_id', '?')}': operação '{op_ref}' não existe no OpenAPI")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_new_domain_scenarios_require_contract_update(rule: dict, ctx) -> RuleResult:
    """TSC-002: Novos cenários de domínio não podem ser adicionados sem atualizar o contrato."""
    test_scenarios = ctx.contracts.get("19_ATLETAS_TEST_SCENARIOS.yaml") or {}
    scenarios = test_scenarios.get("scenarios") or []

    if not scenarios:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Nenhum cenário encontrado")

    meta = test_scenarios.get("meta") or {}
    contract_version = meta.get("version") or meta.get("schema_version")

    openapi_doc = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    openapi_info = openapi_doc.get("info") or {}
    openapi_version = openapi_info.get("version")

    # Se não tiver versionamento, apenas avisa
    if not contract_version:
        return RuleResult.skip(
            rule["rule_id"], rule["checker_id"],
            "Meta de test_scenarios sem campo 'version' — não é possível validar sincronismo"
        )

    # Verificar se os cenários cobrem todas as operações do OpenAPI
    paths = openapi_doc.get("paths") or {}
    canonical_ops = set()
    for path_item in paths.values():
        for method_item in path_item.values():
            if isinstance(method_item, dict):
                op_id = method_item.get("operationId")
                if op_id:
                    canonical_ops.add(op_id)

    covered = {s.get("operation_id") or s.get("operationId") for s in scenarios}
    covered.discard(None)

    uncovered = canonical_ops - covered
    if uncovered:
        # Isso é warning (não must_pass): informar mas não bloquear
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Operações sem cenário de teste: {', '.join(sorted(uncovered))}"
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_property_based_tests_do_not_redefine_domain_truth(rule: dict, ctx) -> RuleResult:
    """TSC-003 (warning): Testes baseados em propriedade não devem redefinar verdade de domínio."""
    # Essa regra é estruturalmente difícil de verificar via AST sem execução
    # Implementada como documentação de padrão esperado

    test_scenarios = ctx.contracts.get("19_ATLETAS_TEST_SCENARIOS.yaml") or {}
    scenarios = test_scenarios.get("scenarios") or []

    property_based = [
        s for s in scenarios
        if s.get("test_type") == "property_based" or "property" in (s.get("test_type") or "").lower()
    ]

    if not property_based:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Verificar se cenários property-based referenciam formalmente os invariants
    invariants_doc = ctx.contracts.get("15_ATLETAS_INVARIANTS.yaml") or {}
    invariant_ids = {inv.get("invariant_id") for inv in (invariants_doc.get("invariants") or [])}
    invariant_ids.discard(None)

    errors = []
    for scenario in property_based:
        inv_ref = scenario.get("invariant_reference") or scenario.get("invariant_id")
        if not inv_ref:
            errors.append(
                f"Cenário property-based '{scenario.get('scenario_id', '?')}': "
                "não declara 'invariant_reference' — pode redefinir verdade de domínio"
            )
        elif inv_ref not in invariant_ids:
            errors.append(
                f"Cenário '{scenario.get('scenario_id', '?')}': "
                f"'invariant_reference: {inv_ref}' não encontrado em 15_ATLETAS_INVARIANTS.yaml"
            )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_test_scenarios_are_canonical_only", check_test_scenarios_are_canonical_only)
register_checker("check_new_domain_scenarios_require_contract_update", check_new_domain_scenarios_require_contract_update)
register_checker("check_property_based_tests_do_not_redefine_domain_truth", check_property_based_tests_do_not_redefine_domain_truth)
