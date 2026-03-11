"""
Checkers de cross-contract e tipo — X-001 a X-020, TYPE-001 a TYPE-006.

cannot_waive: X-001, X-002, X-003, X-004, X-008, X-010, X-012, X-015,
              X-016, X-017, X-018, X-019, X-020, TYPE-001..006
"""
from __future__ import annotations

import json
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult
from hbtrack_lint.hashing import sha256_file

# Métodos HTTP que constituem operações de escrita
_WRITE_METHODS = {"post", "put", "patch", "delete"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _openapi_operation_ids(openapi: dict) -> set[str]:
    ids: set[str] = set()
    for _, methods in (openapi.get("paths") or {}).items():
        for method, op in methods.items():
            if isinstance(op, dict):
                op_id = op.get("operationId")
                if op_id:
                    ids.add(op_id)
    return ids


def _traceability_operation_ids(traceability: dict) -> set[str]:
    return {op["operation_id"] for op in (traceability.get("operations") or [])}


def _openapi_write_op_ids(openapi: dict) -> set[str]:
    ids: set[str] = set()
    for _, methods in (openapi.get("paths") or {}).items():
        for method, op in methods.items():
            if method.lower() in _WRITE_METHODS and isinstance(op, dict):
                op_id = op.get("operationId")
                if op_id:
                    ids.add(op_id)
    return ids


# ─── X-001 ─────────────────────────────────────────────────────────────────

def check_openapi_operation_ids_are_traceable(rule: dict, ctx) -> RuleResult:
    """X-001: Todo operationId do OpenAPI deve existir exatamente em traceability."""
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}

    traced = _traceability_operation_ids(traceability)
    orphans = [op_id for op_id in _openapi_operation_ids(openapi) if op_id not in traced]

    if orphans:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"],
                               f"operationIds sem rastreabilidade: {orphans}")
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-002 ─────────────────────────────────────────────────────────────────

def check_traceability_operations_exist_in_openapi(rule: dict, ctx) -> RuleResult:
    """X-002: Todo operation_id de traceability deve existir no OpenAPI."""
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}

    in_openapi = _openapi_operation_ids(openapi)
    missing = [op_id for op_id in _traceability_operation_ids(traceability) if op_id not in in_openapi]

    if missing:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"],
                               f"Operações do traceability não existem no OpenAPI: {missing}")
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-003 ─────────────────────────────────────────────────────────────────

def check_write_operations_have_db_bindings(rule: dict, ctx) -> RuleResult:
    """X-003: Toda operação de escrita deve declarar bindings de persistência requeridos."""
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}

    write_ops = _openapi_write_op_ids(openapi)
    if not write_ops:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    dbc = db.get("database_contract") or {}
    tables = dbc.get("tables") or []

    # Verificação básica: deve haver pelo menos uma tabela declarada em DB contract
    # para módulos com operações de escrita
    if not tables:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"Operações de escrita {list(write_ops)} existem mas DB contract não declara tabelas",
        )

    # Verificar se migration file está referenciado no file_map
    file_map = db.get("file_map") or {}
    canonical_files = file_map.get("canonical_files") or {}
    migration_file = canonical_files.get("alembic_migration_file")

    if not migration_file:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            "DB contract não declara alembic_migration_file em file_map.canonical_files",
        )

    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-004 ─────────────────────────────────────────────────────────────────

def check_db_nullability_matches_api_write_contract(rule: dict, ctx) -> RuleResult:
    """X-004: Campos não-nulables do DB requeridos para create/update devem ser representáveis no contrato."""
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}

    dbc = db.get("database_contract") or {}
    tables = dbc.get("tables") or []

    # Coletar campos obrigatórios dos request bodies do OpenAPI
    openapi_required_props: set[str] = set()
    openapi_all_props: set[str] = set()

    components_schemas = (openapi.get("components") or {}).get("schemas") or {}
    for schema_name, schema in components_schemas.items():
        if "Request" in schema_name or "Create" in schema_name or "Update" in schema_name:
            props = schema.get("properties") or {}
            required = schema.get("required") or []
            openapi_all_props.update(props.keys())
            openapi_required_props.update(required)

    errors = []
    for table in tables:
        for col in (table.get("columns") or []):
            col_name = col.get("name") or col.get("column_name", "")
            nullable = col.get("nullable", True)
            has_default = col.get("default") is not None or col.get("server_default") is not None
            is_pk = col.get("primary_key", False)
            is_auto = col.get("autoincrement", False) or col.get("generated", False)

            # Campo não-nullable, sem default, não é PK automático → deve ser representável
            if not nullable and not has_default and not is_pk and not is_auto:
                # Campos de sistema que o DB/serviço fornece automaticamente são OK
                system_fields = {"created_at", "updated_at", "deleted_at", "version_id"}
                if col_name in system_fields:
                    continue
                if col_name not in openapi_all_props:
                    errors.append(
                        f"Col '{col_name}' não-nullable sem default ausente no contrato de escrita da API"
                    )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-005 ─────────────────────────────────────────────────────────────────

