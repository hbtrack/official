"""
Check 9: CORS preflight simulation.
Simulates what the browser sends before a cross-origin GET request.
Fail codes: CORS_BLOCKING_ORIGIN, CORS_METHOD_NOT_ALLOWED, CORS_HEADERS_NOT_ALLOWED
"""
from __future__ import annotations

from urllib.parse import urlparse

import requests

from tools.diagnostics.models.check_result import CheckResult


def check_cors_preflight(
    api_base_url: str,
    frontend_origin: str,
    health_path: str,
    timeout: int = 8,
    verify_tls: bool = False,
) -> CheckResult:
    """
    Check 9: Simulate OPTIONS preflight for the local frontend origin.
    """
    parsed = urlparse(api_base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    full_url = base + health_path

    headers = {
        "Origin": frontend_origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type",
    }

    try:
        resp = requests.options(
            full_url,
            headers=headers,
            timeout=timeout,
            verify=verify_tls,
        )

        allow_origin = resp.headers.get("Access-Control-Allow-Origin", "")
        allow_methods = resp.headers.get("Access-Control-Allow-Methods", "")
        allow_headers = resp.headers.get("Access-Control-Allow-Headers", "")

        # Determine if origin is allowed
        origin_allowed = (
            allow_origin == "*"
            or allow_origin == frontend_origin
            or frontend_origin in allow_origin
        )

        if not origin_allowed:
            return CheckResult(
                name="cors_preflight",
                status="fail",
                evidence={
                    "url": full_url,
                    "request_origin": frontend_origin,
                    "response_allow_origin": allow_origin or "(not set)",
                    "status_code": resp.status_code,
                },
                root_cause_candidate="CORS_BLOCKING_ORIGIN",
            )

        # Check methods
        if (
            allow_methods
            and allow_methods != "*"
            and "GET" not in allow_methods.upper()
        ):
            return CheckResult(
                name="cors_preflight",
                status="fail",
                evidence={
                    "url": full_url,
                    "request_origin": frontend_origin,
                    "response_allow_methods": allow_methods,
                },
                root_cause_candidate="CORS_METHOD_NOT_ALLOWED",
            )

        return CheckResult(
            name="cors_preflight",
            status="pass",
            evidence={
                "url": full_url,
                "request_origin": frontend_origin,
                "response_allow_origin": allow_origin,
                "response_allow_methods": allow_methods,
                "status_code": resp.status_code,
            },
        )

    except requests.Timeout:
        return CheckResult(
            name="cors_preflight",
            status="fail",
            evidence=f"OPTIONS {full_url} timed out",
            root_cause_candidate="API_HTTP_TIMEOUT",
        )
    except requests.ConnectionError as exc:
        return CheckResult(
            name="cors_preflight",
            status="fail",
            evidence=f"OPTIONS {full_url} connection error: {exc}",
            root_cause_candidate="API_HTTP_UNREACHABLE",
        )
