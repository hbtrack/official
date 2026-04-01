#!/usr/bin/env bash
set -euo pipefail

# B8-002 — Este script injeta variáveis de ambiente de aplicação (Django) em .env.
# PACT_BROKER_BASE_URL e PACT_BROKER_TOKEN NÃO são injetados por este script.
# Essas variáveis são CI-only e passadas via GitHub Actions vars/secrets ao job
# `contract-conformance` do deploy.yml (ADR-025).

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <staging|production> <output-path> <image-tag>" >&2
  exit 2
fi

ENV_NAME="$1"
OUTPUT_PATH="$2"
IMAGE_TAG="$3"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$(dirname "$OUTPUT_PATH")"

python3 "$ROOT/scripts/deploy/render_env_from_contract.py" \
  --env "$ENV_NAME" \
  --output "$OUTPUT_PATH" \
  --set "IMAGE_TAG=$IMAGE_TAG"

chmod 600 "$OUTPUT_PATH"
echo "OK: ambiente '$ENV_NAME' injetado em $OUTPUT_PATH"