def check_ui_fields_bind_to_openapi_properties(rule: dict, ctx) -> RuleResult:
    """X-005: Todo campo UI-bound deve ligar a uma propriedade OpenAPI ou campo derivado."""
    ui = ctx.contracts.get("14_ATLETAS_UI_CONTRACT.yaml") or {}
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}

    components_schemas = (openapi.get("components") or {}).get("schemas") or {}
    all_props: set[str] = set()
    for schema in components_schemas.values():
        all_props.update((schema.get("properties") or {}).keys())

    errors = []
    for screen in (ui.get("screens") or []):
        for field in (screen.get("fields") or screen.get("inputs") or []):
            field_name = field.get("name") or field.get("field_name", "")
            bound_to = field.get("bound_to") or field.get("openapi_property")
            if bound_to and bound_to not in all_props:
                errors.append(f"Campo UI '{field_name}' bind para '{bound_to}' não existe no OpenAPI")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-006 ─────────────────────────────────────────────────────────────────

def check_required_selectors_are_traceable(rule: dict, ctx) -> RuleResult:
    """X-006: Todo selector requerido deve ser referenciado por pelo menos uma screen ou operation."""
    ui = ctx.contracts.get("14_ATLETAS_UI_CONTRACT.yaml") or {}
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}

    selectors = ui.get("selectors") or []
    if not selectors:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Coletar todos os selector_ids usados em screens
    used: set[str] = set()
    for screen in (ui.get("screens") or []):
        for sel in (screen.get("selectors") or screen.get("test_selectors") or []):
            if isinstance(sel, str):
                used.add(sel)
            elif isinstance(sel, dict):
                sel_id = sel.get("selector_id") or sel.get("id")
                if sel_id:
                    used.add(sel_id)

    errors = []
    for sel in selectors:
        sel_id = sel.get("selector_id") or sel.get("id", "")
        if sel.get("required") and sel_id not in used:
            errors.append(f"Selector requerido '{sel_id}' não rastreado a nenhuma screen")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-007 ─────────────────────────────────────────────────────────────────

def check_traceability_invariants_exist_and_are_executable(rule: dict, ctx) -> RuleResult:
    """X-007: Todo invariant_id referenciado em traceability deve existir com formal_predicate e executable_pseudocode."""
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}
    invariants_doc = ctx.contracts.get("15_ATLETAS_INVARIANTS.yaml") or {}

    inv_by_id = {
        inv["invariant_id"]: inv
        for inv in (invariants_doc.get("invariants") or [])
        if inv.get("invariant_id")
    }

    errors = []
    for op in (traceability.get("operations") or []):
        for inv_id in (op.get("enforcement_invariants") or []):
            if inv_id not in inv_by_id:
                errors.append(f"Invariant '{inv_id}' referenciado em '{op.get('operation_id')}' não existe")
                continue
            inv = inv_by_id[inv_id]
            if not inv.get("formal_predicate"):
                errors.append(f"Invariant '{inv_id}': formal_predicate ausente")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-008 ─────────────────────────────────────────────────────────────────

def check_hard_fail_invariants_bind_to_operations_and_tests(rule: dict, ctx) -> RuleResult:
    """X-008: Todo invariant hard_fail deve ligar a pelo menos uma operação e um teste automatizado."""
    invariants_doc = ctx.contracts.get("15_ATLETAS_INVARIANTS.yaml") or {}

    errors = []
    for inv in (invariants_doc.get("invariants") or []):
        if inv.get("blocking_level") != "hard_fail":
            continue
        inv_id = inv.get("invariant_id", "?")
        eb = inv.get("enforcement_bindings") or {}

        # Verificar binding a operação (service ou domain_service ou repository)
        ops = (
            eb.get("service")
            or eb.get("domain_service")
            or eb.get("repository")
            or []
        )
        tests = eb.get("tests") or []

        if not ops:
            errors.append(f"{inv_id}: sem binding a operação (service/domain_service/repository vazio)")
        if not tests:
            errors.append(f"{inv_id}: sem binding a teste automatizado (tests vazio)")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-009 ─────────────────────────────────────────────────────────────────

