"""
Check 4: DNS resolution.
Fail codes: API_HOST_UNRESOLVED
"""
from __future__ import annotations

import socket

from tools.diagnostics.models.check_result import CheckResult


def check_dns_resolution(host: str) -> CheckResult:
    """
    Check 4: Verify the API host resolves via DNS.
    Skipped for localhost/loopback hosts.
    """
    if host in ("localhost", "127.0.0.1", "::1", ""):
        return CheckResult(
            name="dns_resolution",
            status="skip",
            evidence=f"Skipped: {host!r} is localhost/loopback",
        )

    try:
        results = socket.getaddrinfo(host, None)
        addresses = list({r[4][0] for r in results})
        return CheckResult(
            name="dns_resolution",
            status="pass",
            evidence=f"{host} -> {', '.join(addresses)}",
        )
    except socket.gaierror as exc:
        return CheckResult(
            name="dns_resolution",
            status="fail",
            evidence=f"DNS resolution failed for {host!r}: {exc}",
            root_cause_candidate="API_HOST_UNRESOLVED",
        )
