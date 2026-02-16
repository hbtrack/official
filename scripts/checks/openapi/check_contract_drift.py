#!/usr/bin/env python3
"""
check_contract_drift.py

Purpose : Detect drift between on-disk openapi.json (SSOT) and the live
          FastAPI application contract.
Category: checks/openapi
Side Fx : FS_READ
Exit Codes:
  0  - No drift (openapi.json matches live app schema)
  2  - Drift detected (openapi.json is stale)
  3  - Error (import failure, missing files, parse error)
  20 - Contract drift (alias for 2, used by exit_codes_registry)

Strategy:
  1. Import app.main.app and call app.openapi() to get the live spec.
  2. Load docs/_generated/openapi.json (SSOT).
  3. Compare structurally (ignoring key order, info.version, description
     whitespace).
  4. Report additions/removals/changes in paths, schemas, parameters.

Usage:
  python scripts/checks/openapi/check_contract_drift.py [--verbose] [--fix]

  --fix   Rewrites openapi.json with the current live spec.

Requires:
  - Backend venv with FastAPI + all app deps
  - DATABASE_URL or JWT_SECRET may be needed for app startup
"""
# HB_SCRIPT_KIND=CHECK
# HB_SCRIPT_SCOPE=openapi
# HB_SCRIPT_SIDE_EFFECTS=FS_READ
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=python scripts/checks/openapi/check_contract_drift.py
# HB_SCRIPT_OUTPUTS=exit_code,console

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# ── Paths ───────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "Hb Track - Backend"
OPENAPI_JSON = REPO_ROOT / "docs" / "_generated" / "openapi.json"

# Exit codes (per exit_codes_registry.yaml)
EC_OK = 0
EC_DRIFT = 20      # canonical exit code for contract drift
EC_DRIFT_ALT = 2   # generic check "fail"
EC_ERROR = 3


def log(msg: str, verbose: bool) -> None:
    if verbose:
        print(f"  [DEBUG] {msg}", file=sys.stderr)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _load_env(verbose: bool) -> None:
    """Load .env from backend root for JWT_SECRET / DATABASE_URL if needed."""
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


def get_live_spec(verbose: bool) -> Dict[str, Any]:
    """Import FastAPI app and extract OpenAPI spec."""
    # Ensure backend is importable
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))

    # Set dummy JWT_SECRET if not present (required for config load)
    if not os.getenv("JWT_SECRET"):
        os.environ["JWT_SECRET"] = "dummy-secret-for-openapi-generation"

    log("Importing app.main.app...", verbose)
    try:
        from app.main import app
        spec = app.openapi()
        log(f"Live spec: {len(spec.get('paths', {}))} paths, "
            f"{len(spec.get('components', {}).get('schemas', {}))} schemas", verbose)
        return spec
    except Exception as e:
        print(f"[ERROR] Cannot import/call app.openapi(): {e}", file=sys.stderr)
        sys.exit(EC_ERROR)


def load_ssot_spec(verbose: bool) -> Dict[str, Any]:
    """Load the on-disk openapi.json SSOT."""
    if not OPENAPI_JSON.exists():
        print(f"[ERROR] openapi.json not found: {OPENAPI_JSON}", file=sys.stderr)
        sys.exit(EC_ERROR)

    log(f"Loading SSOT: {OPENAPI_JSON}", verbose)
    with open(OPENAPI_JSON, encoding="utf-8") as f:
        return json.load(f)


# ── Structural comparison ──────────────────────────────────────────────────

def _extract_paths(spec: Dict[str, Any]) -> Set[str]:
    """Extract all operationId-qualified endpoints."""
    paths = set()
    for path, methods in spec.get("paths", {}).items():
        for method in methods:
            if method.lower() in ("get", "post", "put", "patch", "delete", "options", "head"):
                paths.add(f"{method.upper()} {path}")
    return paths


def _extract_schemas(spec: Dict[str, Any]) -> Set[str]:
    """Extract component schema names."""
    return set(spec.get("components", {}).get("schemas", {}).keys())


def _deep_compare_keys(
    ssot: Dict, live: Dict, prefix: str = ""
) -> List[str]:
    """Recursively compare dict keys / values at path-level granularity."""
    diffs = []
    all_keys = set(ssot.keys()) | set(live.keys())
    # Skip metadata keys that change on every generation
    skip = {"info", "openapi"}
    for key in sorted(all_keys - skip):
        full = f"{prefix}.{key}" if prefix else key
        in_ssot = key in ssot
        in_live = key in live
        if in_ssot and not in_live:
            diffs.append(f"  REMOVED from live: {full}")
        elif in_live and not in_ssot:
            diffs.append(f"  ADDED in live:     {full}")
        elif isinstance(ssot[key], dict) and isinstance(live[key], dict):
            # Recurse only 2 levels deep for readability
            if prefix.count(".") < 2:
                diffs.extend(_deep_compare_keys(ssot[key], live[key], full))
            elif ssot[key] != live[key]:
                diffs.append(f"  CHANGED:           {full}")
        elif ssot[key] != live[key]:
            diffs.append(f"  CHANGED:           {full}")
    return diffs


