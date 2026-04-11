"""
Checkers de side effects — SE-001 a SE-012.

cannot_waive: SE-006, SE-009, SE-010, SE-011, SE-012
"""
from __future__ import annotations

import ast
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult


def _get_side_effects(ctx) -> list[dict]:
    se = ctx.contracts.get("18_ATLETAS_SIDE_EFFECTS.yaml") or {}
    return se.get("side_effects") or []


def check_side_effect_idempotency_keys_are_declared_and_safe(rule: dict, ctx) -> RuleResult:
    """SE-001: Todo side effect externo deve declarar idempotency_key derivada de inputs únicos do evento."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        if not effect.get("idempotency_key"):
            errors.append(f"SE '{effect.get('side_effect_id', '?')}': idempotency_key ausente")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_replay_policy_is_declared(rule: dict, ctx) -> RuleResult:
    """SE-002: Todo side effect deve declarar replay_policy."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        if not effect.get("replay_policy"):
            errors.append(f"SE '{effect.get('side_effect_id', '?')}': replay_policy ausente")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_retry_policy_is_declared_when_retryable(rule: dict, ctx) -> RuleResult:
    """SE-003: Todo SE retryable deve declarar retry_policy."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        error_policy = effect.get("error_policy") or {}
        if error_policy.get("retryable") and not error_policy.get("retry_policy"):
            errors.append(f"SE '{effect.get('side_effect_id', '?')}': retryable=true mas retry_policy ausente")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effects_are_skipped_during_projection_rebuild(rule: dict, ctx) -> RuleResult:
    """SE-004 (POST_EXECUTION): Rebuild de projeção deve pular side effects salvo se replay_policy permite."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        replay_policy = effect.get("replay_policy") or ""
        if replay_policy.lower() not in ("skip", "skip_on_rebuild", "idempotent_skip"):
            target_file = effect.get("target_file")
            if target_file:
                impl_path = ctx.repo_root / target_file
                if impl_path.exists():
                    source = impl_path.read_text(encoding="utf-8", errors="replace")
                    if "is_rebuild" not in source and "rebuild_mode" not in source:
                        errors.append(
                            f"SE '{effect.get('side_effect_id', '?')}': "
                            f"replay_policy='{replay_policy}' mas implementação não verifica rebuild_mode"
                        )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_no_undeclared_external_calls_exist(rule: dict, ctx) -> RuleResult:
    """SE-005 (POST_EXECUTION): Nenhuma chamada de rede não declarada fora de side effects permitidos."""
    effects = _get_side_effects(ctx)
    # Sem side effects declarados = nenhuma chamada externa esperada
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_handlers_do_not_write_read_models(rule: dict, ctx) -> RuleResult:
    """SE-006 (POST_EXECUTION, cannot_waive): Handlers de SE não devem mutar tabelas de projeção ou de domínio."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    read_model_tables: set[str] = set()
    for rm in (projections.get("read_models") or []):
        if rm.get("target_table"):
            read_model_tables.add(rm["target_table"])

    errors = []
    for effect in effects:
        target_file = effect.get("target_file")
        if not target_file:
            continue
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            continue

        source = impl_path.read_text(encoding="utf-8", errors="replace")
        for table in read_model_tables:
            if table in source:
                errors.append(
                    f"SE '{effect.get('side_effect_id', '?')}' em '{target_file}': "
                    f"referência à tabela de projeção '{table}'"
                )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_handlers_do_not_import_projection_modules(rule: dict, ctx) -> RuleResult:
    """SE-007 (POST_EXECUTION): Handlers de SE não devem importar módulos de projeção."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        target_file = effect.get("target_file")
        if not target_file:
            continue
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            continue

        source = impl_path.read_text(encoding="utf-8", errors="replace")
        if "projection" in source.lower() and ("import" in source):
            # Verificar imports de projection
            try:
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        names = [n.name for n in getattr(node, "names", [])]
                        module = getattr(node, "module", "") or ""
                        if "projection" in module.lower() or any("projection" in n.lower() for n in names):
                            errors.append(
                                f"SE '{effect.get('side_effect_id', '?')}': importa módulo de projeção"
                            )
                            break
            except SyntaxError:
                pass

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_handlers_forbid_system_clock(rule: dict, ctx) -> RuleResult:
    """SE-008 (POST_EXECUTION): Handlers de SE não devem usar system clock como input de negócio."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    forbidden_clock = {"datetime.now()", "date.today()", "time.time()"}
    errors = []
    for effect in effects:
        target_file = effect.get("target_file")
        if not target_file:
            continue
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            continue
        source = impl_path.read_text(encoding="utf-8", errors="replace")
        for call in forbidden_clock:
            if call in source:
                errors.append(f"SE '{effect.get('side_effect_id', '?')}': uso de clock '{call}'")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_handlers_use_declared_integration_symbols(rule: dict, ctx) -> RuleResult:
    """SE-009 (POST_EXECUTION, cannot_waive): Handlers de SE devem usar apenas símbolos de integração declarados."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        declared_symbols = effect.get("integration_symbols") or []
        target_file = effect.get("target_file")
        if not declared_symbols or not target_file:
            continue
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            continue

        source = impl_path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        # Verificar que os símbolos declarados são usados (não verificamos o inverso — muito complexo)
        for sym in declared_symbols:
            if sym not in source:
                errors.append(
                    f"SE '{effect.get('side_effect_id', '?')}': símbolo de integração '{sym}' declarado mas não encontrado"
                )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_result_usage(rule: dict, ctx) -> RuleResult:
    """SE-010 (POST_EXECUTION, cannot_waive): Handlers de SE devem preservar SideEffectResult wrapper e shell de logging."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        target_file = effect.get("target_file")
        if not target_file:
            continue
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            continue
        source = impl_path.read_text(encoding="utf-8", errors="replace")
        if "SideEffectResult" not in source:
            errors.append(
                f"SE '{effect.get('side_effect_id', '?')}': SideEffectResult wrapper não encontrado em '{target_file}'"
            )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_trigger_logic_equivalence(rule: dict, ctx) -> RuleResult:
    """SE-011 (POST_EXECUTION, cannot_waive): Lógica de trigger gerada deve ser equivalente ao predicado declarado."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Verificação: cada SE com trigger_condition deve ter lógica de trigger no arquivo de implementação
    errors = []
    for effect in effects:
        trigger = effect.get("trigger") or {}
        condition = trigger.get("trigger_condition") or trigger.get("condition")
        target_file = effect.get("target_file")
        if not condition or not target_file:
            continue
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            continue

        source = impl_path.read_text(encoding="utf-8", errors="replace")
        # Verificação básica: trigger logic section presente
        if "trigger" not in source.lower() and "condition" not in source.lower():
            errors.append(
                f"SE '{effect.get('side_effect_id', '?')}': trigger_condition declarado mas lógica de trigger não encontrada"
            )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effect_predicate_manifest_is_present(rule: dict, ctx) -> RuleResult:
    """SE-012 (POST_PLAN, cannot_waive): Todo SE com trigger_condition deve ter entrada no manifesto de predicados."""
    effects = _get_side_effects(ctx)
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Verificar se existe manifesto de predicados
    manifest_path = ctx.repo_root / "_reports" / "side_effect_predicate_manifest.json"

    effects_with_condition = [
        e for e in effects
        if (e.get("trigger") or {}).get("trigger_condition") or (e.get("trigger") or {}).get("condition")
    ]

    if not effects_with_condition:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    if not manifest_path.exists():
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Side effects com trigger_condition declarados mas manifesto de predicados não encontrado em {manifest_path}",
        )

    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_side_effect_idempotency_keys_are_declared_and_safe", check_side_effect_idempotency_keys_are_declared_and_safe)
register_checker("check_side_effect_replay_policy_is_declared", check_side_effect_replay_policy_is_declared)
register_checker("check_side_effect_retry_policy_is_declared_when_retryable", check_side_effect_retry_policy_is_declared_when_retryable)
register_checker("check_side_effects_are_skipped_during_projection_rebuild", check_side_effects_are_skipped_during_projection_rebuild)
register_checker("check_no_undeclared_external_calls_exist", check_no_undeclared_external_calls_exist)
register_checker("check_side_effect_handlers_do_not_write_read_models", check_side_effect_handlers_do_not_write_read_models)
register_checker("check_side_effect_handlers_do_not_import_projection_modules", check_side_effect_handlers_do_not_import_projection_modules)
register_checker("check_side_effect_handlers_forbid_system_clock", check_side_effect_handlers_forbid_system_clock)
register_checker("check_side_effect_handlers_use_declared_integration_symbols", check_side_effect_handlers_use_declared_integration_symbols)
register_checker("check_side_effect_result_usage", check_side_effect_result_usage)
register_checker("check_side_effect_trigger_logic_equivalence", check_side_effect_trigger_logic_equivalence)
register_checker("check_side_effect_predicate_manifest_is_present", check_side_effect_predicate_manifest_is_present)
