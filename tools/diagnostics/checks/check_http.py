"""
Check 7: HTTP health reachability.
Fail codes: API_HTTP_UNREACHABLE, API_HTTP_TIMEOUT,
            API_HEALTH_ENDPOINT_MISSING, API_UNEXPECTED_REDIRECT,
            API_RETURNED_500
"""
from __future__ import annotations

from urllib.parse import urlparse

import requests

from tools.diagnostics.models.check_result import CheckResult


def check_http_health(
    api_base_url: str,
    health_path: str,
    timeout: int = 8,
    verify_tls: bool = False,
) -> CheckResult:
    """
    Check 7: Verify the API responds at the health endpoint.
    URL constructed as: scheme://netloc + health_path
    """
    parsed = urlparse(api_base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    full_url = base + health_path

    try:
        resp = requests.get(
            full_url,
            timeout=timeout,
            verify=verify_tls,
            allow_redirects=False,
        )

        if resp.is_redirect or resp.status_code in (301, 302, 307, 308):
            return CheckResult(
                name="http_health_reachability",
                status="fail",
                evidence=(
                    f"GET {full_url} returned unexpected redirect "
                    f"{resp.status_code} -> {resp.headers.get('Location', '')}"
                ),
                root_cause_candidate="API_UNEXPECTED_REDIRECT",
            )

        if resp.status_code == 404:
            return CheckResult(
                name="http_health_reachability",
                status="fail",
                evidence=f"GET {full_url} returned 404 — endpoint not found",
                root_cause_candidate="API_HEALTH_ENDPOINT_MISSING",
            )

        if resp.status_code >= 500:
            return CheckResult(
                name="http_health_reachability",
                status="fail",
                evidence=f"GET {full_url} returned {resp.status_code}",
                root_cause_candidate="API_RETURNED_500",
            )

        return CheckResult(
            name="http_health_reachability",
            status="pass",
            evidence=f"GET {full_url} -> {resp.status_code}",
        )

    except requests.Timeout:
        return CheckResult(
            name="http_health_reachability",
            status="fail",
            evidence=f"GET {full_url} timed out after {timeout}s",
            root_cause_candidate="API_HTTP_TIMEOUT",
        )
    except requests.ConnectionError as exc:
        return CheckResult(
            name="http_health_reachability",
            status="fail",
            evidence=f"GET {full_url} connection error: {exc}",
            root_cause_candidate="API_HTTP_UNREACHABLE",
        )
