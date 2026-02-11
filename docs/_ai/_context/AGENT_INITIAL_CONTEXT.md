# AGENT_INITIAL_CONTEXT.md

## Descrição
Contexto inicial que todo agente deve carregar ao iniciar. Contém ambiente, stack, convenções e porta única de autoridade (SSOT).

---

## Seções

### 1. Ambiente Técnico
- **OS**: Windows
- **Shell**: PowerShell 5.1
- **Language Stack**: Python 3.11+, TypeScript 5.x, SQL (PostgreSQL 12+)
- **Repository Root**: `C:\HB TRACK`

### 2. Autoridade (SSOT)
- Canon Docs: `docs/_canon/`
- Generated Artifacts: `docs/_generated/`
- ADRs: `docs/ADR/`

### 3. Estrutura Padrão
**Backend**: `Hb Track - Backend/`
**Frontend**: `Hb Track - Fronted/` (note: typo no nome da pasta)
**Scripts**: `scripts/`

### 4. Fluxos Críticos
- Modelos: `05_MODELS_PIPELINE.md`
- Git/PR: `10_GIT_PR_MERGE_WORKFLOW.md`
- Comandos Aprovados: `08_APPROVED_COMMANDS.md`

---

## TODO
- [ ] Incorporar variáveis de ambiente padrão
- [ ] Adicionar timeouts/limites recomendados
- [ ] Documentar hierarchy de autoridade completa
