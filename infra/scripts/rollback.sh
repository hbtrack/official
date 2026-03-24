#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# HB Track — rollback.sh
# Faz rollback para uma imagem anterior sem downtime.
#
# Uso: ./infra/scripts/rollback.sh --env <staging|production> --sha <git-sha>
#
# Exemplos:
#   ./infra/scripts/rollback.sh --env staging --sha abc1234
#   ./infra/scripts/rollback.sh --env production --sha def5678
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Argumentos ────────────────────────────────────────────────────────────────
ENV=""
SHA=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env)  ENV="$2";  shift 2 ;;
        --sha)  SHA="$2";  shift 2 ;;
        *) echo "Argumento desconhecido: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$ENV" || -z "$SHA" ]]; then
    echo "Erro: --env e --sha sao obrigatorios" >&2
    echo "Uso: $0 --env <staging|production> --sha <git-sha>" >&2
    exit 1
fi

if [[ "$ENV" != "staging" && "$ENV" != "production" ]]; then
    echo "Erro: --env deve ser 'staging' ou 'production'" >&2
    exit 1
fi

# ── Configuracao por ambiente ──────────────────────────────────────────────────
DEPLOY_DIR="/opt/hbtrack/${ENV}"
COMPOSE_FILE="${DEPLOY_DIR}/infra/docker-compose.prod.yml"
ENV_FILE="${DEPLOY_DIR}/.env"
REGISTRY="${REGISTRY:-ghcr.io/hbtrack}"
HEALTH_URL=""

if [[ "$ENV" == "staging" ]]; then
    HEALTH_URL="https://staging.handballtrack.app/health"
else
    HEALTH_URL="https://api.handballtrack.app/health"
fi

ROLLBACK_IMAGE="${REGISTRY}/hbtrack-backend:${SHA}"

echo ""
echo "== HB Track Rollback =="
echo "  Ambiente : ${ENV}"
echo "  SHA alvo : ${SHA}"
echo "  Imagem   : ${ROLLBACK_IMAGE}"
echo "  Diretorio: ${DEPLOY_DIR}"
echo ""

# ── Verificar que a imagem existe no registry ──────────────────────────────────
if ! docker manifest inspect "${ROLLBACK_IMAGE}" > /dev/null 2>&1; then
    echo "ERRO: Imagem nao encontrada no registry: ${ROLLBACK_IMAGE}" >&2
    echo "Verifique se o SHA esta correto e a imagem foi publicada." >&2
    exit 1
fi

# ── Atualizar IMAGE_TAG no .env do servidor ────────────────────────────────────
echo "[1/4] Atualizando IMAGE_TAG para ${SHA} em ${ENV_FILE}..."
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERRO: Arquivo .env nao encontrado em ${ENV_FILE}" >&2
    exit 1
fi

# Substituir IMAGE_TAG= no .env (cria backup antes)
cp "${ENV_FILE}" "${ENV_FILE}.bak"
sed -i "s|^IMAGE_TAG=.*|IMAGE_TAG=${SHA}|" "${ENV_FILE}"

# ── Pull da imagem de rollback ─────────────────────────────────────────────────
echo "[2/4] Baixando imagem ${ROLLBACK_IMAGE}..."
docker pull "${ROLLBACK_IMAGE}"

# ── Recriar containers afetados ───────────────────────────────────────────────
echo "[3/4] Reiniciando servicos com a imagem de rollback..."
cd "${DEPLOY_DIR}"
IMAGE_TAG="${SHA}" docker compose -f "${COMPOSE_FILE}" up -d --no-deps api celery_worker celery_beat

# ── Health check pos-rollback ─────────────────────────────────────────────────
echo "[4/4] Verificando saude da aplicacao (${HEALTH_URL})..."
MAX_ATTEMPTS=24
ATTEMPT=0

until curl -sf "${HEALTH_URL}" > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [[ $ATTEMPT -ge $MAX_ATTEMPTS ]]; then
        echo "FALHA: Health check nao passou em ${MAX_ATTEMPTS} tentativas." >&2
        echo "Restaurando .env original..."
        cp "${ENV_FILE}.bak" "${ENV_FILE}"
        echo "ROLLBACK FALHOU — correcao manual necessaria." >&2
        exit 1
    fi
    echo "  Aguardando... (${ATTEMPT}/${MAX_ATTEMPTS})"
    sleep 5
done

echo ""
echo "ROLLBACK CONCLUIDO com sucesso."
echo "  Imagem ativa: ${ROLLBACK_IMAGE}"
echo "  /health: OK"
