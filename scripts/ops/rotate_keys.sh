#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

SECRET_NAME=""
ENVIRONMENT=""
FORMAT="text"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --secret)
      SECRET_NAME="${2:-}"
      shift 2
      ;;
    --environment)
      ENVIRONMENT="${2:-}"
      shift 2
      ;;
    --format)
      FORMAT="${2:-}"
      shift 2
      ;;
    *)
      echo "usage: $0 --secret <NAME> --environment <staging|production> [--format text|json]" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$SECRET_NAME" || -z "$ENVIRONMENT" ]]; then
  echo "usage: $0 --secret <NAME> --environment <staging|production> [--format text|json]" >&2
  exit 2
fi

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
  echo "environment deve ser staging ou production" >&2
  exit 2
fi

if [[ "$FORMAT" != "text" && "$FORMAT" != "json" ]]; then
  echo "format deve ser text ou json" >&2
  exit 2
fi

python3 - "$ROOT" "$SECRET_NAME" "$ENVIRONMENT" "$FORMAT" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])
secret_name = sys.argv[2]
environment = sys.argv[3]
fmt = sys.argv[4]

catalog_path = root / "docs" / "_canon" / "graph" / "ops" / "secrets_catalog.yaml"
catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}

gh_entries = [item for item in ((catalog.get("github_actions") or {}).get("secrets") or []) if isinstance(item, dict)]
runtime_entries = [item for item in (catalog.get("runtime_secrets") or []) if isinstance(item, dict)]

gh_entry = next((item for item in gh_entries if item.get("name") == secret_name), None)
runtime_entry = next((item for item in runtime_entries if item.get("name") == secret_name), None)

entry = runtime_entry or gh_entry
if entry is None:
    payload = {
        "status": "FAIL",
        "secret": secret_name,
        "environment": environment,
        "message": "secret nao catalogado no source graph operacional",
        "source_ref": "docs/_canon/graph/ops/secrets_catalog.yaml",
    }
    if fmt == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"FAIL: {payload['message']}: {secret_name}", file=sys.stderr)
    raise SystemExit(2)

rotation_ref = entry.get("rotation_ref")
rotation_command_ref = entry.get("rotation_command_ref")
rotation_period_days = entry.get("rotation_period_days")
rotation_actor = entry.get("rotation_actor")
rotate_on = entry.get("rotate_on") or []
storage_modes = (runtime_entry or {}).get("storage_modes") or {}
storage_mode = storage_modes.get(environment)

issues: list[str] = []
if not isinstance(rotation_ref, str) or not rotation_ref:
    issues.append("rotation_ref ausente")
if not isinstance(rotation_command_ref, str) or not rotation_command_ref:
    issues.append("rotation_command_ref ausente")
elif not (root / rotation_command_ref).exists():
    issues.append("rotation_command_ref inexistente")
if not isinstance(rotation_period_days, int) or rotation_period_days <= 0:
    issues.append("rotation_period_days invalido")
if not isinstance(rotation_actor, str) or not rotation_actor.strip():
    issues.append("rotation_actor ausente")
if not isinstance(rotate_on, list) or not rotate_on or not all(isinstance(item, str) and item.strip() for item in rotate_on):
    issues.append("rotate_on invalido")

status = "PASS" if not issues else "FAIL"
payload = {
    "status": status,
    "secret": secret_name,
    "environment": environment,
    "source_ref": "docs/_canon/graph/ops/secrets_catalog.yaml",
    "rotation_ref": rotation_ref,
    "rotation_command_ref": rotation_command_ref,
    "rotation_period_days": rotation_period_days,
    "rotation_actor": rotation_actor,
    "rotate_on": rotate_on,
    "storage_mode": storage_mode,
    "github_actions_environments": (gh_entry or {}).get("environments", []),
    "kind": (gh_entry or {}).get("kind"),
    "category": (runtime_entry or {}).get("category"),
    "notes": (gh_entry or {}).get("notes"),
}
if issues:
    payload["issues"] = issues

if fmt == "json":
    print(json.dumps(payload, ensure_ascii=False, indent=2))
else:
    if status == "PASS":
        print(
            f"PASS: {secret_name} [{environment}] rotate every {rotation_period_days} day(s) "
            f"by {rotation_actor} via {rotation_command_ref}"
        )
    else:
        print(f"FAIL: {secret_name} [{environment}] -> {', '.join(issues)}", file=sys.stderr)
        raise SystemExit(2)

if status != "PASS":
    raise SystemExit(2)
PY