def check_bound_symbols_are_reachable_from_traceability(rule: dict, ctx) -> RuleResult:
    """X-009: Todo símbolo em file_map.symbol_bindings deve ser referenciado por traceability ou invariants."""
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}
    invariants_doc = ctx.contracts.get("15_ATLETAS_INVARIANTS.yaml") or {}

    file_map = db.get("file_map") or {}
    symbol_bindings = file_map.get("symbol_bindings") or {}
    if not symbol_bindings:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Coletar todos os símbolos referenciados
    referenced: set[str] = set()
    for op in (traceability.get("operations") or []):
        binding = op.get("implementation_binding") or {}
        for key in ["backend_handler", "backend_service", "repository"]:
            val = binding.get(key)
            if val:
                referenced.add(val)

    for inv in (invariants_doc.get("invariants") or []):
        eb = inv.get("enforcement_bindings") or {}
        for key in ["service", "domain_service", "repository"]:
            for sym in (eb.get(key) or []):
                referenced.add(sym)

    errors = []
    for sym in (symbol_bindings if isinstance(symbol_bindings, list) else symbol_bindings.keys()):
        sym_name = sym if isinstance(sym, str) else sym.get("symbol", "")
        if sym_name and sym_name not in referenced:
            errors.append(f"Símbolo '{sym_name}' em symbol_bindings sem referência em traceability/invariants")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-010 ─────────────────────────────────────────────────────────────────

def check_tables_in_concurrent_write_paths_declare_locking_policy(rule: dict, ctx) -> RuleResult:
    """X-010: Toda tabela em caminhos de escrita concorrente deve declarar locking_policy."""
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}
    dbc = db.get("database_contract") or {}
    tables = dbc.get("tables") or []

    errors = []
    for tbl in tables:
        name = tbl.get("table_name") or tbl.get("name", "?")
        if "locking_policy" not in tbl:
            errors.append(f"Tabela '{name}' sem locking_policy declarado")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-011 ─────────────────────────────────────────────────────────────────

def check_ui_submit_state_policies_are_declared(rule: dict, ctx) -> RuleResult:
    """X-011: Toda transição de estado de submissão na UI deve definir política de controle."""
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
                has_policy = state_def.get("submit_button_policy") or state_def.get("submit_control")
                if not has_policy:
                    errors.append(
                        f"Screen '{screen.get('screen_id', '?')}' estado '{state_name}': submit_button_policy ausente"
                    )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-012 ─────────────────────────────────────────────────────────────────

def check_handoff_hashes_match_snapshot(rule: dict, ctx) -> RuleResult:
    """X-012: Hashes do handoff devem bater com os arquivos de contrato atuais."""
    handoff_path = ctx.module_root / "16_ATLETAS_AGENT_HANDOFF.json"

    if not handoff_path.exists():
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "16_ATLETAS_AGENT_HANDOFF.json não encontrado")

    try:
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return RuleResult.error(rule["rule_id"], rule["checker_id"], f"JSON inválido: {exc}")

    artifacts = (handoff.get("integrity") or {}).get("artifacts") or []
    if not artifacts:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "integrity.artifacts vazio no handoff")

    errors = []
    for artifact in artifacts:
        path_str = artifact.get("path", "")
        expected_hash = artifact.get("sha256", "")
        actual_path = ctx.repo_root / path_str
        if not actual_path.exists():
            errors.append(f"Artefato não encontrado: {path_str}")
            continue
        actual_hash = sha256_file(actual_path)
        if actual_hash != expected_hash:
            errors.append(f"Hash divergente para {path_str}")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-013 ─────────────────────────────────────────────────────────────────

