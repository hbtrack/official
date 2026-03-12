"""
Configuration for CONNECTIVITY_DIAGNOSTIC_CONTRACT v1.1.0

Canonical values sourced from DIAGNOSTIC_CONNECTIVITY_CONTRACT.yaml.
All values are overridable via environment variables prefixed with DIAG_.
"""
from __future__ import annotations

import os
import pathlib

# Resolve the workspace root (two levels above tools/diagnostics/)
_HERE = pathlib.Path(__file__).parent               # tools/diagnostics/
_WORKSPACE_ROOT = _HERE.parent.parent               # repo root


# ── Canonical target API ──────────────────────────────────────────────────────
API_BASE_URL: str = os.environ.get(
    "DIAG_API_BASE_URL",
    "http://191.252.185.34:8000/api/v1",
)

# ── Frontend origin (browser's local origin) ─────────────────────────────────
FRONTEND_ORIGIN: str = os.environ.get(
    "DIAG_FRONTEND_ORIGIN",
    "http://localhost:3000",
)

# ── Health endpoints (real paths — NOT /ready alias) ─────────────────────────
HEALTH_PATH: str = "/api/v1/health"
READINESS_PATH: str = "/api/v1/health/readiness"

# ── Frontend environment resolution ──────────────────────────────────────────
FRONTEND_ENV_VAR_NAMES: list = ["NEXT_PUBLIC_API_URL"]

ENV_FILE: str = os.environ.get(
    "DIAG_ENV_FILE",
    str(_WORKSPACE_ROOT / "Hb Track - Frontend" / ".env.local"),
)

# ── HTTP settings ─────────────────────────────────────────────────────────────
TIMEOUT_SECONDS: int = int(os.environ.get("DIAG_TIMEOUT", "8"))
VERIFY_TLS: bool = os.environ.get("DIAG_VERIFY_TLS", "false").lower() == "true"

# ── Reporting ─────────────────────────────────────────────────────────────────
REPORT_JSON_PATH: str = os.environ.get(
    "DIAG_REPORT_JSON",
    str(_WORKSPACE_ROOT / "_reports" / "connectivity_diagnostic_report.json"),
)
REPORT_MD_PATH: str = os.environ.get(
    "DIAG_REPORT_MD",
    str(_WORKSPACE_ROOT / "_reports" / "connectivity_diagnostic_report.md"),
)
REPORT_MARKDOWN: bool = True

# ── Exit codes ────────────────────────────────────────────────────────────────
EXIT_PASS: int = 0
EXIT_FAIL_ACTIONABLE: int = 2
EXIT_ERROR_INFRA: int = 3
EXIT_BLOCKED_INPUT: int = 4
