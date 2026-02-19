#!/usr/bin/env python3
"""
check_schema_drift.py

Purpose : Detect drift between on-disk schema.sql (SSOT) and live database.
Category: checks/db
Side Fx : DB_READ, FS_READ
Exit Codes:
  0 - No drift (schema.sql matches live DB)
  2 - Drift detected (schema.sql is stale)
  3 - Error (connection failure, missing files, parse error)
  5 - Schema drift (alias for 2, used by exit_codes_registry)

Uses the same pg_dump approach as gen_docs_soot.py to get a fresh dump
and compares it (structurally) against docs/ssot/schema.sql.

Usage:
  python scripts/checks/db/check_schema_drift.py [--verbose] [--fix]

  --fix   Regenerates schema.sql if drift is detected (equivalent to
          running gen_docs_soot.py schema step).

Requires:
  - DATABASE_URL env var (or .env file in backend root)
  - pg_dump on PATH
"""
# HB_SCRIPT_KIND=CHECK
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_READ,FS_READ
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=python scripts/checks/db/check_schema_drift.py
# HB_SCRIPT_OUTPUTS=exit_code,console

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

# ── Paths ───────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "Hb Track - Backend"
SCHEMA_SQL = REPO_ROOT / "docs" / "ssot" / "schema.sql"

# Exit codes (per exit_codes_registry.yaml)
EC_OK = 0
EC_DRIFT = 5       # canonical exit code for schema drift
EC_DRIFT_ALT = 2   # generic check "fail"
EC_ERROR = 3


def log(msg: str, verbose: bool) -> None:
    if verbose:
        print(f"  [DEBUG] {msg}", file=sys.stderr)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _load_env(verbose: bool) -> None:
    """Try loading .env from the backend root if DATABASE_URL is not set."""
    if os.getenv("DATABASE_URL"):
        log("DATABASE_URL already set", verbose)
        return

    env_file = BACKEND_ROOT / ".env"
    if not env_file.exists():
        return

    log(f"Loading .env from {env_file}", verbose)
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and not os.getenv(key):
                os.environ[key] = val


def _clean_url(database_url: str) -> str:
    """Normalize async driver prefixes for pg_dump."""
    url = database_url
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgresql+psycopg2://", "postgresql://")
    url = url.replace("postgresql+psycopg://", "postgresql://")
    return url


def _normalize_schema(raw: str) -> str:
    """
    Normalize a pg_dump output for structural comparison.

    Strips:
    - Comments (-- ...)
    - Blank lines
    - Timestamp-like patterns
    - SET/SELECT statements (config noise)
    - Ownership / privilege lines
    """
    lines = []
    skip_patterns = re.compile(
        r"^\s*(--|SET |SELECT |ALTER .* OWNER|GRANT |REVOKE )", re.IGNORECASE
    )
    for line in raw.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue
        if skip_patterns.match(stripped):
            continue
        lines.append(stripped)
    return "\n".join(lines)


# ── Core logic ──────────────────────────────────────────────────────────────