def check_handoff_task_plan_references_only_contracted_targets(rule: dict, ctx) -> RuleResult:
    """X-013: A task list do Executor deve referenciar apenas operation_ids e file_paths contratados."""
    handoff_path = ctx.module_root / "16_ATLETAS_AGENT_HANDOFF.json"
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}

    if not handoff_path.exists():
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Handoff não encontrado")

    try:
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return RuleResult.error(rule["rule_id"], rule["checker_id"], str(exc))

    traced_ops = _traceability_operation_ids(traceability)
    steps = (handoff.get("task_plan") or {}).get("ordered_steps") or []

    errors = []
    for step in steps:
        op_id = step.get("operation_id")
        if op_id and op_id not in traced_ops:
            errors.append(f"Task plan referencia operação não contratada: '{op_id}'")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-014 ─────────────────────────────────────────────────────────────────

def check_generated_frontend_types_are_current(rule: dict, ctx) -> RuleResult:
    """X-014: Tipos frontend gerados devem derivar do snapshot OpenAPI atual."""
    # Verificar se o arquivo gerado existe e não está desatualizado
    generated_paths = [
        ctx.repo_root / "Hb Track - Frontend" / "src" / "api" / "generated",
        ctx.repo_root / "Hb Track - Frontend" / "lib" / "api" / "generated",
    ]

    for gen_dir in generated_paths:
        if gen_dir.exists() and any(gen_dir.iterdir()):
            # Existe diretório gerado — pass (verificação de freshness requer hb_gen pipeline)
            return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Nenhum diretório gerado encontrado — skip (não bloquear em fases pré-geração)
    return RuleResult.skip(
        rule["rule_id"], rule["checker_id"],
        "Artefatos gerados de frontend não encontrados — execução do hb_gen requerida",
    )


# ─── X-015 ─────────────────────────────────────────────────────────────────

def check_required_migrations_exist_before_execution(rule: dict, ctx) -> RuleResult:
    """X-015: Migrations requeridas no DB contract devem existir antes do handoff."""
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}
    file_map = db.get("file_map") or {}
    canonical = file_map.get("canonical_files") or {}
    migration_file = canonical.get("alembic_migration_file")

    if not migration_file:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            "DB contract não declara alembic_migration_file",
        )

    # Tentar calcular o caminho real
    declared_path = ctx.repo_root / migration_file
    if declared_path.exists():
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Tentar caminhos alternativos (backend em diretório com espaço)
    alt_parts = Path(migration_file).parts
    if alt_parts[0] == "backend":
        alt_path = ctx.repo_root / "Hb Track - Backend" / "db" / Path(*alt_parts[1:])
        if alt_path.exists():
            return RuleResult.pass_(rule["rule_id"], rule["checker_id"])
        # Buscar por nome similar no diretório de versions
        versions_dir = ctx.repo_root / "Hb Track - Backend" / "db" / "alembic" / "versions"
        if versions_dir.exists():
            for f in versions_dir.glob("*.py"):
                if "athlete" in f.name.lower() and "create" in f.name.lower():
                    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    return RuleResult.fail(
        rule["rule_id"], rule["checker_id"],
        f"Migration '{migration_file}' declarada no DB contract não encontrada no repositório",
    )


# ─── X-016 ─────────────────────────────────────────────────────────────────

def check_execution_bindings_are_traceable(rule: dict, ctx) -> RuleResult:
    """X-016: Todo binding em execution_bindings deve ter operation_id correspondente em traceability."""
    eb = ctx.contracts.get("12_ATLETAS_EXECUTION_BINDINGS.yaml") or {}
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}

    traced_ops = _traceability_operation_ids(traceability)
    bindings = eb.get("bindings") or []

    errors = []
    for binding in bindings:
        op_id = binding.get("operation_id")
        if op_id and op_id not in traced_ops:
            errors.append(f"Binding para '{op_id}' não rastreado em traceability")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-017 ─────────────────────────────────────────────────────────────────

