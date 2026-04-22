"""
Motor de despacho de regras — RuleResult e run_rule.

SSOT: docs/hbtrack/modulos/atletas/MOTORES.md
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class RuleResult:
    rule_id: str
    checker_id: str
    status: str      # "PASS" | "FAIL" | "ERROR" | "SKIP"
    message: str = ""

    @classmethod
    def pass_(cls, rule_id: str, checker_id: str, message: str = "") -> "RuleResult":
        return cls(rule_id=rule_id, checker_id=checker_id, status="PASS", message=message)

    @classmethod
    def fail(cls, rule_id: str, checker_id: str, message: str) -> "RuleResult":
        return cls(rule_id=rule_id, checker_id=checker_id, status="FAIL", message=message)

    @classmethod
    def error(cls, rule_id: str, checker_id: str, message: str) -> "RuleResult":
        return cls(rule_id=rule_id, checker_id=checker_id, status="ERROR", message=message)

    @classmethod
    def skip(cls, rule_id: str, checker_id: str, message: str = "") -> "RuleResult":
        return cls(rule_id=rule_id, checker_id=checker_id, status="SKIP", message=message)


# Registro global de checkers: checker_id -> função
_CHECKERS: dict[str, Callable] = {}


def register_checker(checker_id: str, fn: Callable) -> None:
    _CHECKERS[checker_id] = fn


def clear_registry() -> None:
    """Remove todos os checkers. Usar APENAS em testes."""
    _CHECKERS.clear()


def get_checkers() -> dict[str, Callable]:
    return _CHECKERS


def run_rule(rule: dict, context) -> RuleResult:
    """Despacha a regra para o checker registrado pelo checker_id."""
    checker_id = rule.get("checker_id", "")
    rule_id = rule.get("rule_id", checker_id)

    fn = _CHECKERS.get(checker_id)
    if fn is None:
        return RuleResult.skip(rule_id, checker_id, f"Checker não implementado: {checker_id}")

    try:
        return fn(rule, context)
    except Exception as exc:
        return RuleResult.error(rule_id, checker_id, f"{type(exc).__name__}: {exc}")


# ─── Governance v2 ────────────────────────────────────────────────────────────

# Constantes de status v2 (mantém legado STATUS_FAIL / STATUS_ERROR por retrocompat)
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"                      # legado, mantido por retrocompat
STATUS_FAIL_ACTIONABLE = "FAIL_ACTIONABLE"
STATUS_ERROR = "ERROR"                    # legado, mantido
STATUS_ERROR_INFRA = "ERROR_INFRA"
STATUS_BLOCKED_INPUT = "BLOCKED_INPUT"
STATUS_SKIP = "SKIP"
STATUS_WARNING = "WARNING"
STATUS_INFO = "INFO"

VALID_STATUSES_V2 = frozenset([
    STATUS_PASS, STATUS_FAIL_ACTIONABLE, STATUS_ERROR_INFRA,
    STATUS_BLOCKED_INPUT, STATUS_SKIP, STATUS_WARNING, STATUS_INFO,
])

_FAIL_STATUSES = frozenset([
    STATUS_FAIL, STATUS_FAIL_ACTIONABLE,
    STATUS_ERROR, STATUS_ERROR_INFRA, STATUS_BLOCKED_INPUT,
])


def aggregate_results(results):
    """Agrega lista de RuleResult. Fail-closed: qualquer FAIL*/ERROR* = FAIL.

    Retorna:
        {
            "total":     int,
            "counts":    dict[str, int],
            "overall":   "PASS" | "FAIL",
            "exit_code": 0 if overall == "PASS" else 1,
        }
    """
    from collections import Counter
    counts = Counter(r.status for r in results)
    has_failure = any(r.status in _FAIL_STATUSES for r in results)
    overall = "FAIL" if has_failure else "PASS"
    return {
        "total": len(results),
        "counts": dict(counts),
        "overall": overall,
        "exit_code": 0 if overall == "PASS" else 1,
    }
