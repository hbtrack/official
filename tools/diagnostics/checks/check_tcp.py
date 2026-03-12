"""
Check 5: TCP connectivity.
Fail codes: API_PORT_CLOSED, API_TCP_TIMEOUT
"""
from __future__ import annotations

import socket

from tools.diagnostics.models.check_result import CheckResult


def check_tcp_connectivity(host: str, port: int, timeout: int = 8) -> CheckResult:
    """
    Check 5: Verify the API port is reachable via TCP.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return CheckResult(
                name="tcp_connectivity",
                status="pass",
                evidence=f"{host}:{port} reachable",
            )
    except socket.timeout:
        return CheckResult(
            name="tcp_connectivity",
            status="fail",
            evidence=f"{host}:{port} — connection timed out ({timeout}s)",
            root_cause_candidate="API_TCP_TIMEOUT",
        )
    except (ConnectionRefusedError, OSError) as exc:
        return CheckResult(
            name="tcp_connectivity",
            status="fail",
            evidence=f"{host}:{port} — port closed or unreachable: {exc}",
            root_cause_candidate="API_PORT_CLOSED",
        )