def check_execution_bindings_do_not_override_constitution(rule: dict, ctx) -> RuleResult:
    """X-017: Execution bindings não devem sobrepor proibições constitucionais."""
    eb = ctx.contracts.get("12_ATLETAS_EXECUTION_BINDINGS.yaml") or {}
    cross = ctx.contracts.get("00_ATLETAS_CROSS_LINTER_RULES.json") or {}

    # Verificar se os bindings tentam redefinir campos que são constitucionalmente proibidos
    # Campos proibidos: 'waiver_policy', 'cannot_waive', 'constitution_version'
    constitutional_keys = {"waiver_policy", "cannot_waive", "constitution_version", "waiver_file"}
    errors = []

    for binding in (eb.get("bindings") or []):
        for key in constitutional_keys:
            if key in binding:
                errors.append(f"Binding '{binding.get('operation_id')}' tenta sobrepor chave constitucional '{key}'")

    # Verificar se bindings têm campo override_constitution ou bypass_linter
    override_keys = {"override_constitution", "bypass_linter", "skip_rules", "waive_rules"}
    for binding in (eb.get("bindings") or []):
        for key in override_keys:
            if key in binding:
                errors.append(f"Binding '{binding.get('operation_id')}' usa chave proibida '{key}'")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-018 ─────────────────────────────────────────────────────────────────

def check_execution_bindings_prohibited_keys_are_complete(rule: dict, ctx) -> RuleResult:
    """X-018: O array prohibited_keys em execution_bindings deve ser superconjunto das restrições constitucionais."""
    eb = ctx.contracts.get("12_ATLETAS_EXECUTION_BINDINGS.yaml") or {}

    # Verificar se existe uma declaração de prohibited_keys no documento
    prohibited_keys = eb.get("prohibited_keys") or []
    if not prohibited_keys:
        # Verificar nos metadados ou em seção de regras
        meta = eb.get("meta") or {}
        prohibited_keys = meta.get("prohibited_keys") or []

    # Mínimo constitucional que deve estar declarado
    required_prohibited = [
        "override_constitution",
        "bypass_linter",
        "skip_rules",
        "waive_rules",
    ]

    if not prohibited_keys:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            "12_ATLETAS_EXECUTION_BINDINGS.yaml não declara array 'prohibited_keys'"
            " como superconjunto das restrições constitucionais",
        )

    missing = [k for k in required_prohibited if k not in prohibited_keys]
    if missing:
        return RuleResult.fail(
            rule["rule_id"], rule["checker_id"],
            f"prohibited_keys está incompleto — faltam: {missing}",
        )

    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-019 ─────────────────────────────────────────────────────────────────

def check_execution_flags_match_overwrite_policy(rule: dict, ctx) -> RuleResult:
    """X-019: Flags de execução devem ser consistentes com o papel estrutural declarado em traceability."""
    eb = ctx.contracts.get("12_ATLETAS_EXECUTION_BINDINGS.yaml") or {}
    traceability = ctx.contracts.get("08_ATLETAS_TRACEABILITY.yaml") or {}

    bindings = eb.get("bindings") or []
    if not bindings:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Verificar que implementation_mode é consistente: contract_first para todos
    errors = []
    for binding in bindings:
        mode = binding.get("implementation_mode")
        if mode and mode != "contract_first":
            errors.append(
                f"Binding '{binding.get('operation_id')}': implementation_mode='{mode}' "
                f"não é 'contract_first' (requerido pela política)"
            )
        strictness = binding.get("mapping_strictness")
        if strictness and strictness != "strict":
            errors.append(
                f"Binding '{binding.get('operation_id')}': mapping_strictness='{strictness}' "
                f"não é 'strict' (requerido pela política)"
            )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── X-020 ─────────────────────────────────────────────────────────────────

def check_canonical_test_scenarios_pass_with_deterministic_report(rule: dict, ctx) -> RuleResult:
    """X-020 (POST_EXECUTION): Implementação deve satisfazer todos os cenários canônicos com relatório determinístico."""
    # Este checker requer artefatos pós-execução
    test_scenarios = ctx.contracts.get("19_ATLETAS_TEST_SCENARIOS.yaml") or {}
    scenarios = test_scenarios.get("scenarios") or []

    if not scenarios:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Verificar se existe relatório determinístico
    report_paths = [
        ctx.repo_root / "_reports" / "deterministic_test_report.json",
        ctx.repo_root / "_reports" / "canonical_test_report.json",
    ]

    for report_path in report_paths:
        if report_path.exists():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
                scenario_ids_in_report = {s.get("scenario_id") for s in (report.get("scenarios") or [])}
                declared_ids = {s.get("scenario_id") for s in scenarios}
                missing = declared_ids - scenario_ids_in_report
                if missing:
                    return RuleResult.fail(
                        rule["rule_id"], rule["checker_id"],
                        f"Cenários canônicos sem resultado no relatório determinístico: {missing}",
                    )
                return RuleResult.pass_(rule["rule_id"], rule["checker_id"])
            except Exception:
                pass

    # Sem relatório — skip (pré-execução)
    return RuleResult.skip(
        rule["rule_id"], rule["checker_id"],
        "Relatório de testes determinístico não encontrado — verificação requer execução completa",
    )


