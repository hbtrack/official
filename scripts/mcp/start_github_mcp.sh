#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI nao encontrado no PATH." >&2
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "npx nao encontrado no PATH." >&2
  exit 1
fi

TOKEN="${GITHUB_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  TOKEN="$(gh auth token 2>/dev/null || true)"
fi

if [ -z "$TOKEN" ]; then
  echo "Nenhum token GitHub disponivel. Execute 'gh auth login' ou exporte GITHUB_TOKEN." >&2
  exit 1
fi

export GITHUB_TOKEN="$TOKEN"
exec npx -y @modelcontextprotocol/server-github "$@"
