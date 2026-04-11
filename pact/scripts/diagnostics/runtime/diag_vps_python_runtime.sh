#!/bin/bash
###############################################################################
# diag_vps_python_runtime.sh
#
# Descrição:
#   Script de diagnóstico que verifica objetivamente:
#   1. Versão do Python no venv que o systemd está usando
#   2. Comando real do systemctl (ExecStart)
#   3. Python do processo em execução (via /proc)
#   4. Compatibilidade do código HB Track com o runtime da VPS
#
# Side-effects: FS_READ, DB_READ (postgres connection test)
#
# Exit codes:
#   0 = OK (todas as verificações passaram)
#   1 = AVISO (alguma verificação falhou, mas não crítica)
#   2 = ERRO (verificação crítica falhou)
#
# Uso:
#   1. Copie este script para a VPS:
#      scp scripts/diagnostics/runtime/diag_vps_python_runtime.sh deploy@VPS:/tmp/
#
#   2. Execute na VPS:
#      chmod +x /tmp/diag_vps_python_runtime.sh
#      /tmp/diag_vps_python_runtime.sh
#
# Origem:
#   Criado para eliminar suposições sobre Python 3.8 vs 3.11+ no ambiente VPS.
#   Referência: protocolos de validação.md - seção verificação runtime Python.
#
###############################################################################

set -u  # Abort on undefined variables
# Não usar set -e para controlar exit codes manualmente

# ============================================================================
# Configuração
# ============================================================================

SERVICE_NAME="hbtrack-backend.service"
VENV_PATH="/home/deploy/hbtrack-backend/current/venv"
APP_PATH="/home/deploy/hbtrack-backend/current/app"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

EXIT_CODE=0

# ============================================================================
# Funções
# ============================================================================

log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

log_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    if [ $EXIT_CODE -eq 0 ]; then
        EXIT_CODE=1
    fi
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    EXIT_CODE=2
}

# ============================================================================
# 1. Verificar versão do Python no venv do systemd
# ============================================================================

log_section "1. Python do venv (usado pelo systemd)"

if [ ! -f "${VENV_PATH}/bin/python" ]; then
    log_error "Venv Python não encontrado em ${VENV_PATH}/bin/python"