def compare_specs(
    ssot: Dict[str, Any], live: Dict[str, Any], verbose: bool
) -> Tuple[List[str], dict]:
    """
    Compare SSOT vs live spec.
    Returns (diff_lines, summary_dict).
    """
    diffs: List[str] = []
    summary = {"paths_added": 0, "paths_removed": 0, "schemas_added": 0,
               "schemas_removed": 0, "other_changes": 0}

    # Paths
    ssot_paths = _extract_paths(ssot)
    live_paths = _extract_paths(live)
    added_paths = sorted(live_paths - ssot_paths)
    removed_paths = sorted(ssot_paths - live_paths)

    if added_paths:
        summary["paths_added"] = len(added_paths)
        diffs.append(f"+++ Endpoints in live app but NOT in openapi.json ({len(added_paths)}):")
        for p in added_paths:
            diffs.append(f"  + {p}")

    if removed_paths:
        summary["paths_removed"] = len(removed_paths)
        diffs.append(f"--- Endpoints in openapi.json but NOT in live app ({len(removed_paths)}):")
        for p in removed_paths:
            diffs.append(f"  - {p}")

    # Schemas
    ssot_schemas = _extract_schemas(ssot)
    live_schemas = _extract_schemas(live)
    added_schemas = sorted(live_schemas - ssot_schemas)
    removed_schemas = sorted(ssot_schemas - live_schemas)

    if added_schemas:
        summary["schemas_added"] = len(added_schemas)
        diffs.append(f"+++ Schemas in live app but NOT in openapi.json ({len(added_schemas)}):")
        for s in added_schemas[:20]:
            diffs.append(f"  + {s}")
        if len(added_schemas) > 20:
            diffs.append(f"  ... and {len(added_schemas) - 20} more")

    if removed_schemas:
        summary["schemas_removed"] = len(removed_schemas)
        diffs.append(f"--- Schemas in openapi.json but NOT in live app ({len(removed_schemas)}):")
        for s in removed_schemas[:20]:
            diffs.append(f"  - {s}")
        if len(removed_schemas) > 20:
            diffs.append(f"  ... and {len(removed_schemas) - 20} more")

    # Deep comparison on paths section
    ssot_paths_dict = ssot.get("paths", {})
    live_paths_dict = live.get("paths", {})
    structural = _deep_compare_keys(ssot_paths_dict, live_paths_dict, "paths")
    if structural:
        summary["other_changes"] = len(structural)
        diffs.append(f"~~ Structural changes in paths ({len(structural)}):")
        diffs.extend(structural[:40])
        if len(structural) > 40:
            diffs.append(f"  ... and {len(structural) - 40} more")

    return diffs, summary


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check openapi.json drift against live FastAPI app"
    )
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed debug info")
    parser.add_argument("--fix", action="store_true",
                        help="Regenerate openapi.json if drift detected")
    args = parser.parse_args()

    # Load env
    _load_env(args.verbose)

    # Load SSOT
    print(f"📖 Reading SSOT: {OPENAPI_JSON.relative_to(REPO_ROOT)}")
    ssot = load_ssot_spec(args.verbose)
    ssot_path_count = len(ssot.get("paths", {}))
    ssot_schema_count = len(ssot.get("components", {}).get("schemas", {}))
    log(f"SSOT: {ssot_path_count} paths, {ssot_schema_count} schemas", args.verbose)

    # Get live spec
    print("🔍 Extracting live OpenAPI spec from FastAPI app...")
    live = get_live_spec(args.verbose)

    # Compare
    print("📊 Comparing specs...")
    diffs, summary = compare_specs(ssot, live, args.verbose)

    if not diffs:
        print("✅ No contract drift. openapi.json matches live app.")
        return EC_OK

    # Drift detected
    total = (summary["paths_added"] + summary["paths_removed"] +
             summary["schemas_added"] + summary["schemas_removed"] +
             summary["other_changes"])
    print(f"⚠️  Contract drift detected! ({total} differences)")
    print()
    for line in diffs:
        print(line)
    print()

    if args.fix:
        print("🔧 Regenerating openapi.json from live app...")
        with open(OPENAPI_JSON, "w", encoding="utf-8") as f:
            json.dump(live, f, indent=2, ensure_ascii=False)
        print(f"✅ openapi.json regenerated: {OPENAPI_JSON.relative_to(REPO_ROOT)}")
        return EC_OK

    print(f"Fix: python scripts/checks/openapi/check_contract_drift.py --fix")
    print(f"  or: python scripts/generate/docs/gen_docs_soot.py --openapi")
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
