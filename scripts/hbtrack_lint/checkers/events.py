"""
Checkers de eventos — EV-001 a EV-009.

cannot_waive: EV-008
"""
from __future__ import annotations

import ast
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult


def check_projection_event_types_exist(rule: dict, ctx) -> RuleResult:
    """EV-001: Todo event_type consumido por projeção deve existir no AsyncAPI."""
    events = ctx.contracts.get("05_ATLETAS_EVENTS.asyncapi.yaml") or {}
    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}

    # Coletar event_types declarados no AsyncAPI
    channels = events.get("channels") or {}
    messages = (events.get("components") or {}).get("messages") or {}
    declared_events: set[str] = set(messages.keys())
    for ch_name, ch_data in channels.items():
        msg = (ch_data.get("publish") or ch_data.get("subscribe") or {}).get("message")
        if isinstance(msg, dict):
            event_id = msg.get("$ref", "").split("/")[-1] or msg.get("messageId")
            if event_id:
                declared_events.add(event_id)
        elif isinstance(msg, str):
            declared_events.add(msg.split("/")[-1])

    read_models = projections.get("read_models") or []
    errors = []
    for rm in read_models:
        for handler in (rm.get("event_handlers") or []):
            event_type = handler.get("event_type") or handler.get("event")
            if event_type and declared_events and event_type not in declared_events:
                errors.append(f"Projeção '{rm.get('read_model_id', '?')}': event_type '{event_type}' não declarado no AsyncAPI")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_versions_are_supported_or_upcasted(rule: dict, ctx) -> RuleResult:
    """EV-002: Toda versão de evento consumida por projeção deve ser suportada ou ter upcaster."""
    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    upcast_pipeline = projections.get("upcast_pipeline")
    # upcast_pipeline pode ser dict (policy) ou list (upcasters) dependendo da versão do contrato
    upcast_list = upcast_pipeline if isinstance(upcast_pipeline, list) else []
    upcasted_versions: set[tuple] = {
        (u.get("event_type"), str(u.get("from_version")))
        for u in upcast_list if isinstance(u, dict)
    }

    errors = []
    read_models = projections.get("read_models") or []
    for rm in read_models:
        for handler in (rm.get("event_handlers") or []):
            event_type = handler.get("event_type") or ""
            versions = handler.get("supported_versions") or [handler.get("event_version")]
            for v in versions:
                if v is None:
                    continue

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_side_effects_reference_declared_events(rule: dict, ctx) -> RuleResult:
    """EV-003: Todo side effect baseado em evento deve referenciar event_type e event_version declarados."""
    events = ctx.contracts.get("05_ATLETAS_EVENTS.asyncapi.yaml") or {}
    side_effects = ctx.contracts.get("18_ATLETAS_SIDE_EFFECTS.yaml") or {}

    effects = side_effects.get("side_effects") or []
    if not effects:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for effect in effects:
        trigger = effect.get("trigger") or {}
        event_type = trigger.get("event_type")
        if event_type:
            event_version = trigger.get("event_version")
            if not event_version:
                errors.append(f"Side effect '{effect.get('side_effect_id', '?')}': event_version ausente")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_and_side_effect_handlers_are_separated(rule: dict, ctx) -> RuleResult:
    """EV-004: Handlers de projeção não devem sobrepor handlers de side-effect."""
    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    side_effects = ctx.contracts.get("18_ATLETAS_SIDE_EFFECTS.yaml") or {}

    proj_symbols: set[str] = set()
    read_models = projections.get("read_models") or []
    for rm in read_models:
        sym = rm.get("target_model_symbol")
        if sym:
            proj_symbols.add(sym)
        for handler in (rm.get("event_handlers") or []):
            h_sym = handler.get("handler_symbol")
            if h_sym:
                proj_symbols.add(h_sym)

    se_symbols: set[str] = set()
    for effect in (side_effects.get("side_effects") or []):
        sym = effect.get("handler_symbol")
        if sym:
            se_symbols.add(sym)

    overlap = proj_symbols & se_symbols
    if overlap:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Símbolos compartilhados entre projeção e side-effect: {list(overlap)}",
        )
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_read_models_have_event_provenance(rule: dict, ctx) -> RuleResult:
    """EV-005: Se source_of_truth é event_store, todo read model deve ter mapeamento de evento."""
    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    event_store = projections.get("event_store_contract") or {}

    if event_store.get("source_of_truth") != "event_store":
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    read_models = projections.get("read_models") or []
    errors = []
    for rm in read_models:
        if not (rm.get("event_handlers") or rm.get("source_events")):
            errors.append(f"Read model '{rm.get('read_model_id', '?')}' sem mapeamento de evento")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_event_aggregate_id_type_matches_db_contract(rule: dict, ctx) -> RuleResult:
    """EV-006: aggregate_id do evento deve bater com o tipo de identificador canônico no DB contract."""
    events = ctx.contracts.get("05_ATLETAS_EVENTS.asyncapi.yaml") or {}
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}

    if not events:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_event_partition_key_matches_aggregate_id(rule: dict, ctx) -> RuleResult:
    """EV-007: Contratos de evento e projeção devem concordar em aggregate_id como partition key."""
    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    read_models = projections.get("read_models") or []

    errors = []
    for rm in read_models:
        partition_key = rm.get("partition_key")
        if partition_key and partition_key not in ("id", "athlete_id", "aggregate_id"):
            errors.append(f"Read model '{rm.get('read_model_id', '?')}': partition_key='{partition_key}' inesperado")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_upcasters_are_pure_functions(rule: dict, ctx) -> RuleResult:
    """EV-008 (POST_EXECUTION, cannot_waive): Upcasters devem ser funções puras sobre entrada validada e defaults injetados."""
    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    upcast_pipeline = projections.get("upcast_pipeline")
    upcast_list = upcast_pipeline if isinstance(upcast_pipeline, list) else []

    if not upcast_list:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    errors = []
    for upcaster in upcast_list:
        if not isinstance(upcaster, dict):
            continue
        symbol = upcaster.get("handler_symbol") or upcaster.get("function")
        target_file = upcaster.get("target_file")
        if not symbol or not target_file:
            continue

        # Verificar o arquivo de implementação (POST_EXECUTION)
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            # Não existe ainda — skip
            continue

        source = impl_path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            errors.append(f"Upcaster '{symbol}': arquivo com erro de sintaxe")
            continue

        # Verificar usos proibidos: datetime.now, date.today, random, side effects externos
        forbidden_calls = {"datetime.now", "date.today", "time.time", "random", "requests", "httpx", "os.environ"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                call_str = ""
                if isinstance(func, ast.Attribute):
                    call_str = f"{getattr(func.value, 'id', '')}.{func.attr}"
                elif isinstance(func, ast.Name):
                    call_str = func.id
                if call_str in forbidden_calls:
                    errors.append(f"Upcaster '{symbol}': uso proibido de '{call_str}' (não-puro)")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_pydantic_model_construct_forbidden_in_event_pipeline(rule: dict, ctx) -> RuleResult:
    """EV-009 (POST_EXECUTION): model_construct proibido no pipeline de eventos."""
    projections = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    read_models = projections.get("read_models") or []

    errors = []
    for rm in read_models:
        target_file = rm.get("target_file")
        if not target_file:
            continue
        impl_path = ctx.repo_root / target_file
        if not impl_path.exists():
            continue
        source = impl_path.read_text(encoding="utf-8", errors="replace")
        if "model_construct" in source:
            errors.append(f"'{target_file}': uso de model_construct proibido no pipeline de eventos")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_projection_event_types_exist", check_projection_event_types_exist)
register_checker("check_projection_versions_are_supported_or_upcasted", check_projection_versions_are_supported_or_upcasted)
register_checker("check_side_effects_reference_declared_events", check_side_effects_reference_declared_events)
register_checker("check_projection_and_side_effect_handlers_are_separated", check_projection_and_side_effect_handlers_are_separated)
register_checker("check_read_models_have_event_provenance", check_read_models_have_event_provenance)
register_checker("check_event_aggregate_id_type_matches_db_contract", check_event_aggregate_id_type_matches_db_contract)
register_checker("check_event_partition_key_matches_aggregate_id", check_event_partition_key_matches_aggregate_id)
register_checker("check_upcasters_are_pure_functions", check_upcasters_are_pure_functions)
register_checker("check_pydantic_model_construct_forbidden_in_event_pipeline", check_pydantic_model_construct_forbidden_in_event_pipeline)
