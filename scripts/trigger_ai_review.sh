#!/usr/bin/env bash
# scripts/trigger_ai_review.sh
# Força re-trigger do ai-pr-review em PR já aberto via empty commit
# Uso: bash scripts/trigger_ai_review.sh <PR_NUMBER>
# Pré-requisito: gh autenticado, estar na branch do PR
set -euo pipefail

PR="${1:?Informe o número do PR. Uso: bash scripts/trigger_ai_review.sh <PR>}"
REPO="${GITHUB_REPOSITORY:-hbtrack/official}"

# Obter branch do PR
BRANCH=$(GH_TOKEN="" gh pr view "${PR}" --repo "${REPO}" --json headRefName --jq '.headRefName' 2>/dev/null || echo "")

if [ -z "${BRANCH}" ]; then
    echo "ERRO: Não foi possível obter a branch do PR #${PR}."
    echo "Verifique: gh auth status"
    exit 1
fi

echo "PR #${PR} — branch: ${BRANCH}"

# Verificar se estamos na branch correta
CURRENT_BRANCH=$(git branch --show-current)
if [ "${CURRENT_BRANCH}" != "${BRANCH}" ]; then
    echo "Mudando para branch ${BRANCH}..."
    git checkout "${BRANCH}" || { echo "ERRO: checkout falhou"; exit 1; }
fi

# Empty commit para gerar evento 'synchronize' que trigga o workflow
git commit --allow-empty -m "ci: trigger ai-review for PR #${PR} [skip ci-contracts]"
git push

echo ""
echo "Empty commit pushado em ${BRANCH}"
echo "O workflow ai-pr-review deve trigar em instantes."
echo "Acompanhar: gh run list --repo ${REPO} --limit 5"
