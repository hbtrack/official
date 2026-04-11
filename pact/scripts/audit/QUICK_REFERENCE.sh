#!/usr/bin/env bash
# Quick reference: Domain Completeness Auditor - Commands & Usage

set -e

echo "════════════════════════════════════════════════════════════════════════════════"
echo "DOMAIN COMPLETENESS AUDITOR — QUICK REFERENCE"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# 1. Audit single module
echo "1. AUDIT MÓDULO ÚNICO"
echo "─────────────────────────"
echo "  python scripts/audit/run_domain_completeness.py"
echo ""
echo "  Testa: wellness (padrão)"
echo "  Saída: _reports/DOMAIN_COMPLETENESS_AUDIT_YYYYMMDD_HHMMSS.{md,json}"
echo ""

# 2. Audit all modules
echo "2. AUDIT TODOS OS 16 MÓDULOS"
echo "──────────────────────────────"
echo "  python scripts/audit/run_all_modules_audit.py"
echo ""
echo "  Testa: ai_ingestion, analytics, audit, competitions, exercises, identity_access,"
echo "         matches, medical, notifications, reports, scout, seasons, teams, training,"
echo "         users, wellness"
echo ""
echo "  Saída: "
echo "    - _reports/DOMAIN_COMPLETENESS_ALL_MODULES_YYYYMMDD_HHMMSS.md"
echo "    - _reports/DOMAIN_COMPLETENESS_ALL_MODULES_YYYYMMDD_HHMMSS.json"
echo ""

# 3. GitHub Actions
echo "3. CI/CD GITHUB ACTIONS"
echo "────────────────────────"
echo "  Trigger: Toda segunda-feira 09:00 UTC"
echo "  Manual:  Actions → Domain Completeness Audit → Run workflow"
echo ""
echo "  Workflow: .github/workflows/domain-completeness-audit.yml"
echo "  Status:   Automaticamente commentado em PRs"
echo ""

# 4. View latest reports
echo "4. VER RELATÓRIOS GERADOS"
echo "──────────────────────────"
echo "  # Último audit individual"
echo "  cat \$(ls -t _reports/DOMAIN_COMPLETENESS_AUDIT_*.md | head -1)"
echo ""
echo "  # Último audit de 16 módulos"
echo "  cat \$(ls -t _reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.md | head -1)"
echo ""

# 5. JSON parsing
echo "5. PARSER JSONPYTHON"
echo "─────────────────────"
echo "  python -c \""
echo "  import json"
echo "  with open('_reports/DOMAIN_COMPLETENESS_ALL_MODULES_*.json') as f:"
echo "    data = json.load(f)"
echo "    for module, result in data.items():"
echo "      print(f'{module}: {\"PASS\" if result.get(\"passed\") else \"FAIL\"}')"
echo "  \""
echo ""

# 6. Criteria explanation
echo "6. CRITÉRIOS (DC1-DC5)"
echo "──────────────────────"
echo "  DC1: Fase 0 determinística (consistência de saída)"
echo "  DC2: Artefatos obrigatórios detectados"
echo "  DC3: Boundary cross-module detectado"
echo "  DC4: Sem lacunas silenciosas"
echo "  DC5: Handoff materializável (zero inferência)"
echo ""

# 7. If audit fails
echo "7. SE AUDIT FALHAR"
echo "──────────────────"
echo "  1. Revisar relatório: cat _reports/DOMAIN_COMPLETENESS_*.md"
echo "  2. Identificar critério FAIL (DC1-DC5)"
echo "  3. Consultar guia de iteração:"
echo "     docs/guias/DOMAIN_COMPLETENESS_AUDITOR.md"
echo "  4. Aplicar fix conforme prompt:"
echo "     .contract_driven/agent_prompts/audit_domain_completeness.prompt.md §8"
echo "  5. Re-run audit para validar"
echo ""

# 8. Documentation
echo "8. DOCUMENTAÇÃO"
echo "────────────────"
echo "  • Guia de uso:"
echo "    docs/guias/DOMAIN_COMPLETENESS_AUDITOR.md"
echo ""
echo "  • CI/CD integration:"
echo "    docs/guias/CI_CD_DOMAIN_COMPLETENESS_INTEGRATION.md"
echo ""
echo "  • Especificação completa:"
echo "    .contract_driven/agent_prompts/audit_domain_completeness.prompt.md"
echo ""

# 9. Current status
echo "9. STATUS ATUAL"
echo "────────────────"
echo "  ✅ Executor: Operacional"
echo "  ✅ 16 módulos: 100% PASS"
echo "  ✅ CI/CD: Configurado (semanal + manual)"
echo "  ✅ Documentação: Completa"
echo ""

# 10. Files
echo "10. ARQUIVOS CHAVE"
echo "───────────────────"
echo "  scripts/audit/run_domain_completeness.py (425 L)"
echo "  scripts/audit/run_all_modules_audit.py (220 L)"
echo "  .github/workflows/domain-completeness-audit.yml"
echo "  docs/guias/DOMAIN_COMPLETENESS_AUDITOR.md"
echo "  docs/guias/CI_CD_DOMAIN_COMPLETENESS_INTEGRATION.md"
echo ""

echo "════════════════════════════════════════════════════════════════════════════════"
echo "Para mais información: cat docs/guias/DOMAIN_COMPLETENESS_AUDITOR.md"
echo "════════════════════════════════════════════════════════════════════════════════"
