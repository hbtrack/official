"""
Checkers de projeções e read models — PROJ-001..010.

cannot_waive: PROJ-006, PROJ-010
"""
from __future__ import annotations

import ast
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult

# ─── Utilitários para PROJ-006 (extraídos de MOTORES.md) ──────────────────

def _extract_call_name(func: ast.AST) -> tuple[str | None, str | None]:
    if isinstance(func, ast.Name):
        return func.id, None
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            return func.value.id, func.attr
        return None, func.attr
    return None, None


def _keyword_uses_name(node: ast.Call, keyword_name: str, var_name: str) -> bool:
    for kw in node.keywords:
        if kw.arg == keyword_name and isinstance(kw.value, ast.Name) and kw.value.id == var_name:
            return True
    return False


class ProjectionAtomicShellVisitor(ast.NodeVisitor):
    def __init__(self, target_function: str):
        self.target_function = target_function
        self.function_found = False
        self.with_transaction_scope = False
        self.idempotency_guard_found = False
        self.ledger_mark_found = False
        self.tx_aliases: set[str] = set()
        self.violations: list[dict] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name != self.target_function:
            return

        self.function_found = True

        for stmt in node.body:
            if isinstance(stmt, ast.With):
                for item in stmt.items:
                    if isinstance(item.context_expr, ast.Call):
                        name, attr = _extract_call_name(item.context_expr.func)
                        if name == "transaction_scope" and attr is None:
                            self.with_transaction_scope = True
                            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                                self.tx_aliases.add(item.optional_vars.id)
                            else:
                                self.violations.append({
                                    "kind": "missing_tx_alias",
                                    "lineno": stmt.lineno,
                                })
                            self._inspect_transaction_block(stmt)

        if not self.with_transaction_scope:
            self.violations.append({
                "kind": "missing_transaction_scope",
                "function": node.name,
                "lineno": node.lineno,
            })

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def _inspect_transaction_block(self, with_node: ast.With) -> None:
        for stmt in with_node.body:
            # idempotency guard
            if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Call):
                name, attr = _extract_call_name(stmt.test.func)
                if name == "projection_event_already_applied" and attr is None:
                    tx_ok = any(_keyword_uses_name(stmt.test, "tx", tx) for tx in self.tx_aliases)
                    if tx_ok:
                        self.idempotency_guard_found = True
                    else:
                        self.violations.append({
                            "kind": "idempotency_guard_missing_tx",
                            "lineno": stmt.lineno,
                        })

            # ledger mark
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                name, attr = _extract_call_name(stmt.value.func)
                if name == "mark_projection_event_applied" and attr is None:
                    tx_ok = any(_keyword_uses_name(stmt.value, "tx", tx) for tx in self.tx_aliases)
                    if tx_ok:
                        self.ledger_mark_found = True
                    else:
                        self.violations.append({
                            "kind": "ledger_mark_missing_tx",
                            "lineno": stmt.lineno,
                        })

    def finalize(self) -> None:
        if self.function_found:
            if not self.idempotency_guard_found:
                self.violations.append({"kind": "missing_idempotency_guard"})
            if not self.ledger_mark_found:
                self.violations.append({"kind": "missing_ledger_mark"})


# ─── Checkers ─────────────────────────────────────────────────────────────

