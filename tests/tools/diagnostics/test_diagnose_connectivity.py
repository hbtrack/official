"""
Test matrix: TC01–TC10 — CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0

All tests are fully offline (network calls mocked).
Covers Definition of Done checks from DIAGNOSTIC_CONNECTIVITY_CONTRACT.yaml.
"""
from __future__ import annotations

import os
import pathlib
import socket
import sys
from unittest.mock import MagicMock, patch, patch as _patch

import pytest

# ── Ensure workspace root on path ─────────────────────────────────────────────
_WORKSPACE = pathlib.Path(__file__).parent.parent.parent.parent
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from tools.diagnostics.diagnose_connectivity import run_diagnostic

# ── Test constants ────────────────────────────────────────────────────────────
_REMOTE_API = "http://191.252.185.34/api/v1"
_REMOTE_HOST = "191.252.185.34"
_REMOTE_PORT = 80
_ORIGIN = "http://localhost:3000"
_HEALTH_PATH = "/api/v1/health"
_READINESS_PATH = "/api/v1/health/readiness"

_BASE_PARAMS: dict = dict(
    api_base_url=_REMOTE_API,
    frontend_origin=_ORIGIN,
    health_path=_HEALTH_PATH,
    readiness_path=_READINESS_PATH,
    env_var_names=["NEXT_PUBLIC_API_URL"],
    env_file="",          # empty → only os.environ used in unit tests
    timeout=8,
    verify_tls=False,
)

# Fake DNS result for address resolution
_DNS_RESULT = [(2, 1, 6, "", (_REMOTE_HOST, 0))]

# Healthy JSON body returned by /api/v1/health
_HEALTHY_BODY = {
    "status": "healthy",
    "version": "1.0",
    "environment": "staging",
    "database": {"status": "healthy"},
}

# CORS headers that accept localhost:3000
_CORS_HEADERS_OK = {
    "Access-Control-Allow-Origin": "http://localhost:3000",
    "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
}


class _FakeSocket:
    """Minimal context-manager socket stub for TCP pass."""

    def __enter__(self) -> "_FakeSocket":
        return self

    def __exit__(self, *args: object) -> None:
        pass


def _mock_resp(
    status: int,
    json_data: object = None,
    headers: dict | None = None,
) -> MagicMock:
    """Build a minimal requests.Response mock."""
    m = MagicMock()
    m.status_code = status
    m.ok = status < 400
    m.is_redirect = False
    # Use a real dict for headers so .get() works natively
    m.headers = headers or {}
    if json_data is not None:
        m.json.return_value = json_data
    else:
        m.json.side_effect = ValueError("no JSON")
    return m


# ─── TC01 ─────────────────────────────────────────────────────────────────────
def test_tc01_url_missing() -> None:
    """TC01: FRONTEND_API_URL_MISSING — var not defined anywhere."""
    env_clean = {k: v for k, v in os.environ.items() if k != "NEXT_PUBLIC_API_URL"}
    with patch.dict("os.environ", env_clean, clear=True):
        result = run_diagnostic(
            **{**_BASE_PARAMS, "env_file": "/nonexistent_path/.env.local"}
        )

    assert result.root_cause_code == "FRONTEND_API_URL_MISSING", result.root_cause_code
    assert result.exit_code == 4, result.exit_code
    assert result.status == "fail"
    # Verify the failing check is in the list
    names = [c.name for c in result.checks]
    assert "frontend_api_url_discovery" in names


# ─── TC02 ─────────────────────────────────────────────────────────────────────
def test_tc02_url_invalid() -> None:
    """TC02: FRONTEND_API_URL_INVALID — env var contains a non-URL string."""
    with patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": "not-a-url"}):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "FRONTEND_API_URL_INVALID", result.root_cause_code
    assert result.exit_code == 4
    assert result.status == "fail"


# ─── TC03 ─────────────────────────────────────────────────────────────────────
def test_tc03_localhost_misuse() -> None:
    """TC03: FRONTEND_API_URL_LOCALHOST_MISUSE — frontend points to localhost but API is remote."""
    with patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": "http://localhost:8000/api/v1"}):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "FRONTEND_API_URL_LOCALHOST_MISUSE", result.root_cause_code
    assert result.exit_code == 2
    assert result.status == "fail"
    # Must identify misuse before any network check
    check_names = [c.name for c in result.checks]
    assert "dns_resolution" not in check_names, "Should stop before DNS on localhost misuse"


# ─── TC04 ─────────────────────────────────────────────────────────────────────
def test_tc04_dns_unresolved() -> None:
    """TC04: API_HOST_UNRESOLVED — DNS resolution fails for the remote host."""
    with (
        patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": _REMOTE_API}),
        patch("socket.getaddrinfo", side_effect=socket.gaierror("name or service not known")),
    ):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "API_HOST_UNRESOLVED", result.root_cause_code
    assert result.exit_code == 2
    assert result.status == "fail"


# ─── TC05 ─────────────────────────────────────────────────────────────────────
def test_tc05_port_closed() -> None:
    """TC05: API_PORT_CLOSED — TCP connection refused."""
    with (
        patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": _REMOTE_API}),
        patch("socket.getaddrinfo", return_value=_DNS_RESULT),
        patch("socket.create_connection", side_effect=ConnectionRefusedError("connection refused")),
    ):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "API_PORT_CLOSED", result.root_cause_code
    assert result.exit_code == 2
    assert result.status == "fail"


