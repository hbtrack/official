#!/usr/bin/env bash
set -euo pipefail

# HB Track — WSL/Linux Environment Setup (WSL-native + hermetic)
#
# Uso recomendado:
#   source ./setup-env.sh
#
# Objetivo:
# - carregar NVM (se disponível)
# - garantir Node WSL-native (evitar wrappers Windows em $HOME/bin)
# - expor CLIs do projeto via node_modules/.bin

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Este script deve ser 'source'd para afetar o ambiente atual:" >&2
  echo "  source ./setup-env.sh" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Centraliza a lógica de toolchain no bootstrap canônico dos contract gates.
# shellcheck source=/dev/null
source "${REPO_ROOT}/scripts/contract_gates/env.sh"

echo "✓ Environment ready:"
echo "  Node  : $(node --version) ($(command -v node))"
echo "  npm   : $(npm --version) ($(command -v npm))"
echo "  Python: $(python3 --version)"
