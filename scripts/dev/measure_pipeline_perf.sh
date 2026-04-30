#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

log_section() {
  printf '\n== %s ==\n' "$1"
}

run_timed() {
  local label="$1"
  shift
  log_section "$label"
  printf '+ %q' "$1"
  shift || true
  for arg in "$@"; do
    printf ' %q' "$arg"
  done
  printf '\n'
  time "$@"
}

log_section "HB Track pipeline performance measurement"
printf 'Repository: %s\n' "$ROOT"
printf 'Branch: %s\n' "$(git branch --show-current 2>/dev/null || echo unknown)"
printf 'Commit: %s\n' "$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf 'Python: %s\n' "$(python3 --version 2>&1)"
printf 'Node: %s\n' "$(node --version 2>/dev/null || echo unavailable)"
printf 'npm: %s\n' "$(npm --version 2>/dev/null || echo unavailable)"

run_timed "1) hb validate local" \
  python3 scripts/hb validate --profile local

run_timed "2) compile api policy check" \
  python3 scripts/contracts/validate/api/compile_api_policy.py --all --check

run_timed "3) contracts lint" \
  npm run contracts:lint

log_section "Done"
