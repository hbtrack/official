#!/usr/bin/env bash
set -euo pipefail

# Canonical toolchain bootstrap for Contract Gates tooling (CI/local).
#
# Goals:
# - Ensure a **WSL-native** Node.js is available (avoid Windows interop via wrappers).
# - Prefer project-pinned CLIs in `node_modules/.bin` over global installs.
# - Prevent accidental use of `$HOME/bin/*` wrappers (commonly pointing to `node.exe`/`*.exe`).

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

_hbtrack_sanitize_path() {
  local wrapper_bin="${HOME}/bin"
  local out=""
  local IFS=":"
  for part in ${PATH}; do
    [[ -z "${part}" ]] && continue
    [[ "${part}" == "${wrapper_bin}" ]] && continue
    if [[ -z "${out}" ]]; then
      out="${part}"
    else
      out="${out}:${part}"
    fi
  done
  printf "%s" "${out}"
}

# 1) Remove known wrapper path from PATH (defensive).
export PATH="$(_hbtrack_sanitize_path)"

# 2) Ensure Node.js exists (prefer NVM) and is WSL-native.
if ! command -v node >/dev/null 2>&1; then
  export NVM_DIR="${NVM_DIR:-${HOME}/.nvm}"
  if [[ -s "${NVM_DIR}/nvm.sh" ]]; then
    # shellcheck source=/dev/null
    . "${NVM_DIR}/nvm.sh"
    if [[ -f "${REPO_ROOT}/.nvmrc" ]]; then
      (cd "${REPO_ROOT}" && nvm use --silent >/dev/null 2>&1) || true
    else
      nvm use --silent default >/dev/null 2>&1 || true
    fi
  fi
fi

NODE_PATH_BIN="$(command -v node || true)"
if [[ -z "${NODE_PATH_BIN}" ]]; then
  echo "ERROR: Node.js não encontrado no PATH (nem via NVM)." >&2
  echo "Dica: instale via nvm e rode: source scripts/contract_gates/env.sh" >&2
  return 2 2>/dev/null || exit 2
fi

if [[ "${NODE_PATH_BIN}" == *"node.exe"* || "${NODE_PATH_BIN}" == /mnt/* ]]; then
  echo "ERROR: Node resolve para binário Windows/Interop: ${NODE_PATH_BIN}" >&2
  echo "Remova wrappers em ${HOME}/bin do PATH e use Node WSL-native (nvm)." >&2
  return 3 2>/dev/null || exit 3
fi

# 3) Expor CLIs do projeto sem sobrescrever runtimes globais (node/npm).
#    Nota: em caso de `node_modules/` incompleto, preferimos manter os binários globais (NVM)
#    como default; o pipeline de contract gates tem fallback explícito para CLIs globais quando
#    os bins locais falham.
if [[ ":${PATH}:" != *":${REPO_ROOT}/node_modules/.bin:"* ]]; then
  export PATH="${PATH}:${REPO_ROOT}/node_modules/.bin"
fi
