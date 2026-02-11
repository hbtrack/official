# MAP_ROUTING_AGENT_DOCUMENTATION.md

## Descrição
Roteamento para tarefas de documentação: quando editar qual doc, aprovações necessárias, e sequência de atualização.

---

## Mapa de Documentação Canônica

### Tier 1: SSOT (Never edit directly, use workflows)
```
Categoria: Database
├─ schema.sql → Alembic migrations (workflow: inv.ps1 refresh)
├─ parity_report.json → auto-generated por parity_gate.ps1
└─ alembic_state.txt → auto-generated por agent_guard.py

Categoria: API
├─ openapi.json → auto-generated por FastAPI (docs gen)
└─ não editar manualmente
```

### Tier 2: Canon Authority (Edit via ADR + approval)
```
docs/_canon/
├─ 00_START_HERE.md → Entry point, referências, SSOT
├─ 01_AUTHORITY_SSOT.md → What to trust (DB > Code > Docs)
├─ 03_WORKFLOWS.md → Operational procedures
├─ 05_MODELS_PIPELINE.md → Models workflow, gates, checklist
├─ 08_APPROVED_COMMANDS.md → CommandLine allowlist + guardrails
└─ 10_GIT_PR_MERGE_WORKFLOW.md → Git procedure
```

### Tier 3: ADR + Guides (Edit with issue/ADR tracking)
```
docs/ADR/
├─ _INDEX_ADR.md → Index of all ADRs
├─ architecture/ → Architecture decisions
└─ migrations/ → Migration history

docs/execution_tasks/
├─ CHANGELOG.md → Changes by date/impact
├─ EXECUTIONLOG.md → Execution traces + lessons learned
└─ EXEC_TASK_*.md → Actionable task specifications
```

### Tier 4: Reference (Edit as knowledge evolves)
```
docs/references/
├─ exit_codes.md → Exit code semantics (0/1/2/3/4)
├─ naming_conventions.md → Code + file naming standards
└─ glossary.md → Terms + definitions
```

---

## Workflow: Canon Edit

**Quando editar doc canônico:**
1. Identificar qual tier (1=SSOT, 2=Canon, 3=ADR, 4=Reference)
2. Abrir ADR se mudança impactar múltiplos fluxos
3. Escrever proposta + justificativa
4. Submeter para revisão
5. Após aprovação: editar + commit
6. Atualizar CHANGELOG + EXECUTIONLOG

**Exemplo:**
```
Tarefa: Adicionar novo comando aprovado em 08_APPROVED_COMMANDS.md
├─ ADR: Ou não? (se for novo pattern, sim; senão, direto)
├─ Edit: Adicionar linha em table
├─ Test: Validar markdown sintaxe
├─ Commit: "docs(canon): add <comando>"
└─ Register: CHANGELOG + EXECUTIONLOG
```

---

## Checklist: Doc Edit Validation

- [ ] Markdown válido (sintaxe, headers, links)
- [ ] Nenhum link quebrado (use caminhos relativos)
- [ ] Nenhuma PII/secrets disperso
- [ ] Referências cruzadas consistentes (usar docs._ai._INDEX.md como audit)
- [ ] Git diff revisado antes de commit
- [ ] CHANGELOG + EXECUTIONLOG atualizados

---

## TODO
- [ ] Criar script de validação de links
- [ ] Documentar approval workflow (quem aprova o quê)
- [ ] Adicionar spell checker + grammar linter