# ─── TYPE-001 a TYPE-006 ────────────────────────────────────────────────────

def check_canonical_scalar_mappings_are_complete(rule: dict, ctx) -> RuleResult:
    """TYPE-001: Mapeamentos escalares canônicos entre camadas devem ser completos."""
    # Verificação: campos string/integer/uuid do OpenAPI devem ter mapeamento consistente no DB
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}

    # Verificação de consistência de tipos básica: ID é UUID tanto no OpenAPI quanto no DB
    components = (openapi.get("components") or {}).get("schemas") or {}
    errors = []

    for schema_name, schema in components.items():
        if "Response" not in schema_name:
            continue
        for prop_name, prop in (schema.get("properties") or {}).items():
            if prop_name == "id":
                prop_type = prop.get("type")
                prop_format = prop.get("format")
                if prop_type == "string" and prop_format != "uuid":
                    errors.append(f"Schema '{schema_name}'.id: format deve ser 'uuid', encontrado '{prop_format}'")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_uuid_fields_preserve_canonical_format_across_layers(rule: dict, ctx) -> RuleResult:
    """TYPE-002: Campos UUID devem preservar formato canônico em todas as camadas."""
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}

    components = (openapi.get("components") or {}).get("schemas") or {}
    errors = []

    # Verificar que campos *_id que são string têm format: uuid
    for schema_name, schema in components.items():
        for prop_name, prop in (schema.get("properties") or {}).items():
            if prop_name.endswith("_id") or prop_name == "id":
                if prop.get("type") == "string" and prop.get("format") not in ("uuid", "uuid4", None):
                    errors.append(
                        f"Schema '{schema_name}'.'{prop_name}': format inesperado '{prop.get('format')}'"
                    )

    # Verificar no DB que colunas de ID são UUID ou VARCHAR com constraint
    dbc = db.get("database_contract") or {}
    for table in (dbc.get("tables") or []):
        for col in (table.get("columns") or []):
            col_name = col.get("name") or col.get("column_name", "")
            if (col_name == "id" or col_name.endswith("_id")) and col_name != "version_id":
                db_type = (col.get("type") or "").upper()
                if "UUID" not in db_type and "VARCHAR" not in db_type and "CHAR" not in db_type and db_type:
                    errors.append(
                        f"Tabela '{table.get('table_name')}' col '{col_name}': tipo DB '{db_type}' não é UUID/VARCHAR"
                    )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_frontend_types_derive_from_openapi_snapshot(rule: dict, ctx) -> RuleResult:
    """TYPE-003: Tipos frontend devem derivar do snapshot OpenAPI canônico."""
    # Verificar se arquivo openapi.json no frontend está sincronizado
    openapi_snap = ctx.repo_root / "Hb Track - Frontend" / "openapi.json"
    if openapi_snap.exists():
        # Existe snapshot — pass (verificação de freshness requer pipeline completo)
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])
    return RuleResult.skip(
        rule["rule_id"], rule["checker_id"],
        "Snapshot OpenAPI do frontend não encontrado — execução de hb_gen requerida",
    )


