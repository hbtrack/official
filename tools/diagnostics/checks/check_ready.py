"""
Check 11: Backend readiness.
Uses /api/v1/health/readiness (canonical path — NOT /ready).
Fail codes: BACKEND_NOT_READY
"""
from __future__ import annotations

from urllib.parse import urlparse

import requests

from tools.diagnostics.models.check_result import CheckResult


def check_readiness(
    api_base_url: str,
    readiness_path: str,
    timeout: int = 8,
    verify_tls: bool = False,
) -> CheckResult:
    """
    Check 11: Verify /api/v1/health/readiness.
    200 = backend ready, 503 = backend not ready.
    """
    parsed = urlparse(api_base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    full_url = base + readiness_path

    try:
        resp = requests.get(full_url, timeout=timeout, verify=verify_tls)

        if resp.status_code == 503:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            return CheckResult(
                name="backend_readiness",
                status="fail",
                evidence={"url": full_url, "status_code": 503, "body": body},
                root_cause_candidate="BACKEND_NOT_READY",
            )

        if resp.status_code == 200:
            return CheckResult(
                name="backend_readiness",
                status="pass",
                evidence={"url": full_url, "status_code": 200},
            )

        # Unexpected status — warn but don't classify as root cause
        return CheckResult(
            name="backend_readiness",
            status="warn",
            evidence={
                "url": full_url,
                "status_code": resp.status_code,
                "note": "Unexpected status code from readiness endpoint",
            },
        )

    except requests.Timeout:
        return CheckResult(
            name="backend_readiness",
            status="fail",
            evidence=f"GET {full_url} timed out after {timeout}s",
            root_cause_candidate="BACKEND_NOT_READY",
        )
    except requests.ConnectionError as exc:
        return CheckResult(
            name="backend_readiness",
            status="fail",
            evidence=f"GET {full_url} connection error: {exc}",
            root_cause_candidate="BACKEND_NOT_READY",
        )
