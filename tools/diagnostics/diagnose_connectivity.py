#!/usr/bin/env python3
"""
diagnose_connectivity.py — CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0

Executes all connectivity checks in canonical order and produces a structured
diagnostic report with root cause classification and recommended action.

Usage:
    python tools/diagnostics/diagnose_connectivity.py
    python tools/diagnostics/diagnose_connectivity.py --json-only
    python tools/diagnostics/diagnose_connectivity.py --api-url http://... --origin http://...
    python tools/diagnostics/diagnose_connectivity.py --no-report

Exit codes:
    0 = PASS
    2 = FAIL_ACTIONABLE  (correctable by config / CORS / URL / readiness / dependency)
    3 = ERROR_INFRA      (internal script failure)
    4 = BLOCKED_INPUT    (missing or unparseable required input)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import traceback
from typing import List, Optional
from urllib.parse import urlparse

# ── Ensure workspace root is on sys.path ─────────────────────────────────────
_HERE = pathlib.Path(__file__).parent            # tools/diagnostics/
_WORKSPACE_ROOT = _HERE.parent.parent            # repo root
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

# ── Internal imports ─────────────────────────────────────────────────────────
from tools.diagnostics import config as _cfg
from tools.diagnostics.models.check_result import CheckResult
from tools.diagnostics.models.diagnostic_result import DiagnosticResult
from tools.diagnostics.checks.check_frontend_config import (
    check_frontend_api_url,
    check_frontend_api_url_topology,
    check_api_url_parse,
)
from tools.diagnostics.checks.check_dns import check_dns_resolution
from tools.diagnostics.checks.check_tcp import check_tcp_connectivity
from tools.diagnostics.checks.check_tls import check_tls
from tools.diagnostics.checks.check_http import check_http_health
from tools.diagnostics.checks.check_protocol_coherence import check_protocol_coherence
from tools.diagnostics.checks.check_cors import check_cors_preflight
from tools.diagnostics.checks.check_health import check_health_schema, check_backend_dependencies
from tools.diagnostics.checks.check_ready import check_readiness
from tools.diagnostics.checks.classify_root_cause import classify_root_cause
from tools.diagnostics.reporters.write_json_report import write_json_report
from tools.diagnostics.reporters.write_md_report import write_md_report

# ── Recommended actions per root_cause_code ──────────────────────────────────
_RECOMMENDED_ACTIONS: dict = {
    "PASS": (
        "No action needed — all checks passed."
    ),
    "FRONTEND_API_URL_MISSING": (
        "Define NEXT_PUBLIC_API_URL in 'Hb Track - Frontend/.env.local' "
        "pointing to the public API URL (e.g., http://191.252.185.34/api/v1)."
    ),
    "FRONTEND_API_URL_INVALID": (
        "Fix NEXT_PUBLIC_API_URL — it must be a valid http(s)://host/path URL."
    ),
    "FRONTEND_API_URL_LOCALHOST_MISUSE": (
        "Change NEXT_PUBLIC_API_URL from localhost to the public API URL: "
        "NEXT_PUBLIC_API_URL=http://191.252.185.34/api/v1 "
        "The browser resolves 'localhost' as the user's own machine, not the VPS."
    ),
    "API_URL_PARSE_ERROR": (
        "Verify DIAG_API_BASE_URL (or default) is a valid http(s)://host URL."
    ),
    "API_HOST_UNRESOLVED": (
        "Verify DNS for the API host is correct and the domain is registered/propagated."
    ),
    "API_PORT_CLOSED": (
        "Verify Nginx is running on the VPS (sudo systemctl status nginx) "
        "and port 80 is open in UFW (sudo ufw status)."
    ),
    "API_TCP_TIMEOUT": (
        "Verify network route to the VPS and firewall rules. "
        "Run: curl -v --connect-timeout 10 http://191.252.185.34/api/v1/health"
    ),
    "TLS_CERT_INVALID": (
        "Renew or fix the TLS certificate. "
        "Check with: openssl s_client -connect host:443"
    ),
    "TLS_HOSTNAME_MISMATCH": (
        "Ensure the certificate's CN/SAN matches the API hostname."
    ),
    "TLS_HANDSHAKE_FAILED": (
        "Investigate TLS configuration in Nginx: nginx -t && journalctl -u nginx"
    ),
    "MIXED_CONTENT_RISK": (
        "Either serve the frontend over HTTP (development) or upgrade the API to HTTPS. "
        "Browsers block HTTPS pages loading HTTP resources."
    ),
    "API_HTTP_UNREACHABLE": (
        "Check if Nginx is running and proxying: "
        "sudo systemctl status nginx; sudo journalctl -u hbtrack-backend -n 50"
    ),
    "API_HTTP_TIMEOUT": (
        "Increase timeout or investigate backend/Nginx latency."
    ),
    "API_HEALTH_ENDPOINT_MISSING": (
        "Ensure GET /api/v1/health is registered in the backend and the "
        "application is deployed and running."
    ),
    "API_UNEXPECTED_REDIRECT": (
        "Investigate Nginx redirect rules. "
        "Run: curl -v http://191.252.185.34/api/v1/health"
    ),
    "API_RETURNED_500": (
        "Check backend logs: sudo journalctl -u hbtrack-backend -n 100 --no-pager"
    ),
    "CORS_BLOCKING_ORIGIN": (
        "Add http://localhost:3000 to CORS_ORIGINS in the backend .env on the VPS. "
        "Current allowed: http://191.252.185.34,https://hbtracking.com. "
        "Fix: CORS_ORIGINS=http://191.252.185.34,https://hbtracking.com,http://localhost:3000 "
        "Then: sudo systemctl restart hbtrack-backend"
    ),
    "CORS_METHOD_NOT_ALLOWED": (
        "Add GET to CORS_ALLOW_METHODS in the backend configuration."
    ),
    "CORS_HEADERS_NOT_ALLOWED": (
        "Add required headers (e.g., Authorization, Content-Type) "
        "to CORS_ALLOW_HEADERS in the backend configuration."
    ),
    "HEALTH_RESPONSE_INVALID": (
        "GET /api/v1/health returned non-JSON. Check backend logs for startup errors."
    ),
    "HEALTH_SCHEMA_INVALID": (
        "Update /api/v1/health to return an object with at least 'status' and 'database' fields."
    ),
    "BACKEND_NOT_READY": (
        "GET /api/v1/health/readiness returned 503. Database may be unavailable. "
        "Run: sudo systemctl status postgresql; sudo journalctl -u hbtrack-backend -n 50"
    ),
    "DATABASE_DOWN": (
        "Health reports database unavailable. Verify PostgreSQL: "
        "sudo systemctl status postgresql. "
        "Check DATABASE_URL in /home/deploy/hbtrack-backend/.env"
    ),
    "DATABASE_DEGRADED": (
        "Health reports database degraded. Monitor and investigate connection pool usage."
    ),
    "UNKNOWN_FAILURE": (
        "Unclassified failure — inspect all check evidence in the diagnostic report."
    ),
    "BLOCKED_INPUT": (
        "Provide required configuration inputs to the diagnostic script."
    ),
    "ERROR_INFRA": (
        "Internal error in the diagnostic script. Inspect the traceback evidence."
    ),
}

# ── Root cause summaries ──────────────────────────────────────────────────────
_ROOT_CAUSE_SUMMARIES: dict = {
    "PASS": "All checks passed — no connectivity issue detected.",
    "FRONTEND_API_URL_MISSING": "NEXT_PUBLIC_API_URL is not defined in the frontend environment.",
    "FRONTEND_API_URL_INVALID": "NEXT_PUBLIC_API_URL contains a syntactically invalid URL.",
    "FRONTEND_API_URL_LOCALHOST_MISUSE": (
        "NEXT_PUBLIC_API_URL points to localhost but the backend is remote. "
        "The browser will route requests to the user's own machine, not the VPS."
    ),
    "API_URL_PARSE_ERROR": "The target API URL cannot be parsed into scheme/host/port.",
    "API_HOST_UNRESOLVED": "DNS resolution failed for the API host.",
    "API_PORT_CLOSED": "The API port is closed or refused connection.",
    "API_TCP_TIMEOUT": "TCP connection to the API host timed out.",
    "TLS_CERT_INVALID": "TLS certificate is invalid or not trusted.",
    "TLS_HOSTNAME_MISMATCH": "TLS certificate hostname does not match the API host.",
    "TLS_HANDSHAKE_FAILED": "TLS handshake failed.",
    "MIXED_CONTENT_RISK": "Frontend (HTTPS) is configured to call an HTTP API — browsers will block this.",
    "API_HTTP_UNREACHABLE": "API did not respond to HTTP request — connection refused or network error.",
    "API_HTTP_TIMEOUT": "HTTP request to the API health endpoint timed out.",
    "API_HEALTH_ENDPOINT_MISSING": "GET /api/v1/health returned 404 — endpoint not deployed.",
    "API_UNEXPECTED_REDIRECT": "API health endpoint responded with an unexpected HTTP redirect.",
    "API_RETURNED_500": "API health endpoint returned a 5xx server error.",
    "CORS_BLOCKING_ORIGIN": (
        "API is reachable but its CORS policy does not permit the local frontend origin."
    ),
    "CORS_METHOD_NOT_ALLOWED": "CORS policy does not allow the required HTTP method.",
    "CORS_HEADERS_NOT_ALLOWED": "CORS policy does not allow the required request headers.",
    "HEALTH_RESPONSE_INVALID": "GET /api/v1/health did not return valid JSON.",
    "HEALTH_SCHEMA_INVALID": "GET /api/v1/health response is missing required fields.",
    "BACKEND_NOT_READY": "GET /api/v1/health/readiness returned 503 — backend not ready for traffic.",
    "DATABASE_DOWN": "API is accessible but /api/v1/health declares the database unavailable.",
    "DATABASE_DEGRADED": "API is accessible but /api/v1/health declares the database degraded.",
    "UNKNOWN_FAILURE": "Unclassified failure — inspect all check evidence.",
}


def _is_remote_target(api_base_url: str) -> bool:
    """Return True if the API host is not localhost/loopback."""
    host = urlparse(api_base_url).hostname or ""
    return host not in ("localhost", "127.0.0.1", "::1", "")


def run_diagnostic(
    api_base_url: str,
    frontend_origin: str,
    health_path: str,
    readiness_path: str,
    env_var_names: list,
    env_file: str,
    timeout: int,
    verify_tls: bool,
) -> DiagnosticResult:
    """
    Execute all checks in canonical order and return a DiagnosticResult.
    First structural blocker in the chain dominates the root cause.
    """
    checks: List[CheckResult] = []
    inputs = {
        "api_base_url": api_base_url,
        "frontend_origin": frontend_origin,
        "health_path": health_path,
        "readiness_path": readiness_path,
        "env_var_names": env_var_names,
        "env_file": env_file,
        "timeout_seconds": timeout,
        "verify_tls": verify_tls,
    }

    # ── Check 1: frontend_api_url_discovery ──────────────────────────────────
    c1, frontend_url = check_frontend_api_url(env_var_names, env_file)
    checks.append(c1)
    if c1.status == "fail":
        return _finalize(checks, inputs)

    # ── Check 2: frontend_api_url_topology_check ─────────────────────────────
    is_remote = _is_remote_target(api_base_url)
    c2 = check_frontend_api_url_topology(frontend_url, is_remote)  # type: ignore[arg-type]
    checks.append(c2)
    if c2.status == "fail":
        # LOCALHOST_MISUSE is a logical blocker — no point testing remote API
        return _finalize(checks, inputs)

    # ── Check 3: api_url_parse ────────────────────────────────────────────────
    c3, parsed_url = check_api_url_parse(api_base_url)
    checks.append(c3)
    if c3.status == "fail":
        return _finalize(checks, inputs)

    assert parsed_url is not None  # guaranteed by status=="pass" path above

    # ── Check 4: dns_resolution ──────────────────────────────────────────────
    c4 = check_dns_resolution(parsed_url["host"])
    checks.append(c4)
    if c4.status == "fail":
        return _finalize(checks, inputs)

    # ── Check 5: tcp_connectivity ─────────────────────────────────────────────
    c5 = check_tcp_connectivity(parsed_url["host"], parsed_url["port"], timeout)
    checks.append(c5)
    if c5.status == "fail":
        return _finalize(checks, inputs)

    # ── Check 6: tls_validation (https only) ─────────────────────────────────
    if parsed_url["scheme"] == "https":
        c6 = check_tls(parsed_url["host"], parsed_url["port"], timeout)
        checks.append(c6)
        if c6.status == "fail":
            return _finalize(checks, inputs)
    else:
        checks.append(CheckResult(
            name="tls_validation",
            status="skip",
            evidence="Skipped: scheme is http",
        ))

    # ── Check 7: http_health_reachability ─────────────────────────────────────
    c7 = check_http_health(api_base_url, health_path, timeout, verify_tls)
    checks.append(c7)
    if c7.status == "fail":
        return _finalize(checks, inputs)

    # ── Check 8: protocol_coherence ───────────────────────────────────────────
    c8 = check_protocol_coherence(frontend_origin, api_base_url)
    checks.append(c8)
    # Mixed content is a browser-level block — record but continue gathering evidence

    # ── Check 9: cors_preflight ───────────────────────────────────────────────
    c9 = check_cors_preflight(api_base_url, frontend_origin, health_path, timeout, verify_tls)
    checks.append(c9)
    # CORS failure is recorded; continue to gather health/readiness evidence

    # ── Check 10: backend_health_schema ──────────────────────────────────────
    c10, health_body = check_health_schema(api_base_url, health_path, timeout, verify_tls)
    checks.append(c10)
    if c10.status == "fail":
        return _finalize(checks, inputs)

    # ── Check 11: backend_readiness ──────────────────────────────────────────
    c11 = check_readiness(api_base_url, readiness_path, timeout, verify_tls)
    checks.append(c11)

    # ── Check 12: backend_dependency_inference ────────────────────────────────
    if health_body:
        c12 = check_backend_dependencies(health_body)
        checks.append(c12)
    else:
        checks.append(CheckResult(
            name="backend_dependency_inference",
            status="skip",
            evidence="Skipped: no valid health body available",
        ))

    # ── Check 13: root_cause_classification ──────────────────────────────────
    return _finalize(checks, inputs)


def _finalize(checks: List[CheckResult], inputs: dict) -> DiagnosticResult:
    root_cause_code, exit_code = classify_root_cause(checks)
    status = "pass" if root_cause_code == "PASS" else "fail"
    summary = _ROOT_CAUSE_SUMMARIES.get(root_cause_code, root_cause_code)
    recommended_action = _RECOMMENDED_ACTIONS.get(
        root_cause_code, "Investigate diagnostic evidence."
    )
    return DiagnosticResult(
        status=status,
        exit_code=exit_code,
        root_cause_code=root_cause_code,
        root_cause_summary=summary,
        checks=checks,
        inputs=inputs,
        recommended_action=recommended_action,
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--api-url", default=None, help="Override API base URL")
    p.add_argument("--origin", default=None, help="Override frontend origin (e.g. http://localhost:3000)")
    p.add_argument("--env-file", default=None, help="Override path to frontend .env file")
    p.add_argument("--timeout", type=int, default=None, help="Override HTTP timeout (seconds)")
    p.add_argument(
        "--json-only",
        action="store_true",
        help="Print JSON report to stdout only; suppress prose output",
    )
    p.add_argument(
        "--no-report",
        action="store_true",
        help="Skip writing report files to _reports/",
    )
    return p


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    api_base_url = args.api_url or _cfg.API_BASE_URL
    frontend_origin = args.origin or _cfg.FRONTEND_ORIGIN
    env_file = args.env_file or _cfg.ENV_FILE
    timeout = args.timeout or _cfg.TIMEOUT_SECONDS

    try:
        result = run_diagnostic(
            api_base_url=api_base_url,
            frontend_origin=frontend_origin,
            health_path=_cfg.HEALTH_PATH,
            readiness_path=_cfg.READINESS_PATH,
            env_var_names=_cfg.FRONTEND_ENV_VAR_NAMES,
            env_file=env_file,
            timeout=timeout,
            verify_tls=_cfg.VERIFY_TLS,
        )
    except Exception as exc:
        result = DiagnosticResult(
            status="fail",
            exit_code=_cfg.EXIT_ERROR_INFRA,
            root_cause_code="ERROR_INFRA",
            root_cause_summary=f"Internal diagnostic script error: {exc}",
            checks=[
                CheckResult(
                    name="script_execution",
                    status="fail",
                    evidence=traceback.format_exc(),
                )
            ],
            inputs={"api_base_url": api_base_url, "frontend_origin": frontend_origin},
            recommended_action=_RECOMMENDED_ACTIONS["ERROR_INFRA"],
        )

    if not args.no_report:
        write_json_report(result, _cfg.REPORT_JSON_PATH)
        if _cfg.REPORT_MARKDOWN:
            write_md_report(result, _cfg.REPORT_MD_PATH)

    sys.stdout.buffer.write(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=True).encode("ascii") + b"\n"
    )

    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