def check_projection_event_types_exist(rule: dict, ctx) -> RuleResult:
    """PROJ-001 (PRE_PLAN): Tipos de evento consumidos pela projeção devem existir no AsyncAPI."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    events_doc = ctx.contracts.get("05_ATLETAS_EVENTS.asyncapi.yaml") or {}

    # Coletar tipos de evento declarados
    channels = events_doc.get("channels") or {}
    declared_events: set[str] = set()
    for ch in channels.values():
        payload = (ch.get("publish") or ch.get("subscribe") or {})
        msg = payload.get("message") or {}
        name = msg.get("name")
        if name:
            declared_events.add(name)

    errors = []
    for rm in (projections_doc.get("read_models") or []):
        for handler in (rm.get("event_handlers") or []):
            event_type = handler.get("event_type")
            if event_type and declared_events and event_type not in declared_events:
                errors.append(f"Tipo de evento '{event_type}' não declarado no AsyncAPI")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_consumed_versions_are_explicit(rule: dict, ctx) -> RuleResult:
    """PROJ-002 (PRE_PLAN): Versões de evento consumidas devem ser listadas explicitamente."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    errors = []

    for rm in (projections_doc.get("read_models") or []):
        for handler in (rm.get("event_handlers") or []):
            versions = handler.get("supported_versions") or handler.get("event_version")
            if not versions:
                errors.append(
                    f"Handler '{handler.get('handler_symbol', '?')}' não declara versão(ões) explícitas de evento"
                )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_new_event_versions_require_compatibility_strategy(rule: dict, ctx) -> RuleResult:
    """PROJ-003 (PRE_PLAN): Novas versões de evento requerem estratégia de compatibilidade."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    upcast_pipeline = projections_doc.get("upcast_pipeline")
    upcast_list = upcast_pipeline if isinstance(upcast_pipeline, list) else []

    if not upcast_list:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Nenhum upcast_pipeline como lista declarado")

    errors = []
    for entry in upcast_list:
        if not isinstance(entry, dict):
            continue
        from_v = entry.get("from_version")
        to_v = entry.get("to_version")
        upcaster = entry.get("upcaster_symbol") or entry.get("upcaster")
        if not from_v or not to_v:
            errors.append(f"Entrada do upcast_pipeline sem from_version/to_version: {entry}")
        if not upcaster:
            errors.append(f"Entrada de upcaster '{from_v}->{to_v}' sem símbolo de upcaster declarado")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_handlers_are_side_effect_free(rule: dict, ctx) -> RuleResult:
    """PROJ-005 (POST_EXECUTION): Handlers de projeção devem ser side-effect-free."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}

    _FORBIDDEN = ["requests.", "httpx.", "smtplib.", "boto3.", "kafka", "pika.", "celery"]

    errors = []
    for rm in (projections_doc.get("read_models") or []):
        target_file = rm.get("target_file")
        if not target_file:
            continue
        fp = ctx.repo_root / target_file
        if not fp.exists():
            continue

        source = fp.read_text(encoding="utf-8", errors="replace")
        for handler in (rm.get("event_handlers") or []):
            symbol = handler.get("handler_symbol", "")
            # Encontrar corpo da função
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
                    fn_src = source.splitlines()
                    start = node.lineno - 1
                    end = getattr(node, "end_lineno", start + 50)
                    body = "\n".join(fn_src[start:end])
                    for forbidden in _FORBIDDEN:
                        if forbidden in body:
                            errors.append(f"Handler '{symbol}' usa '{forbidden}' (side effect proibido)")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_atomic_shell_integrity(rule: dict, ctx) -> RuleResult:
    """PROJ-006 (POST_EXECUTION, cannot_waive): Handlers devem preservar transaction_scope, guarda de idempotência e ledger mark."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}
    violations = []

    for rm in (projections_doc.get("read_models") or []):
        target_file = rm.get("target_file")
        if not target_file:
            continue

        fp = ctx.repo_root / target_file
        if not fp.exists():
            # Arquivo não existe ainda — POST_EXECUTION, skip gracioso
            continue

        try:
            source = fp.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(fp))
        except (OSError, SyntaxError) as exc:
            violations.append({"file": str(fp), "reason": f"parse_error: {exc}"})
            continue

        for handler in (rm.get("event_handlers") or []):
            symbol = handler.get("handler_symbol")
            if not symbol:
                continue

            visitor = ProjectionAtomicShellVisitor(symbol)
            visitor.visit(tree)
            visitor.finalize()

            if not visitor.function_found:
                violations.append({"file": str(fp), "handler_symbol": symbol, "reason": "handler_not_found"})
                continue

            for v in visitor.violations:
                v["file"] = str(fp)
                v["handler_symbol"] = symbol
                violations.append(v)

    if violations:
        msgs = [f"{v.get('file', '?')}:{v.get('handler_symbol', '?')} → {v.get('reason') or v.get('kind', '?')}" for v in violations]
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], " | ".join(msgs))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_handlers_forbid_nested_transactions(rule: dict, ctx) -> RuleResult:
    """PROJ-007 (POST_EXECUTION): Handlers não podem abrir transações aninhadas."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}

    _NESTED_TX_PATTERNS = ["begin_transaction", "start_transaction", "db.begin(", "session.begin(", "conn.begin("]

    errors = []
    for rm in (projections_doc.get("read_models") or []):
        target_file = rm.get("target_file")
        if not target_file:
            continue
        fp = ctx.repo_root / target_file
        if not fp.exists():
            continue

        source = fp.read_text(encoding="utf-8", errors="replace")
        for pattern in _NESTED_TX_PATTERNS:
            if pattern in source:
                errors.append(f"'{target_file}' contém padrão de transação aninhada proibida: '{pattern}'")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_tables_are_write_protected(rule: dict, ctx) -> RuleResult:
    """PROJ-008 (POST_EXECUTION): Tabelas de projeção não devem ser escritas fora dos handlers declarados."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}

    projection_tables: set[str] = set()
    for rm in (projections_doc.get("read_models") or []):
        tbl = rm.get("target_table") or rm.get("table_name")
        if tbl:
            projection_tables.add(tbl)

    if not projection_tables:
        return RuleResult.skip(rule["rule_id"], rule["checker_id"], "Nenhuma tabela de projeção declarada")

    # Verificar arquivos de serviço (não-projeção) que escrevem nas tabelas de projeção
    service_dirs = [
        ctx.repo_root / "Hb Track - Backend" / "app" / "services",
        ctx.repo_root / "Hb Track - Backend" / "app" / "routers",
    ]

    errors = []
    for sdir in service_dirs:
        if not sdir.exists():
            continue
        for py_file in sdir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8", errors="replace")
            for tbl in projection_tables:
                # Heurística: INSERT INTO <table> fora de handler de projeção
                if f'"{tbl}"' in source or f"'{tbl}'" in source or tbl in source:
                    if "transaction_scope" not in source:
                        errors.append(
                            f"'{py_file.name}' pode estar escrevendo diretamente na tabela de projeção '{tbl}'"
                        )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_idempotency_ledger_is_declared(rule: dict, ctx) -> RuleResult:
    """PROJ-009 (PRE_PLAN): Contrato de projeção deve declarar ledger de idempotência."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}

    errors = []
    for rm in (projections_doc.get("read_models") or []):
        rm_id = rm.get("read_model_id", "?")
        ledger = rm.get("idempotency_ledger") or rm.get("ledger") or rm.get("uniqueness_key")
        if not ledger:
            errors.append(f"Read model '{rm_id}' não declara idempotency_ledger ou uniqueness_key")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_projection_accumulator_fields_declare_sequencing_dependency(rule: dict, ctx) -> RuleResult:
    """PROJ-010 (PRE_PLAN, cannot_waive): Campos acumuladores em read models devem declarar ordering_key, accumulation_semantics e replay_consistency_policy."""
    projections_doc = ctx.contracts.get("17_ATLETAS_PROJECTIONS.yaml") or {}

    REQUIRED_KEYS = ["ordering_key", "accumulation_semantics", "replay_consistency_policy"]
    ACCUMULATOR_INDICATORS = {"is_accumulator", "source_type"}

    errors = []
    for rm in (projections_doc.get("read_models") or []):
        rm_id = rm.get("read_model_id", "?")
        fields = rm.get("fields") or []

        for field in fields:
            field_name = field.get("name") or field.get("field_name", "?")

            # Identificar campo acumulador
            is_acc = field.get("is_accumulator") or field.get("source_type") in {"accumulator", "sum", "count", "average", "rolling"}
            if not is_acc:
                continue

            missing = [k for k in REQUIRED_KEYS if not field.get(k)]
            if missing:
                errors.append(
                    f"Read model '{rm_id}', campo acumulador '{field_name}': "
                    f"faltam chaves obrigatórias: {', '.join(missing)}"
                )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# PROJ-004: check_new_event_versions_require_compatibility_strategy — já implementado como PROJ-003 alias
