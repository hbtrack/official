"""
Checkers de determinismo temporal — TIME-002, TIME-003.

cannot_waive: TIME-002
"""
from __future__ import annotations

import ast
from pathlib import Path

from hbtrack_lint.engine import register_checker, RuleResult

# Padrões de uso proibido de clock do sistema
_FORBIDDEN_CLOCK_PATTERNS = [
    "datetime.now",
    "date.today",
    "time.time",
    "datetime.utcnow",
    "arrow.now",
    "arrow.utcnow",
    "pendulum.now",
    "pendulum.today",
]

# Arquivos de invariants que devem ser verificados
_INVARIANT_FILES = [
    "Hb Track - Backend/app/core/athlete_validations.py",
    "Hb Track - Backend/app/services/athlete_service.py",
    "Hb Track - Backend/app/services/athlete_service_v2.py",
]


def _has_system_clock_usage(source: str, tree: ast.AST) -> list[str]:
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            # Verificar padrões como datetime.now, date.today
            obj = getattr(node.value, "id", "") or getattr(node.value, "attr", "")
            attr = node.attr
            call_str = f"{obj}.{attr}"
            if call_str in _FORBIDDEN_CLOCK_PATTERNS:
                violations.append(f"L{node.lineno}: {call_str}")
    return violations


def check_temporal_invariants_forbid_system_clock(rule: dict, ctx) -> RuleResult:
    """TIME-002 (POST_EXECUTION, cannot_waive): datetime.now, date.today e system clock são proibidos em caminhos de invariants."""
    invariants_doc = ctx.contracts.get("15_ATLETAS_INVARIANTS.yaml") or {}

    # Identificar invariants temporais
    temporal_invs = []
    for inv in (invariants_doc.get("invariants") or []):
        predicate = inv.get("formal_predicate") or ""
        terms = inv.get("domain_terms") or []
        if any(kw in predicate.lower() for kw in ["year", "date", "birth", "nasc"]):
            temporal_invs.append(inv)

    if not temporal_invs:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Verificar arquivos de implementação
    errors = []
    for file_rel in _INVARIANT_FILES:
        impl_path = ctx.repo_root / file_rel
        if not impl_path.exists():
            continue

        source = impl_path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        violations = _has_system_clock_usage(source, tree)
        if violations:
            # Verificar se é em caminho de validação de invariant (heurística por nome de função)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_name = node.name.lower()
                    if any(kw in func_name for kw in ["validate", "check", "invariant", "category", "birth"]):
                        func_source = source.splitlines()
                        start = node.lineno - 1
                        end = node.end_lineno if hasattr(node, "end_lineno") else start + 20
                        func_body = "\n".join(func_source[start:end])
                        for pattern in _FORBIDDEN_CLOCK_PATTERNS:
                            if pattern in func_body:
                                errors.append(
                                    f"'{file_rel}' função '{node.name}': "
                                    f"uso de clock proibido '{pattern}' em caminho de invariant"
                                )

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


def check_frozen_time_enabled_for_temporal_scenarios(rule: dict, ctx) -> RuleResult:
    """TIME-003 (POST_EXECUTION): Cenários temporais devem usar frozen time."""
    test_scenarios = ctx.contracts.get("19_ATLETAS_TEST_SCENARIOS.yaml") or {}
    scenarios = test_scenarios.get("scenarios") or []

    temporal_scenarios = [
        s for s in scenarios
        if s.get("deterministic_time_required") or "time" in (s.get("category") or "").lower()
    ]

    if not temporal_scenarios:
        return RuleResult.pass_(rule["rule_id"], rule["checker_id"])

    # Verificar arquivos de teste
    test_dirs = [
        ctx.repo_root / "Hb Track - Backend" / "tests" / "athletes",
    ]

    errors = []
    for scenario in temporal_scenarios:
        scenario_id = scenario.get("scenario_id", "?")
        test_id = scenario.get("test_function") or scenario.get("test_id")
        if not test_id:
            continue

        found_frozen = False
        for test_dir in test_dirs:
            if not test_dir.exists():
                continue
            for test_file in test_dir.glob("*.py"):
                source = test_file.read_text(encoding="utf-8", errors="replace")
                if test_id in source:
                    if "freeze_time" in source or "freezegun" in source or "time_machine" in source:
                        found_frozen = True
                        break

        if not found_frozen and any(test_dir.exists() for test_dir in test_dirs):
            errors.append(f"Cenário temporal '{scenario_id}': frozen time não detectado no teste '{test_id}'")

    if errors:
        return RuleResult.fail(rule["rule_id"], rule["checker_id"], "; ".join(errors))
    return RuleResult.pass_(rule["rule_id"], rule["checker_id"])


# ─── Registro ─────────────────────────────────────────────────────────────

register_checker("check_temporal_invariants_forbid_system_clock", check_temporal_invariants_forbid_system_clock)
register_checker("check_frozen_time_enabled_for_temporal_scenarios", check_frozen_time_enabled_for_temporal_scenarios)
