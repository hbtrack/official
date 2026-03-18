#!/bin/bash
# audit-cli.sh — Referência Rápida para Auditorias
# 
# Uso:
#   ./scripts/run/audit-cli.sh dc           # Domain Completeness (todos)
#   ./scripts/run/audit-cli.sh dc wellness   # Domain Completeness (wellness)
#   ./scripts/run/audit-cli.sh ce           # Context Efficiency
#   ./scripts/run/audit-cli.sh both         # Ambas (sequencial)
#   ./scripts/run/audit-cli.sh status       # Status dos workflows (GH API)

set -e

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUDIT_DIR="$WORKSPACE_ROOT/scripts/audit"

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Help
show_help() {
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║              AUDIT CLI — HB TRACK Auditorias de Qualidade                  ║
╚════════════════════════════════════════════════════════════════════════════╝

USAGE:
  audit-cli.sh <command> [module]

COMMANDS:
  dc [module]   Domain Completeness Audit
                  module (opcional): wellness, teams, seasons, etc.
                  Se omitido: testa todos 16 módulos
  
  ce            Context Efficiency Audit
                  Valida boot mínimo (orçamento + alcançabilidade)
  
  both          Ambas auditorias (sequencial: DC → CE)
  
  status        Mostrar status dos últimos workflows (GitHub Actions)
  
  help          Mostrar esta mensagem

EXEMPLOS:
  # Domain Completeness — todos os módulos
  audit-cli.sh dc
  
  # Domain Completeness — apenas wellness
  audit-cli.sh dc wellness
  
  # Context Efficiency
  audit-cli.sh ce
  
  # Ambas
  audit-cli.sh both
  
  # Ver status no GitHub
  audit-cli.sh status

OUTPUTS:
  ✓ _reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.md
  ✓ _reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.json
  ✓ _reports/CONTEXT_EFFICIENCY_AUDIT_*.md
  ✓ _reports/CONTEXT_EFFICIENCY_AUDIT_*.json

EOF
}

# Executar DC audit
run_dc() {
    module="$1"
    
    if [ -z "$module" ]; then
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}  Domain Completeness Audit — Todos os 16 módulos${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
        python "$AUDIT_DIR/run_all_modules_audit.py"
    else
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}  Domain Completeness Audit — Módulo: $module${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
        python "$AUDIT_DIR/run_domain_completeness.py" "$module"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Domain Completeness PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ Domain Completeness FAIL${NC}"
        return 1
    fi
}

# Executar CE audit
run_ce() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Context Efficiency Audit — Boot Mínimo${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    
    python "$AUDIT_DIR/run_context_efficiency_audit.py"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Context Efficiency PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ Context Efficiency FAIL${NC}"
        return 1
    fi
}

# Executar ambas
run_both() {
    echo -e "${YELLOW}▶ Iniciando auditorias combinadas...${NC}"
    echo ""
    
    run_dc
    dc_result=$?
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    run_ce
    ce_result=$?
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ $dc_result -eq 0 ] && [ $ce_result -eq 0 ]; then
        echo -e "${GREEN}✓ Todas as auditorias PASSARAM${NC}"
        return 0
    else
        echo -e "${RED}✗ Uma ou mais auditorias falharam${NC}"
        [ $dc_result -ne 0 ] && echo -e "  ${RED}❌ Domain Completeness${NC}"
        [ $ce_result -ne 0 ] && echo -e "  ${RED}❌ Context Efficiency${NC}"
        return 1
    fi
}

# Status dos workflows (requer gh CLI)
show_status() {
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}✗ GitHub CLI não encontrado${NC}"
        echo "  Instale via: https://cli.github.com/"
        return 1
    fi
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Status dos Workflows (GitHub Actions)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    
    echo ""
    echo "Domain Completeness Audit:"
    gh run list -w domain-completeness-audit.yml --limit 5 --json status,updatedAt,conclusion --template '{{range .}}{{.status}}\t{{.conclusion}}\t{{.updatedAt}}{{"\n"}}{{end}}'
    
    echo ""
    echo "Context Efficiency Audit:"
    gh run list -w context-efficiency-audit.yml --limit 5 --json status,updatedAt,conclusion --template '{{range .}}{{.status}}\t{{.conclusion}}\t{{.updatedAt}}{{"\n"}}{{end}}'
}

# Main
main() {
    command="${1:-help}"
    module="$2"
    
    # Validar comando
    case "$command" in
        dc)
            run_dc "$module"
            ;;
        ce)
            run_ce
            ;;
        both)
            run_both
            ;;
        status)
            show_status
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo -e "${RED}Comando desconhecido: $command${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