# Na constituição, PROJ-004 é checker_id diferente; criar separado:

def check_projection_consumed_versions_are_explicit_proj4(rule: dict, ctx) -> RuleResult:
    """PROJ-004 duplicate alias via constitution checker_id mapping — delegates to PROJ-003 logic."""
    return check_new_event_versions_require_compatibility_strategy(rule, ctx)


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_projection_event_types_exist", check_projection_event_types_exist)
register_checker("check_projection_consumed_versions_are_explicit", check_projection_consumed_versions_are_explicit)
register_checker("check_new_event_versions_require_compatibility_strategy", check_new_event_versions_require_compatibility_strategy)
register_checker("check_projection_handlers_are_side_effect_free", check_projection_handlers_are_side_effect_free)
register_checker("check_projection_atomic_shell_integrity", check_projection_atomic_shell_integrity)
register_checker("check_projection_handlers_forbid_nested_transactions", check_projection_handlers_forbid_nested_transactions)
register_checker("check_projection_tables_are_write_protected", check_projection_tables_are_write_protected)
register_checker("check_projection_idempotency_ledger_is_declared", check_projection_idempotency_ledger_is_declared)
register_checker("check_projection_accumulator_fields_declare_sequencing_dependency", check_projection_accumulator_fields_declare_sequencing_dependency)