def pg_dump_fresh(verbose: bool) -> str:
    """Run pg_dump --schema-only against the live DB and return output."""
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("[ERROR] DATABASE_URL not set. Cannot connect to database.", file=sys.stderr)
        sys.exit(EC_ERROR)

    clean_url = _clean_url(database_url)
    parsed = urlparse(clean_url)

    if not all([parsed.hostname, parsed.username, parsed.path]):
        print(f"[ERROR] Invalid DATABASE_URL format", file=sys.stderr)
        sys.exit(EC_ERROR)

    pg_dump_args = [
        "pg_dump",
        "--schema-only",
        "--no-owner",
        "--no-privileges",
        "-h", parsed.hostname,
        "-p", str(parsed.port or 5432),
        "-U", parsed.username,
        "-d", parsed.path.lstrip("/").split("?")[0],
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = parsed.password or ""

    if "sslmode" in database_url:
        env["PGSSLMODE"] = "require"

    log(f"Running pg_dump against {parsed.hostname}...", verbose)

    try:
        result = subprocess.run(
            pg_dump_args,
            capture_output=True,
            text=False,
            env=env,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        print("[ERROR] pg_dump not found on PATH. Install PostgreSQL client tools.", file=sys.stderr)
        sys.exit(EC_ERROR)
    except subprocess.TimeoutExpired:
        print("[ERROR] pg_dump timed out (120s).", file=sys.stderr)
        sys.exit(EC_ERROR)

    if result.returncode != 0:
        err = (result.stderr or b"").decode("utf-8", errors="replace")
        print(f"[ERROR] pg_dump failed (exit {result.returncode}): {err}", file=sys.stderr)
        sys.exit(EC_ERROR)

    raw = (result.stdout or b"").decode("utf-8", errors="replace")
    log(f"pg_dump returned {len(raw)} bytes", verbose)
    return raw


def compare_schemas(ssot_raw: str, live_raw: str, verbose: bool) -> list[str]:
    """
    Compare normalized schema.sql (SSOT) vs live pg_dump output.
    Returns list of diff lines (empty = no drift).
    """
    ssot_norm = _normalize_schema(ssot_raw)
    live_norm = _normalize_schema(live_raw)

    if ssot_norm == live_norm:
        return []

    # Produce a simple line-based diff summary
    ssot_lines = set(ssot_norm.splitlines())
    live_lines = set(live_norm.splitlines())

    only_in_ssot = sorted(ssot_lines - live_lines)
    only_in_live = sorted(live_lines - ssot_lines)

    diffs = []
    if only_in_ssot:
        diffs.append(f"--- Lines in schema.sql but NOT in live DB ({len(only_in_ssot)}):")
        for line in only_in_ssot[:30]:
            diffs.append(f"  - {line}")
        if len(only_in_ssot) > 30:
            diffs.append(f"  ... and {len(only_in_ssot) - 30} more")

    if only_in_live:
        diffs.append(f"+++ Lines in live DB but NOT in schema.sql ({len(only_in_live)}):")
        for line in only_in_live[:30]:
            diffs.append(f"  + {line}")
        if len(only_in_live) > 30:
            diffs.append(f"  ... and {len(only_in_live) - 30} more")

    return diffs


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check schema.sql drift against live database"
    )
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed debug info")
    parser.add_argument("--fix", action="store_true",
                        help="Regenerate schema.sql if drift detected")
    args = parser.parse_args()

    # Load .env if needed
    _load_env(args.verbose)

    # Read SSOT
    if not SCHEMA_SQL.exists():
        print(f"[ERROR] schema.sql not found: {SCHEMA_SQL}", file=sys.stderr)
        return EC_ERROR

    print(f"📖 Reading SSOT: {SCHEMA_SQL.relative_to(REPO_ROOT)}")
    ssot_raw = SCHEMA_SQL.read_text(encoding="utf-8")
    log(f"SSOT size: {len(ssot_raw)} bytes", args.verbose)

    # Dump live DB
    print("🔍 Dumping live database schema...")
    live_raw = pg_dump_fresh(args.verbose)

    # Compare
    print("📊 Comparing schemas...")
    diffs = compare_schemas(ssot_raw, live_raw, args.verbose)

    if not diffs:
        print("✅ No schema drift. schema.sql matches live database.")
        return EC_OK

    # Drift detected
    print(f"⚠️  Schema drift detected!")
    print()
    for line in diffs:
        print(line)
    print()

    if args.fix:
        print("🔧 Regenerating schema.sql from live DB...")
        from datetime import datetime, timezone
        header = f"-- Schema dump generated: {datetime.now(timezone.utc).isoformat()}Z\n"
        header += f"-- Source: live database\n\n"
        SCHEMA_SQL.write_text(header + live_raw, encoding="utf-8")
        print(f"✅ schema.sql regenerated: {SCHEMA_SQL.relative_to(REPO_ROOT)}")
        return EC_OK

    print(f"Fix: python scripts/checks/db/check_schema_drift.py --fix")
    print(f"  or: python scripts/generate/docs/gen_docs_soot.py (full refresh)")
    return EC_DRIFT


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(EC_ERROR)
