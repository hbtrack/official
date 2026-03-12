#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/env.sh"

node -v
npm -v
redocly --version
spectral --version
ajv help

