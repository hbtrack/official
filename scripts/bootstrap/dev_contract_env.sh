#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${HB_CONTRACT_VENV_DIR:-${REPO_ROOT}/.venv-contract}"
VENV_PY="${VENV_DIR}/bin/python"
REQ_FILE="${REPO_ROOT}/scripts/bootstrap/requirements-contract-dev.txt"
LOCK_FILE="${REPO_ROOT}/package-lock.json"
STAMP_FILE="${VENV_DIR}/.node_modules.lock.sha256"
OASDIFF_VERSION="${HB_OASDIFF_VERSION:-1.12.3}"
OASDIFF_DEST="${VENV_DIR}/bin/oasdiff"

log() {
  printf '%s\n' "$*"
}

die() {
  printf '❌ %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  local cmd="$1"
  command -v "${cmd}" >/dev/null 2>&1 || die "Comando obrigatório ausente: ${cmd}"
}

create_virtualenv() {
  local tmp_log
  tmp_log="$(mktemp)"
  if python3 -m venv "${VENV_DIR}" >"${tmp_log}" 2>&1; then
    rm -f "${tmp_log}"
    return 0
  fi
  if python3 -m virtualenv --version >/dev/null 2>&1; then
    log "python3 -m venv indisponivel; tentando fallback com virtualenv ..."
    if python3 -m virtualenv "${VENV_DIR}" >>"${tmp_log}" 2>&1; then
      rm -f "${tmp_log}"
      return 0
    fi
  fi
  cat "${tmp_log}" >&2
  rm -f "${tmp_log}"
  die "Nao foi possivel criar o virtualenv local. Instale python3-venv/ensurepip ou execute: python3 -m pip install --user virtualenv"
}

venv_has_pip() {
  [[ -x "${VENV_PY}" ]] || return 1
  "${VENV_PY}" -m pip --version >/dev/null 2>&1
}

node_tools_ready() {
  local tool
  for tool in redocly spectral asyncapi; do
    [[ -x "${REPO_ROOT}/node_modules/.bin/${tool}" ]] || return 1
  done
}

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
    return 0
  fi
  shasum -a 256 "$1" | awk '{print $1}'
}

ensure_python_modules() {
  "${VENV_PY}" - "$@" <<'PY'
import importlib.util
import sys

missing = [name for name in sys.argv[1:] if importlib.util.find_spec(name) is None]
if missing:
    print("Módulos Python ausentes:", ", ".join(missing), file=sys.stderr)
    raise SystemExit(1)
PY
}

verify_tool() {
  local tool="$1"
  command -v "${tool}" >/dev/null 2>&1 || die "Ferramenta obrigatória ausente no PATH após bootstrap: ${tool}"
}

ensure_oasdiff() {
  if command -v oasdiff >/dev/null 2>&1; then
    return 0
  fi

  need_cmd curl
  need_cmd tar

  if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
    die "Instalação automática do oasdiff suportada apenas em Linux x86_64. Configure manualmente oasdiff ${OASDIFF_VERSION}."
  fi

  local tmp_dir archive extract_dir resolved
  tmp_dir="$(mktemp -d)"
  archive="${tmp_dir}/oasdiff.tar.gz"
  extract_dir="${tmp_dir}/extract"
  mkdir -p "${extract_dir}" "$(dirname "${OASDIFF_DEST}")"

  log "Instalando oasdiff ${OASDIFF_VERSION} em ${OASDIFF_DEST} ..."
  curl -fsSL "https://github.com/oasdiff/oasdiff/releases/download/v${OASDIFF_VERSION}/oasdiff_${OASDIFF_VERSION}_linux_amd64.tar.gz" -o "${archive}"
  tar -xzf "${archive}" -C "${extract_dir}"
  resolved="$(find "${extract_dir}" -type f -name oasdiff | head -n1)"
  [[ -n "${resolved}" ]] || die "Nao foi possivel localizar o binario do oasdiff no pacote baixado."
  cp "${resolved}" "${OASDIFF_DEST}"
  chmod 0755 "${OASDIFF_DEST}"
  rm -rf "${tmp_dir}"
}

log "══ HB Track Contract Dev Bootstrap ══"
need_cmd python3
need_cmd node
need_cmd npm

if [[ ! -f "${REQ_FILE}" ]]; then
  die "Manifesto de bootstrap ausente: ${REQ_FILE}"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  log "Criando virtualenv local em ${VENV_DIR} ..."
  create_virtualenv
elif ! venv_has_pip; then
  if [[ "${VENV_DIR}" == "${REPO_ROOT}/.venv-contract" ]]; then
    log "Virtualenv local inconsistente; recriando ${VENV_DIR} ..."
    rm -rf "${VENV_DIR}"
    create_virtualenv
  else
    die "Virtualenv existente sem pip funcional: ${VENV_DIR}. Remova o diretório ou aponte HB_CONTRACT_VENV_DIR para outro local."
  fi
fi

log "Verificando pip no virtualenv local ..."
venv_has_pip || die "pip ausente no virtualenv local: ${VENV_PY}"
export PATH="${VENV_DIR}/bin:${PATH}"

log "Instalando dependências Python de governança ..."
PIP_DISABLE_PIP_VERSION_CHECK=1 "${VENV_PY}" -m pip install -r "${REQ_FILE}"

current_lock_hash="$(hash_file "${LOCK_FILE}")"
stored_lock_hash=""
if [[ -f "${STAMP_FILE}" ]]; then
  stored_lock_hash="$(cat "${STAMP_FILE}")"
fi

if [[ ! -d "${REPO_ROOT}/node_modules" || "${current_lock_hash}" != "${stored_lock_hash}" || ! node_tools_ready ]]; then
  log "Sincronizando dependências Node com npm ci ..."
  (cd "${REPO_ROOT}" && npm ci)
  printf '%s' "${current_lock_hash}" > "${STAMP_FILE}"
else
  log "Dependências Node já estão em sincronia com package-lock.json."
fi

# shellcheck source=/dev/null
source "${REPO_ROOT}/scripts/contract_gates/env.sh"
ensure_oasdiff

log "Verificando módulos Python mínimos ..."
ensure_python_modules pytest schemathesis yaml jsonschema

log "Verificando toolchain de contratos ..."
verify_tool oasdiff
verify_tool redocly
verify_tool spectral
verify_tool asyncapi

log "✅ PASS — ambiente local pronto."
log "Python de contratos: ${VENV_PY}"
