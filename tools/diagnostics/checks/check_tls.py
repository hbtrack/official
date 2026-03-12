"""
Check 6: TLS handshake and certificate validation.
Only executed when scheme=https.
Fail codes: TLS_CERT_INVALID, TLS_HOSTNAME_MISMATCH, TLS_HANDSHAKE_FAILED
"""
from __future__ import annotations

import socket
import ssl

from tools.diagnostics.models.check_result import CheckResult


def check_tls(host: str, port: int, timeout: int = 8) -> CheckResult:
    """
    Check 6: Validate TLS handshake and certificate for an HTTPS endpoint.
    """
    ctx = ssl.create_default_context()
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_sock.settimeout(timeout)
    try:
        with ctx.wrap_socket(raw_sock, server_hostname=host) as ssock:
            ssock.connect((host, port))
            cert = ssock.getpeercert()
            subject = cert.get("subject", "")
            return CheckResult(
                name="tls_validation",
                status="pass",
                evidence=f"TLS handshake OK; cert subject={subject}",
            )
    except ssl.SSLCertVerificationError as exc:
        code = (
            "TLS_HOSTNAME_MISMATCH"
            if "hostname" in str(exc).lower()
            else "TLS_CERT_INVALID"
        )
        return CheckResult(
            name="tls_validation",
            status="fail",
            evidence=f"TLS certificate error: {exc}",
            root_cause_candidate=code,
        )
    except ssl.SSLError as exc:
        return CheckResult(
            name="tls_validation",
            status="fail",
            evidence=f"TLS handshake failed: {exc}",
            root_cause_candidate="TLS_HANDSHAKE_FAILED",
        )
    except Exception as exc:
        return CheckResult(
            name="tls_validation",
            status="fail",
            evidence=f"TLS connection error: {exc}",
            root_cause_candidate="TLS_HANDSHAKE_FAILED",
        )