else
    VENV_PYTHON="${VENV_PATH}/bin/python"
    
    echo "Python executable: ${VENV_PYTHON}"
    
    PYTHON_VERSION=$("${VENV_PYTHON}" -c "import sys; print(sys.version)" 2>&1)
    PYTHON_EXECUTABLE=$("${VENV_PYTHON}" -c "import sys; print(sys.executable)" 2>&1)
    
    echo ""
    echo "sys.executable:"
    echo "  ${PYTHON_EXECUTABLE}"
    echo ""
    echo "sys.version:"
    echo "  ${PYTHON_VERSION}"
    
    # Extrair major.minor
    PYTHON_MAJOR_MINOR=$("${VENV_PYTHON}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1)
    echo ""
    echo "Major.Minor: ${PYTHON_MAJOR_MINOR}"
    
    # Verificar se é 3.8
    if echo "${PYTHON_MAJOR_MINOR}" | grep -q "^3\.8"; then
        log_warning "Venv está usando Python 3.8 (pode ter incompatibilidades com código 3.11+)"
    else
        log_ok "Venv está usando Python ${PYTHON_MAJOR_MINOR}"
    fi
fi

# ============================================================================
# 2. Confirmar comando do systemd (ExecStart)
# ============================================================================

log_section "2. Comando systemd (ExecStart)"

if ! systemctl list-unit-files | grep -q "${SERVICE_NAME}"; then
    log_error "Serviço ${SERVICE_NAME} não encontrado no systemd"
else
    echo "Unit file completo:"
    echo ""
    systemctl cat "${SERVICE_NAME}"
    
    echo ""
    echo "ExecStart isolado:"
    systemctl show "${SERVICE_NAME}" -p ExecStart --no-pager
    
    # Verificar se ExecStart usa o venv correto
    EXEC_START=$(systemctl show "${SERVICE_NAME}" -p ExecStart --no-pager)
    
    if echo "${EXEC_START}" | grep -q "${VENV_PATH}"; then
        log_ok "ExecStart usa o venv esperado (${VENV_PATH})"
    else
        log_warning "ExecStart NÃO menciona ${VENV_PATH}"
    fi
    
    # Verificar flags suspeitas (gunicorn vs uvicorn)
    if echo "${EXEC_START}" | grep -qE "\-\-bind|\-\-worker-class"; then
        log_warning "ExecStart contém flags de gunicorn (--bind, --worker-class) mas deveria usar uvicorn"
    fi
fi

# ============================================================================
# 3. Python do processo em execução (/proc inspection)
# ============================================================================

log_section "3. Python do processo em execução"

if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
    log_warning "Serviço ${SERVICE_NAME} não está ativo"
else
    echo "Status do serviço:"
    systemctl status "${SERVICE_NAME}" --no-pager --lines=20
    
    echo ""
    
    # Pegar PID do MainPID
    MAIN_PID=$(systemctl show "${SERVICE_NAME}" -p MainPID --value)
    
    if [ -z "${MAIN_PID}" ] || [ "${MAIN_PID}" = "0" ]; then
        log_warning "Não foi possível obter MainPID do serviço"
    else
        echo "MainPID: ${MAIN_PID}"
        
        if [ -L "/proc/${MAIN_PID}/exe" ]; then
            PROC_PYTHON=$(readlink -f "/proc/${MAIN_PID}/exe")
            echo "Python em execução: ${PROC_PYTHON}"
            
            if echo "${PROC_PYTHON}" | grep -q "${VENV_PATH}"; then
                log_ok "Processo está usando Python do venv esperado"
            else
                log_warning "Processo está usando Python diferente do venv: ${PROC_PYTHON}"
            fi
        else
            log_warning "/proc/${MAIN_PID}/exe não encontrado"
        fi
        
        # Mostrar cmdline
        if [ -f "/proc/${MAIN_PID}/cmdline" ]; then
            echo ""
            echo "Cmdline do processo:"
            tr '\0' ' ' < "/proc/${MAIN_PID}/cmdline"
            echo ""
        fi
    fi
fi

# ============================================================================
# 4. Compatibilidade do código HB Track com runtime da VPS
# ============================================================================

log_section "4. Compatibilidade do código com runtime"

if [ ! -f "${VENV_PYTHON}" ]; then
    log_error "Não é possível testar compatibilidade sem venv Python"
else
    # A) Compilar tudo (detecta match/case, sintaxe inválida)
    echo "A) Compilando código (detecção de sintaxe incompatível)..."
    
    if [ ! -d "${APP_PATH}" ]; then
        log_error "Diretório ${APP_PATH} não encontrado"
    else
        COMPILE_OUTPUT=$("${VENV_PYTHON}" -m compileall -q "${APP_PATH}" 2>&1)
        COMPILE_EXIT=$?
        
        if [ $COMPILE_EXIT -eq 0 ]; then
            log_ok "Código compila sem erros de sintaxe"
        else
            log_error "Código FALHOU ao compilar:"
            echo "${COMPILE_OUTPUT}"
        fi
    fi
    
    # B) Importar entrypoint (detecta type hints/stdlib incompatíveis)
    echo ""
    echo "B) Importando entrypoint (app.main)..."
    
    # Precisamos do PYTHONPATH correto
    OLD_PYTHONPATH="${PYTHONPATH:-}"
    export PYTHONPATH="/home/deploy/hbtrack-backend/current:${PYTHONPATH:-}"
    
    IMPORT_OUTPUT=$("${VENV_PYTHON}" -c "import importlib; importlib.import_module('app.main'); print('IMPORT_OK')" 2>&1)
    IMPORT_EXIT=$?
    
    if [ $IMPORT_EXIT -eq 0 ] && echo "${IMPORT_OUTPUT}" | grep -q "IMPORT_OK"; then
        log_ok "Entrypoint app.main importado com sucesso"
    else
        log_error "Falha ao importar app.main:"
        echo "${IMPORT_OUTPUT}"
    fi
    
    # Restaurar PYTHONPATH
    export PYTHONPATH="${OLD_PYTHONPATH}"
    
    # C) Verificar dependências
    echo ""
    echo "C) Verificando dependências (pip check)..."
    
    PIP_CHECK_OUTPUT=$("${VENV_PYTHON}" -m pip check 2>&1)
    PIP_CHECK_EXIT=$?
    
    if [ $PIP_CHECK_EXIT -eq 0 ]; then
        log_ok "Todas as dependências estão satisfeitas"
    else
        log_warning "Dependências com problemas:"
        echo "${PIP_CHECK_OUTPUT}"
    fi
fi

# ============================================================================
# 5. Logs do journald (evidência de runtime)
# ============================================================================

log_section "5. Logs recentes do serviço (journalctl)"

if systemctl list-unit-files | grep -q "${SERVICE_NAME}"; then
    echo "Últimos 30 logs do serviço:"
    echo ""
    journalctl -u "${SERVICE_NAME}" -n 30 --no-pager
    
    echo ""
    echo "Filtrando por 'RUNTIME' ou 'sys.executable':"
    journalctl -u "${SERVICE_NAME}" --no-pager | grep -iE "RUNTIME|sys\.executable|sys\.version" | tail -20 || echo "(nenhum log de RUNTIME encontrado)"
fi

# ============================================================================
# Resumo Final
# ============================================================================

log_section "Resumo"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Todas as verificações passaram${NC}"
elif [ $EXIT_CODE -eq 1 ]; then
    echo -e "${YELLOW}⚠ Algumas verificações geraram avisos - revise acima${NC}"
else
    echo -e "${RED}✗ Verificações críticas falharam - AÇÃO NECESSÁRIA${NC}"
fi

echo ""
echo "Exit code: ${EXIT_CODE}"

exit ${EXIT_CODE}
