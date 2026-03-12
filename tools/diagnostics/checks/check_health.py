"""
Checks 10 & 12: Backend health schema validation and dependency inference.

Check 10 — backend_health_schema
  Validates /api/v1/health JSON response against minimum required schema.
  Fail codes: HEALTH_RESPONSE_INVALID, HEALTH_SCHEMA_INVALID

Check 12 — backend_dependency_inference
  Infers dependency failures from what the health endpoint actually exposes.
  Today only bank status is inferable — no Redis/queue without explicit exposure.
  Fail codes: DATABASE_DOWN, DATABASE_DEGRADED
"""
from __future__ import annotations

from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

from tools.diagnostics.models.check_result import CheckResult

# Values that the current health endpoint reports as "unhealthy"
_DB_DOWN_VALUES = {"unhealthy", "fail", "down", "error"}
_DB_DEGRADED_VALUES = {"degraded", "warn", "warning"}


def check_health_schema(
    api_base_url: str,
    health_path: str,
    timeout: int = 8,
    verify_tls: bool = False,
) -> Tuple[CheckResult, Optional[dict]]:
    """
    Check 10: Fetch /api/v1/health and validate minimum schema.
    Returns (CheckResult, body_or_None).
    """
    parsed = urlparse(api_base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    full_url = base + health_path

    try:
        resp = requests.get(full_url, timeout=timeout, verify=verify_tls)

        try:
            body = resp.json()
        except Exception:
            return CheckResult(
                name="backend_health_schema",
                status="fail",
                evidence=f"GET {full_url} -> {resp.status_code} — response is not valid JSON",
                root_cause_candidate="HEALTH_RESPONSE_INVALID",
            ), None

        if not isinstance(body, dict):
            return CheckResult(
                name="backend_health_schema",
                status="fail",
                evidence=f"GET {full_url} — JSON root is not an object: {type(body).__name__}",
                root_cause_candidate="HEALTH_RESPONSE_INVALID",
            ), None

        # Minimum required fields: 'status' and 'database'
        if "status" not in body:
            return CheckResult(
                name="backend_health_schema",
                status="fail",
                evidence=f"Health response missing required field 'status'. Got keys: {list(body.keys())}",
                root_cause_candidate="HEALTH_SCHEMA_INVALID",
            ), None

        if "database" not in body:
            return CheckResult(
                name="backend_health_schema",
                status="fail",
                evidence=f"Health response missing required field 'database'. Got keys: {list(body.keys())}",
                root_cause_candidate="HEALTH_SCHEMA_INVALID",
            ), None

        db_info = body.get("database", {})
        db_status = (
            db_info.get("status", "unknown")
            if isinstance(db_info, dict)
            else str(db_info)
        )

        return CheckResult(
            name="backend_health_schema",
            status="pass",
            evidence={
                "url": full_url,
                "global_status": body.get("status"),
                "database_status": db_status,
            },
        ), body

    except requests.Timeout:
        return CheckResult(
            name="backend_health_schema",
            status="fail",
            evidence=f"GET {full_url} timed out",
            root_cause_candidate="API_HTTP_TIMEOUT",
        ), None
    except requests.ConnectionError as exc:
        return CheckResult(
            name="backend_health_schema",
            status="fail",
            evidence=f"GET {full_url} connection error: {exc}",
            root_cause_candidate="API_HTTP_UNREACHABLE",
        ), None


def check_backend_dependencies(health_body: dict) -> CheckResult:
    """
    Check 12: Infer dependency health from the health JSON.
    Restriction: only database is inferable today.
    Redis and queue are NOT inferred without explicit endpoint.
    """
    db = health_body.get("database", {})
    db_status = (
        db.get("status", "unknown").lower()
        if isinstance(db, dict)
        else str(db).lower()
    )

    if db_status in _DB_DOWN_VALUES:
        return CheckResult(
            name="backend_dependency_inference",
            status="fail",
            evidence={"database": db, "inferred_status": "down"},
            root_cause_candidate="DATABASE_DOWN",
        )

    if db_status in _DB_DEGRADED_VALUES:
        return CheckResult(
            name="backend_dependency_inference",
            status="fail",
            evidence={"database": db, "inferred_status": "degraded"},
            root_cause_candidate="DATABASE_DEGRADED",
        )

    return CheckResult(
        name="backend_dependency_inference",
        status="pass",
        evidence={
            "database_status": db_status,
            "note": "Redis/queue not monitored canonically — not inferred",
        },
    )
