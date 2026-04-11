#!/bin/bash
# Git pre-commit hook: Bloquear novos arquivos com authority language fora de allowlist
# Instalação: git config core.hooksPath scripts/git-hooks

set -e

# Padrões de allowlist (canonical paths)
ALLOWLIST_PATTERNS=(
    "docs/_canon/"
    ".contract_driven/"
    "contracts/"
    "generated/"
    "_reports/"
    "docs/hbtrack/modulos/"
)

# Keywords de autoridade
AUTHORITY_KEYWORDS=(
    "SSOT"
    "source of truth"
    "fonte soberana"
    "canônico"
    "normativo"
    "autoridade"
    "soberano"
)

# Excludidas (por razão)
# - _archive/ — histórico, não workspace ativo
# - node_modules/ — dependências externas
# - .git/ — metadados

echo "🔍 Validando C4: Nenhum arquivo novo com authority language fora de allowlist..."

VIOLATIONS=0

# Verificar arquivos staged (.md)
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.md$'); do
    FILE_PATH="$file"
    
    # Excluções  
    if [[ "$FILE_PATH" =~ ^_archive/ ]] || [[ "$FILE_PATH" =~ node_modules/ ]]; then
        continue
    fi
    
    # Verificar se está em allowlist
    IN_ALLOWLIST=0
    for pattern in "${ALLOWLIST_PATTERNS[@]}"; do
        if [[ "$FILE_PATH" =~ ^$pattern ]]; then
            IN_ALLOWLIST=1
            break
        fi
    done
    
    # Se fora de allowlist, procurar por authority language
    if [ $IN_ALLOWLIST -eq 0 ]; then
        FILE_CONTENT=$(git show ":$file")
        
        for keyword in "${AUTHORITY_KEYWORDS[@]}"; do
            if echo "$FILE_CONTENT" | grep -qiE "\b${keyword}\b"; then
                echo "  ❌ $FILE_PATH"
                echo "     Contém keyword de autoridade fora de allowlist: '$keyword'"
                echo "     Mude para: docs/_canon/ ou .contract_driven/"
                VIOLATIONS=$((VIOLATIONS + 1))
            fi
        done
    fi
done

if [ $VIOLATIONS -gt 0 ]; then
    echo ""
    echo "❌ PRÉ-COMMIT FALHOU: $VIOLATIONS arquivo(s) com authority language fora de allowlist"
    echo ""
    echo "Solução:"
    echo "1. Mova arquivo para docs/_canon/ ou .contract_driven/"
    echo "2. Ou remova keywords de autoridade (SSOT, canônico, soberano, etc)"
    echo "3. git add .../arquivo.md && git commit novamente"
    exit 1
fi

echo "✅ C4 validação passou: Nenhum novo intrusivo detectado"
exit 0