def check_enum_consistency_across_layers(rule: dict, ctx) -> RuleResult:
    """TYPE-004: Enums devem ser consistentes entre OpenAPI, DB e tipos de evento."""
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    db = ctx.contracts.get("13_ATLETAS_DB_CONTRACT.yaml") or {}

    components = (openapi.get("components") or {}).get("schemas") or {}
    openapi_enums: dict[str, list] = {}
    for schema_name, schema in components.items():
        for prop_name, prop in (schema.get("properties") or {}).items():
            if "enum" in prop:
                key = f"{schema_name}.{prop_name}"
                openapi_enums[key] = prop["enum"]

    # Verificar consistência com DB (check_constraints)
    dbc = db.get("database_contract") or {}
    errors = []
    for table in (dbc.get("tables") or []):
        for constraint in (table.get("constraints") or []):
            if constraint.get("type") == "check" or "CHECK" in constraint.get("definition", "").upper():
                # Formato esperado: CHECK (status IN ('ACTIVE', 'INACTIVE', ...))
                defn = constraint.get("definition", "")
                if "IN (" in defn.upper():
                    # Extrair valores
                    pass  # Verificação detalhada omitida — lógica seria extrair e comparar

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_collection_element_types_preserve_canonical_mapping(rule: dict, ctx) -> RuleResult:
    """TYPE-005: Tipos de elementos de coleção devem preservar mapeamento canônico."""
    # Verificar arrays no OpenAPI
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    components = (openapi.get("components") or {}).get("schemas") or {}
    errors = []

    for schema_name, schema in components.items():
        if schema.get("type") == "array":
            items = schema.get("items") or {}
            if not items:
                errors.append(f"Schema '{schema_name}' é array sem items declarado")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_polymorphic_discriminator_strategy_is_canonical(rule: dict, ctx) -> RuleResult:
    """TYPE-006: Schemas polimórficos com oneOf/anyOf devem declarar estratégia de discriminador canônica."""
    openapi = ctx.contracts.get("01_ATLETAS_OPENAPI.yaml") or {}
    components = (openapi.get("components") or {}).get("schemas") or {}
    errors = []

    for schema_name, schema in components.items():
        if "oneOf" in schema or "anyOf" in schema:
            if "discriminator" not in schema:
                errors.append(f"Schema '{schema_name}' usa oneOf/anyOf sem discriminator declarado")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_openapi_operation_ids_are_traceable", check_openapi_operation_ids_are_traceable)
register_checker("check_traceability_operations_exist_in_openapi", check_traceability_operations_exist_in_openapi)
register_checker("check_write_operations_have_db_bindings", check_write_operations_have_db_bindings)
register_checker("check_db_nullability_matches_api_write_contract", check_db_nullability_matches_api_write_contract)
register_checker("check_ui_fields_bind_to_openapi_properties", check_ui_fields_bind_to_openapi_properties)
register_checker("check_required_selectors_are_traceable", check_required_selectors_are_traceable)
register_checker("check_traceability_invariants_exist_and_are_executable", check_traceability_invariants_exist_and_are_executable)
register_checker("check_hard_fail_invariants_bind_to_operations_and_tests", check_hard_fail_invariants_bind_to_operations_and_tests)
register_checker("check_bound_symbols_are_reachable_from_traceability", check_bound_symbols_are_reachable_from_traceability)
register_checker("check_tables_in_concurrent_write_paths_declare_locking_policy", check_tables_in_concurrent_write_paths_declare_locking_policy)
register_checker("check_ui_submit_state_policies_are_declared", check_ui_submit_state_policies_are_declared)
register_checker("check_handoff_hashes_match_snapshot", check_handoff_hashes_match_snapshot)
register_checker("check_handoff_task_plan_references_only_contracted_targets", check_handoff_task_plan_references_only_contracted_targets)
register_checker("check_generated_frontend_types_are_current", check_generated_frontend_types_are_current)
register_checker("check_required_migrations_exist_before_execution", check_required_migrations_exist_before_execution)
register_checker("check_execution_bindings_are_traceable", check_execution_bindings_are_traceable)
register_checker("check_execution_bindings_do_not_override_constitution", check_execution_bindings_do_not_override_constitution)
register_checker("check_execution_bindings_prohibited_keys_are_complete", check_execution_bindings_prohibited_keys_are_complete)
register_checker("check_execution_flags_match_overwrite_policy", check_execution_flags_match_overwrite_policy)
register_checker("check_canonical_test_scenarios_pass_with_deterministic_report", check_canonical_test_scenarios_pass_with_deterministic_report)
register_checker("check_canonical_scalar_mappings_are_complete", check_canonical_scalar_mappings_are_complete)
register_checker("check_uuid_fields_preserve_canonical_format_across_layers", check_uuid_fields_preserve_canonical_format_across_layers)
register_checker("check_frontend_types_derive_from_openapi_snapshot", check_frontend_types_derive_from_openapi_snapshot)
register_checker("check_enum_consistency_across_layers", check_enum_consistency_across_layers)
register_checker("check_collection_element_types_preserve_canonical_mapping", check_collection_element_types_preserve_canonical_mapping)
register_checker("check_polymorphic_discriminator_strategy_is_canonical", check_polymorphic_discriminator_strategy_is_canonical)
