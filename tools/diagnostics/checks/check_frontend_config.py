"""
Checks 1-3: Frontend API URL discovery, topology validation, and URL parse.

Check 1 — frontend_api_url_discovery
  Fail codes: FRONTEND_API_URL_MISSING, FRONTEND_API_URL_INVALID

Check 2 — frontend_api_url_topology_check
  Fail codes: FRONTEND_API_URL_LOCALHOST_MISUSE

Check 3 — api_url_parse
  Fail codes: API_URL_PARSE_ERROR
"""
from __future__ import annotations

import os
import pathlib
from typing import Optional, Tuple
from urllib.parse import urlparse

from tools.diagnostics.models.check_result import CheckResult


def _read_env_file(env_file: str, var_names: list) -> Optional[str]:
    """Read the first matching variable from a .env-style file."""
    try:
        path = pathlib.Path(env_file)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip() in var_names:
                    return value.strip().strip('"').strip("'")
    except Exception:
        return None
    return None


def check_frontend_api_url(
    env_var_names: list,
    env_file: Optional[str] = None,
) -> Tuple[CheckResult, Optional[str]]:
    """
    Check 1: Discover the API URL from frontend environment.
    Returns (CheckResult, url_or_None).
    """
    url: Optional[str] = None
    found_source: Optional[str] = None

    # 1. Try os.environ first (highest priority)
    for var in env_var_names:
        val = os.environ.get(var)
        if val and val.strip():
            url = val.strip()
            found_source = f"env:{var}"
            break

    # 2. Try env file
    if url is None and env_file:
        val = _read_env_file(env_file, env_var_names)
        if val:
            url = val
            found_source = f"{env_file}:{env_var_names[0] if env_var_names else 'var'}"

    if url is None:
        return CheckResult(
            name="frontend_api_url_discovery",
            status="fail",
            evidence=(
                f"None of {env_var_names} found in os.environ"
                + (f" or {env_file}" if env_file else "")
            ),
            root_cause_candidate="FRONTEND_API_URL_MISSING",
        ), None

    # Validate URL syntax
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return CheckResult(
                name="frontend_api_url_discovery",
                status="fail",
                evidence=f"{found_source}={url!r} — missing scheme or netloc",
                root_cause_candidate="FRONTEND_API_URL_INVALID",
            ), None
        if parsed.scheme not in ("http", "https"):
            return CheckResult(
                name="frontend_api_url_discovery",
                status="fail",
                evidence=f"{found_source}={url!r} — unsupported scheme {parsed.scheme!r}",
                root_cause_candidate="FRONTEND_API_URL_INVALID",
            ), None
    except Exception as exc:
        return CheckResult(
            name="frontend_api_url_discovery",
            status="fail",
            evidence=f"URL parse exception for {url!r}: {exc}",
            root_cause_candidate="FRONTEND_API_URL_INVALID",
        ), None

    return CheckResult(
        name="frontend_api_url_discovery",
        status="pass",
        evidence=f"{found_source}={url}",
    ), url


def check_frontend_api_url_topology(
    frontend_url: str,
    is_remote_target: bool,
) -> CheckResult:
    """
    Check 2: Detect localhost misuse in browser→VPS topology.
    When the frontend env points to localhost but the target API is remote,
    the browser will never reach the VPS.
    """
    parsed = urlparse(frontend_url)
    host = parsed.hostname or ""
    is_local = host in ("localhost", "127.0.0.1", "::1")

    if is_local and is_remote_target:
        return CheckResult(
            name="frontend_api_url_topology_check",
            status="fail",
            evidence=(
                f"NEXT_PUBLIC_API_URL={frontend_url!r} aponta para localhost, "
                "mas o backend alvo é remoto. Em cenário browser→VPS o browser "
                "resolve localhost como a máquina local, não a VPS."
            ),
            root_cause_candidate="FRONTEND_API_URL_LOCALHOST_MISUSE",
        )

    return CheckResult(
        name="frontend_api_url_topology_check",
        status="pass",
        evidence=(
            f"URL {frontend_url!r} é compatível com a topologia "
            f"(is_local={is_local}, is_remote_target={is_remote_target})"
        ),
    )


def check_api_url_parse(api_base_url: str) -> Tuple[CheckResult, Optional[dict]]:
    """
    Check 3: Parse the target API URL into components.
    Returns (CheckResult, parsed_dict_or_None).
    """
    try:
        parsed = urlparse(api_base_url)
        if not parsed.scheme or not parsed.netloc:
            return CheckResult(
                name="api_url_parse",
                status="fail",
                evidence=f"Cannot parse API URL {api_base_url!r} — missing scheme or netloc",
                root_cause_candidate="API_URL_PARSE_ERROR",
            ), None

        port = parsed.port
        if port is None:
            port = 443 if parsed.scheme == "https" else 80

        result = {
            "scheme": parsed.scheme,
            "host": parsed.hostname or "",
            "port": port,
            "base_path": parsed.path or "",
        }
        return CheckResult(
            name="api_url_parse",
            status="pass",
            evidence=result,
        ), result

    except Exception as exc:
        return CheckResult(
            name="api_url_parse",
            status="fail",
            evidence=f"URL parse exception: {exc}",
            root_cause_candidate="API_URL_PARSE_ERROR",
        ), None
