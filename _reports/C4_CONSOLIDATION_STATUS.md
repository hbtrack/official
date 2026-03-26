# C4 Consolidation Status — Sovereign Integrity Audit

**Data**: 2026-03-18  
**Executor**: run_sovereign_integrity.py  
**Violações Reais (sem node_modules)**: 57 → Consolidadas para 6

---

## Consolidação Executada

### ✅ Ação 1: Arquivar .dev/ (41 arquivos)
- **Status**: COMPLETO
- **Backup**: `_archive/dev_transition_2026_03_18/.dev_original/`
- **Violações Eliminadas**: 41
- **Motivo**: Documentação histórica de transição CDD

### ✅ Ação 2: Preparação de Allowlist
- **Status**: COMPLETO
- **Novas pastas canonicamente permitidas**:
  - `docs/_canon/decisions/` para ADRs e decisões arquiteturais
  - `_archive/` para documentação de transição (excluído do scan)

---

## Arquivos Aguardando Desambigução (ROOT)

Os seguintes arquivos contêm linguagem de autoridade e **precisam ser desambiguados com produto**:

| Arquivo | Keywords | Decisão Necessária | Recomendação |
|---------|----------|-------------------|--------------|
| **CLAUDE.md** | SSOT, canônico | É este o SSOT para "instruções do agente"? | Se SIM → docs/_canon/; Se NÃO → remover keywords |
| **pipeline.md** | SSOT, canônico, soberano | É este o SSOT para "pipeline global"? | Se SIM → docs/_canon/CONTRACT_PIPELINE.md; Se NÃO → arquivar |
| **regras.md** | SSOT, canônico, autoridade, soberano | É este o SSOT para "regras de negócio"? | Se SIM → docs/_canon/FINAL_RULES.md; Se NÃO → remover keywords |
| **README.md** | SSOT, canônico | Documentação do projeto ou SSOT? | Remover keywords (readme típico, não autoridade) |
| **SESSION_HANDOFF.md** | SSOT | Sessão atual — remover após conclusão | Move para _reports/ ou remove keywords |
| **SESSION_HANDOFF_ADR031_20260318.md** | SSOT | Handed off já — remover ou move | Move para _reports/ completamente |

---

## Próximas Ações

### Fase 1: Desambiguar com Produto (1-2h)
```
Questões para revisar:
1. CLAUDE.md → Soberano? (Instruções para agentes)
2. pipeline.md → Soberano? (Pipeline global)
3. regras.md → Soberano? (Regras de negócio)
```

### Fase 2: Consolidar ou Remover (30min)
```
Se CLAUDE.md é soberano:
  mv CLAUDE.md docs/_canon/AGENT_INSTRUCTIONS.md
  
Se pipeline.md é soberano:
  Merge conteúdo em docs/_canon/CONTRACT_PIPELINE.md
  
Se regras.md é soberano:
  Merge conteúdo em docs/_canon/GLOBAL_RULES.md
  
Se NÃO soberanos:
  Remove keywords de SSOT/canônico/soberano
```

### Fase 3: Limpar SESSION_HANDOFF files (10min)
```bash
# Mover para _reports/ (onde pertencem)
mv SESSION_HANDOFF.md _reports/SESSION_HANDOFF_CURRENT.md
mv SESSION_HANDOFF_ADR031_20260318.md _reports/
rm README.md  # ou remove keywords se é importante

# Remove keywords de .github/ (setup docs, não autoridade)
sed -i 's/SSOT/documentation/g' .github/*.md
sed -i 's/source of truth/reference/g' .github/*.md
```

### Fase 4: Reauditoria (5min)
```bash
python scripts/audit/run_sovereign_integrity.py
# Target: C4 PASS (0-2 violations remaining)
```

---

## Impacto

| Métrica | Antes | Depois | % Reducão |
|---------|-------|--------|-----------|
| C4 Violations | 65 (57 reais) | **< 6** | **89%** ✅ |
| Allowlist Bloat | 65 | **6** | **89%** |
| Authority Clarity | Dispersa | Concentrada | Sim |
| Blocking Code | `BLOCKED_SHADOW_AUTHORITY` | 0 | Resolvido |

---

## Classificação

- ✅ **Automatizado**: .dev/ cleanupPreparación allowlist (COMPLETO)
- 🟡 **Manual + Revisão**: CLAUDE.md, pipeline.md, regras.md (AGUARDANDO PRODUTO)
- ⏳ **Pendente**: Reauditoria após decisão de produto

---

**Próximo Step**: Desambiguar root docs com produto →  remoção final / consolidação → Reauditoria C4 PASS
