"""
Check 13: Root cause classification.

Selects the first failing check's root_cause_candidate by canonical precedence order
defined in DIAGNOSTIC_CONNECTIVITY_CONTRACT.yaml §diagnostic_execution_order.
First structural blocker in the chain dominates; later failures become secondary evidence.
"""
from __future__ import annotations

from typing import List, Tuple

from tools.diagnostics.models.check_result import CheckResult

# Canonical precedence order — do NOT reorder without updating the YAML contract
ROOT_CAUSE_PRECEDENCE: List[str] = [
    "FRONTEND_API_URL_MISSING",
    "FRONTEND_API_URL_INVALID",
    "FRONTEND_API_URL_LOCALHOST_MISUSE",
    "API_URL_PARSE_ERROR",
    "API_HOST_UNRESOLVED",
    "API_PORT_CLOSED",
    "API_TCP_TIMEOUT",
    "TLS_CERT_INVALID",
    "TLS_HOSTNAME_MISMATCH",
    "TLS_HANDSHAKE_FAILED",
    "API_HTTP_UNREACHABLE",
    "API_HTTP_TIMEOUT",
    "API_HEALTH_ENDPOINT_MISSING",
    "API_UNEXPECTED_REDIRECT",
    "MIXED_CONTENT_RISK",
    "CORS_BLOCKING_ORIGIN",
    "CORS_METHOD_NOT_ALLOWED",
    "CORS_HEADERS_NOT_ALLOWED",
    "HEALTH_RESPONSE_INVALID",
    "HEALTH_SCHEMA_INVALID",
    "BACKEND_NOT_READY",
    "DATABASE_DOWN",
    "DATABASE_DEGRADED",
    "API_RETURNED_500",
    "UNKNOWN_FAILURE",
]

# Errors where the input/config itself is absent or unparseable → BLOCKED_INPUT (exit 4)
_BLOCKED_INPUT_CAUSES = frozenset({
    "FRONTEND_API_URL_MISSING",
    "FRONTEND_API_URL_INVALID",
    "API_URL_PARSE_ERROR",
})


def classify_root_cause(checks: List[CheckResult]) -> Tuple[str, int]:
    """
    Check 13: Select the dominant root cause and its exit code.
    Returns (root_cause_code, exit_code).
    """
    candidate_set: set = set()
    for chk in checks:
        if chk.status == "fail" and chk.root_cause_candidate:
            candidate_set.add(chk.root_cause_candidate)

    if not candidate_set:
        return "PASS", 0

    for code in ROOT_CAUSE_PRECEDENCE:
        if code in candidate_set:
            return code, _map_exit_code(code)

    # Fallback — should not be reached if all codes are in precedence list
    return "UNKNOWN_FAILURE", 3


def _map_exit_code(code: str) -> int:
    """Map a root_cause_code to its canonical exit code."""
    if code == "PASS":
        return 0
    if code in _BLOCKED_INPUT_CAUSES:
        return 4  # BLOCKED_INPUT
    if code == "UNKNOWN_FAILURE":
        return 3  # ERROR_INFRA
    return 2  # FAIL_ACTIONABLE
