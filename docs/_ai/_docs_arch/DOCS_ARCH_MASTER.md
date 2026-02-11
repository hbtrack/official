# DOCS_ARCH_MASTER.md

## Descrição
Documento master que descreve a arquitetura de documentação do projeto HB Track: como docs estão organizadas, tiers de autoridade, workflows de edição, e integração com agentes.

---

## 🎯 Arquitetura de Documentação HB Track

### Visão Geral
Documentação é organizada em **4 tiers** conforme autoridade e frequência de mudança:

```
Tier 1: SSOT (Source of Truth) ❌ Não editar manualmente
├─ schema.sql (DB structure)
├─ openapi.json (API contracts)
├─ parity_report.json (structural validation)
└─ alembic_state.txt (migration state)

Tier 2: Canon Authority ⚠️ Editar via ADR + Approval
├─ docs/_canon/00_START_HERE.md (entry point)
├─ docs/_canon/01_AUTHORITY_SSOT.md (what to trust)
├─ docs/_canon/03_WORKFLOWS.md (operational procedures)
├─ docs/_canon/05_MODELS_PIPELINE.md (models workflow)
├─ docs/_canon/08_APPROVED_COMMANDS.md (allowlist)
└─ docs/_canon/10_GIT_PR_MERGE_WORKFLOW.md (git procedure)

Tier 3: ADR + Guides 📝 Editar com issue tracking
├─ docs/ADR/_INDEX_ADR.md (ADR index)
├─ docs/ADR/architecture/ (architecture decisions)
├─ docs/ADR/migrations/ (migration history)
├─ docs/execution_tasks/CHANGELOG.md (changes by date)
├─ docs/execution_tasks/EXECUTIONLOG.md (execution traces)
└─ docs/execution_tasks/EXEC_TASK_*.md (actionable tasks)

Tier 4: Reference Documentation 📚 Editar as knowledge evolves
├─ docs/references/exit_codes.md (exit semantics)
├─ docs/references/naming_conventions.md (code naming)
└─ docs/references/glossary.md (terms/definitions)
└─ docs/02_modulos/ (feature documentation)
```

### Diretório: `docs/_ai/` (Este Projeto)

**Propósito**: Guardrails, specs, e prompts para agentes AI.

**Estrutura**:
```
docs/_ai/
├─ _context/          → Initial context, rules, constraints
├─ _specs/            → Formal specifications (JSON/YAML/XML)
├─ _prompts/          → Prompt templates (codigo review, docs, testing)
├─ _maps/             → Routing maps (when to use what gate/agent)
├─ _guardrails/       → Guardrail policies (baseline, parity, requirements)
├─ _checklists/       → Validation checklists (deployment, validation, docs)
├─ _docs_arch/        → Documentation architecture (this file)
├─ 06_AGENT_PROMPTS_MODELS.md      → Agent prompt para models (existing root)
├─ 07_AGENT_ROUTING_MAP.md         → Routing map (existing root)
└─ (+ 5 more existing at root: 00_INDEX.md, etc)
```

---

## 📐 Tiers & Workflows

### Editing Tier 1 (SSOT)
**NUNCA edite manualmente**. Em vez:
```
schema.sql:          Alembic migrations (workflow: inv.ps1 refresh)
openapi.json:        FastAPI docs gen (workflow: build backend)
parity_report:       auto-generated (workflow: parity_gate.ps1)
alembic_state:       auto-generated (workflow: agent_guard.py)
```

### Editing Tier 2 (Canon)
**Processo**:
1. Identificar qual doc (use MAP_ROUTING_AGENT_DOCUMENTATION.md)
2. Abrir ADR (se mudança impacta múltiplos fluxos) ou direto edit
3. Editar doc + escrever descrição clara
4. Testar links + markdown syntax
5. `git add + git commit` com mensagem: `docs(canon): <change>`
6. Update CHANGELOG + EXECUTIONLOG

### Editing Tier 3 (ADR/Guides)
**Processo**:
1. Issue ou ADR proposal
2. Discussão + review comunitária
3. Aprovação
4. Editar documento + ADR
5. Commit com mensagem: `docs(adr): <change>`
6. Update CHANGELOG + EXECUTIONLOG

### Editing Tier 4 (Reference)
**Processo**:
1. Editar direto (menos formal)
2. Commit com mensagem: `docs(reference): <change>`
3. Update CHANGELOG + EXECUTIONLOG

---

## 🔗 Integrações com Agentes

**Agent acessando documentação**:
```
Agent inicia
├─ Carrega 00_START_HERE.md (por quê → próximos passos)
├─ Se modelos: consulta 05_MODELS_PIPELINE.md + MAP_ROUTING_AGENT_MODELS.md
├─ Se código: consulta PROMPT_TEMPLATE_CODE_REVIEW.md da pasta _prompts/
├─ Se documentation: consulta MAP_ROUTING_AGENT_DOCUMENTATION.md
├─ Sempre: valida GUARDRAIL_* policies antes de write
└─ Pós-execução: registra em EXECUTIONLOG.md + CHANGELOG.md
```

**Exemplo**: Agent atualizando modelo
```
1. Lê: _context/AGENT_RULES_ENGINE.md (7 rules)
2. Lê: _guardrails/GUARDRAIL_POLICY_BASELINE.md (baseline local)
3. Lê: _maps/MAP_ROUTING_AGENT_MODELS.md (decision tree)
4. Executa: models_autogen_gate.ps1
5. Valida: against CHECKLIST_AGENT_VALIDATION.md
6. Registra: updates EXECUTIONLOG.md (task T-NNN)
7. Commit: with message from _prompts/PROMPT_TEMPLATE_DOCUMENTATION.md
```

---

## 📊 Referência Cruzada

**Se você está procurando...**
| Você quer | Vá para |
|-----------|---------|
| Entender o projeto | `docs/_canon/00_START_HERE.md` |
| Aprender o modelo de autoridade | `docs/_canon/01_AUTHORITY_SSOT.md` |
| Executar workflow de modelos | `docs/_canon/05_MODELS_PIPELINE.md` |
| Usar um comando do PowerShell | `docs/_canon/08_APPROVED_COMMANDS.md` |
| Entender regras do agente | `docs/_ai/_context/AGENT_RULES_ENGINE.md` |
| Ver roteamento de tarefas | `docs/_ai/_maps/` (3 arquivos) |
| Validar mudanças | `docs/_ai/_checklists/` (3 arquivos) |
| Guardrails operacionais | `docs/_ai/_guardrails/` (3 arquivos) |

---

## 🚀 TODO

- [ ] Adicionar automação de validação de links (quebrados?)
- [ ] Criar converter de docs → wikis (se necessário escalabilidade)
- [ ] Documentar versionamento de docs (quando major versioning?)
- [ ] Adicionar spell checker + grammar linter (PT-BR)
- [ ] Criar indexador full-text (busca dentro de docs)
