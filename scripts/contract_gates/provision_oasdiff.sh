#!/usr/bin/env bash
set -euo pipefail

. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

if ! command -v go >/dev/null 2>&1; then
  echo "Go runtime não encontrado no PATH. Instale Go e reexecute este script." >&2
  exit 1
fi

echo "Instalando oasdiff via 'go install'..."
# O path canônico mudou de tufin/oasdiff -> oasdiff/oasdiff
go install github.com/oasdiff/oasdiff@latest

echo "Verificando oasdiff..."
oasdiff version
