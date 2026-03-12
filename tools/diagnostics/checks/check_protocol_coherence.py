"""
Check 8: Protocol coherence / mixed content risk detection.
Fail codes: MIXED_CONTENT_RISK
"""
from __future__ import annotations

from urllib.parse import urlparse

from tools.diagnostics.models.check_result import CheckResult


def check_protocol_coherence(frontend_origin: str, api_base_url: str) -> CheckResult:
    """
    Check 8: Detect mixed content risk.
    A frontend served over HTTPS calling an HTTP API is blocked by browsers.
    """
    frontend_scheme = urlparse(frontend_origin).scheme
    api_scheme = urlparse(api_base_url).scheme

    if frontend_scheme == "https" and api_scheme == "http":
        return CheckResult(
            name="protocol_coherence",
            status="fail",
            evidence=(
                f"Frontend ({frontend_origin}) uses HTTPS but API "
                f"({api_base_url}) uses HTTP. "
                "Browsers block mixed active content (Mixed Content policy)."
            ),
            root_cause_candidate="MIXED_CONTENT_RISK",
        )

    return CheckResult(
        name="protocol_coherence",
        status="pass",
        evidence=(
            f"No mixed content risk: "
            f"frontend_scheme={frontend_scheme}, api_scheme={api_scheme}"
        ),
    )
