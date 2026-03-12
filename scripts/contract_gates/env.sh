#!/usr/bin/env bash
set -euo pipefail

# Canonical PATH bootstrap for Contract Gates tooling (CI/local).
# Goal: make Node-based CLIs in `node_modules/.bin` available as plain commands:
#   redocly, spectral, ajv

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export PATH="${REPO_ROOT}/node_modules/.bin:${PATH}"