# ─── TC06 ─────────────────────────────────────────────────────────────────────
def test_tc06_cors_blocking() -> None:
    """TC06: CORS_BLOCKING_ORIGIN — API up, CORS does not allow localhost:3000."""
    health_ok = _mock_resp(200, _HEALTHY_BODY)
    ready_ok = _mock_resp(200, {"status": "ready"})
    cors_blocked = _mock_resp(200, headers={})  # No Access-Control-Allow-Origin header

    def _get(url: str, **kw: object):  # type: ignore[return]
        if "readiness" in url:
            return ready_ok
        return health_ok

    with (
        patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": _REMOTE_API}),
        patch("socket.getaddrinfo", return_value=_DNS_RESULT),
        patch("socket.create_connection", return_value=_FakeSocket()),
        patch("requests.get", side_effect=_get),
        patch("requests.options", return_value=cors_blocked),
    ):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "CORS_BLOCKING_ORIGIN", result.root_cause_code
    assert result.exit_code == 2
    assert result.status == "fail"


# ─── TC07 ─────────────────────────────────────────────────────────────────────
def test_tc07_health_missing() -> None:
    """TC07: API_HEALTH_ENDPOINT_MISSING — health endpoint returns 404."""
    not_found = _mock_resp(404)

    with (
        patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": _REMOTE_API}),
        patch("socket.getaddrinfo", return_value=_DNS_RESULT),
        patch("socket.create_connection", return_value=_FakeSocket()),
        patch("requests.get", return_value=not_found),
    ):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "API_HEALTH_ENDPOINT_MISSING", result.root_cause_code
    assert result.exit_code == 2
    assert result.status == "fail"
    # Should not have reached CORS or readiness checks
    check_names = [c.name for c in result.checks]
    assert "cors_preflight" not in check_names


# ─── TC08 ─────────────────────────────────────────────────────────────────────
def test_tc08_backend_not_ready() -> None:
    """TC08: BACKEND_NOT_READY — /api/v1/health/readiness returns 503."""
    health_ok = _mock_resp(200, _HEALTHY_BODY)
    ready_fail = _mock_resp(
        503, {"status": "not_ready", "critical_checks": {"database": "fail"}}
    )
    cors_ok = _mock_resp(200, headers=_CORS_HEADERS_OK)

    def _get(url: str, **kw: object):  # type: ignore[return]
        if "readiness" in url:
            return ready_fail
        return health_ok

    with (
        patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": _REMOTE_API}),
        patch("socket.getaddrinfo", return_value=_DNS_RESULT),
        patch("socket.create_connection", return_value=_FakeSocket()),
        patch("requests.get", side_effect=_get),
        patch("requests.options", return_value=cors_ok),
    ):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "BACKEND_NOT_READY", result.root_cause_code
    assert result.exit_code == 2
    assert result.status == "fail"


# ─── TC09 ─────────────────────────────────────────────────────────────────────
def test_tc09_database_down() -> None:
    """TC09: DATABASE_DOWN — /api/v1/health declares database unhealthy."""
    unhealthy_body = {
        "status": "unhealthy",
        "version": "1.0",
        "environment": "staging",
        "database": {"status": "unhealthy"},
    }
    health_sick = _mock_resp(200, unhealthy_body)
    ready_ok = _mock_resp(200, {"status": "ready"})
    cors_ok = _mock_resp(200, headers=_CORS_HEADERS_OK)

    def _get(url: str, **kw: object):  # type: ignore[return]
        if "readiness" in url:
            return ready_ok
        return health_sick

    with (
        patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": _REMOTE_API}),
        patch("socket.getaddrinfo", return_value=_DNS_RESULT),
        patch("socket.create_connection", return_value=_FakeSocket()),
        patch("requests.get", side_effect=_get),
        patch("requests.options", return_value=cors_ok),
    ):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "DATABASE_DOWN", result.root_cause_code
    assert result.exit_code == 2
    assert result.status == "fail"


# ─── TC10 ─────────────────────────────────────────────────────────────────────
def test_tc10_pass() -> None:
    """TC10: PASS — all checks succeed, system fully healthy."""
    health_ok = _mock_resp(200, _HEALTHY_BODY)
    ready_ok = _mock_resp(200, {"status": "ready"})
    cors_ok = _mock_resp(200, headers=_CORS_HEADERS_OK)

    def _get(url: str, **kw: object):  # type: ignore[return]
        if "readiness" in url:
            return ready_ok
        return health_ok

    with (
        patch.dict("os.environ", {"NEXT_PUBLIC_API_URL": _REMOTE_API}),
        patch("socket.getaddrinfo", return_value=_DNS_RESULT),
        patch("socket.create_connection", return_value=_FakeSocket()),
        patch("requests.get", side_effect=_get),
        patch("requests.options", return_value=cors_ok),
    ):
        result = run_diagnostic(**_BASE_PARAMS)

    assert result.root_cause_code == "PASS", result.root_cause_code
    assert result.exit_code == 0
    assert result.status == "pass"
    # Verify report fields are present
    d = result.to_dict()
    for field in ("contract", "version", "status", "exit_code", "root_cause_code",
                  "root_cause_summary", "inputs", "checks", "recommended_action"):
        assert field in d, f"Required JSON field missing: {field}"


# ─── Extra: verify JSON report contract fields ────────────────────────────────
def test_report_fields_all_present() -> None:
    """All required JSON report fields are present on any result."""
    with patch.dict("os.environ", {}, clear=True):
        result = run_diagnostic(
            **{**_BASE_PARAMS, "env_file": "/nonexistent"}
        )

    d = result.to_dict()
    required_fields = [
        "contract", "version", "status", "exit_code",
        "root_cause_code", "root_cause_summary",
        "inputs", "checks", "recommended_action",
    ]
    for field in required_fields:
        assert field in d, f"Required JSON field missing: {field}"
    assert d["contract"] == "CONNECTIVITY_DIAGNOSTIC_CONTRACT"
    assert d["version"] == "1.1.0"
