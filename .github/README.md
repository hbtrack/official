# .github

> ⚠️ **BRIDGE DOC — NÃO-SOBERANO**: Este README é um navegador de pasta. Não define regras, gates ou políticas canônicas. Em caso de conflito, prevalecem: enforcement executável (`scripts/hb`, `merge-readiness.json`) > schemas > canon (`docs/_canon/`) > este arquivo.

Configuração de governança, CI/CD, agentes de IA e enforcement para o repositório HB Track.

## Estrutura

```
.github/
├── README.md                              # Este arquivo
├── CODEOWNERS                             # Ownership obrigatório de artefatos normativos
├── BRANCH_PROTECTION_SETUP.md            # Runbook de configuração de branch protection
├── QUICK_SETUP_SOLO_DEV.md               # Setup mínimo de enforcement para dev solo
├── CI_FIX_EVIDENCE.md                    # Evidência de correção do CI (package-lock.json sync)
├── copilot-instructions.md               # Bridge doc do agente GitHub Copilot (auto-load)
├── merge-policy.md                       # GERADO — derivado não-soberano (não editar manualmente)
├── agents/
│   ├── hb-contract.agent.md              # Agente CDD: tarefas de contrato e pipeline
│   ├── hb-implementer.agent.md           # Agente de implementação com plano aprovado
│   ├── hb-adversarial-tester.agent.md    # Agente de teste adversarial pós-PR
│   └── hb-mesclado.agent.md              # Agente HandTracker: merges, CI, PRs
├── ai-review/
│   ├── config.yaml                       # Configuração do Gemini AI PR Review
│   └── styleguide.md                     # Guia de estilo para review automático
├── hooks/
│   └── hb-contract-guards.json           # Configuração dos guardrails de contrato
├── instructions/
│   ├── hb-contract-guards.instructions.md        # applyTo: src/**
│   ├── hb-derived-not-sovereign.instructions.md  # applyTo: *.md
│   ├── hb-mesclado.instructions.md               # applyTo: **
│   ├── hb-no-manual-schema-edit.instructions.md  # applyTo: frontend/src/api/**
│   └── hb-roadmap-mode.instructions.md           # applyTo: infra/**, config/**, Dockerfile*, .github/workflows/**
├── rulesets/
│   └── contract-gates.snapshot.json      # Snapshot do ruleset ativo (usado para validação de paridade)
├── skills/
│   ├── hb-merge-orchestrator/            # Skill: merges, CI fix, PRs, workflows, sync/audit
│   ├── hb-pipeline-orchestrator/         # Skill: pipeline CDD completo (contratos)
│   └── hb-roadmap-executor/              # Skill: execução de fases 0-13 do ROADMAP
└── workflows/
    ├── _reusable-ci.yml                  # Workflow reutilizável: testes, build, validate contracts
    ├── ai-pr-review.yml                  # AI PR Review via Gemini
    ├── ci.yml                            # CI principal: chama _reusable-ci.yml em push/PR
    ├── context-efficiency-audit.yml      # Auditoria de eficiência de contexto (agendada)
    ├── contract-gates.yml                # Gates de contrato: validate, architecture drift, governance
    ├── deploy.yml                        # Pipeline de deploy (workflow_dispatch)
    └── domain-completeness-audit.yml     # Auditoria de completude de domínio por módulo (agendada)
```

## Componentes

### Governance

**`CODEOWNERS`** — Define ownership obrigatório para:
- Sistema contract-driven (`.contract_driven/**`)
- Contratos técnicos (`contracts/**`)
- Documentação canônica (`docs/_canon/**`)
- Scripts de validação (`scripts/contracts/validate/**`)

**Efeito:** PRs que modificam estes arquivos requerem aprovação explícita do(s) owner(s).

**`rulesets/contract-gates.snapshot.json`** — Snapshot normalizado do ruleset GitHub ativo. Usado pelo gate de paridade `check_live_ruleset_parity.py` para detectar drift entre o ruleset declarado e o estado real do repositório.

**`merge-policy.md`** — ⚠️ **ARTEFATO GERADO — NÃO EDITAR MANUALMENTE.** Derivado de `merge-readiness.json` + `rulesets/contract-gates.snapshot.json` via `scripts/audit/generate_merge_policy.py`. Documenta os required checks, informational checks e regras de enforcement verificáveis para merge em `main`.

---

### Agentes de IA (`agents/`)

Quatro agentes especializados expostos no dropdown do GitHub Copilot. Cada um opera sobre o mesmo enforcement central do repositório — o dropdown não cria soberania nova.

| Agente | Arquivo | Papel |
|---|---|---|
| **HB Contract** | `hb-contract.agent.md` | Pipeline CDD completo: `hb verify` → worker → `hb artifact` → `validate_contracts` |
| **Hb Implementer** | `hb-implementer.agent.md` | Executa plano aprovado com escopo fechado e evidência auditável |
| **Hb Adversarial Tester** | `hb-adversarial-tester.agent.md` | Testa adversarialmente PR aberto; produz manifesto negativo auditável |
| **HandTracker** | `hb-mesclado.agent.md` | Merges, CI fix, code review, GitHub Actions, branch protection |

Referência completa de papéis e plataformas: `AGENTS.md` (raiz do repositório).

---

### Skills do Copilot (`skills/`)

Domain-specific knowledge carregado on-demand pelo Copilot. Cada skill define o protocolo completo de execução para seu domínio.

| Skill | Diretório | Usar para |
|---|---|---|
| **hb-pipeline-orchestrator** | `skills/hb-pipeline-orchestrator/` | Qualquer tarefa de contrato CDD (new_contract, new_schema, new_event, etc.) |
| **hb-roadmap-executor** | `skills/hb-roadmap-executor/` | Execução de fases 0-13 do ROADMAP (infra, CI/CD, frontend, deploy) |
| **hb-merge-orchestrator** | `skills/hb-merge-orchestrator/` | Merges, CI fix, PRs, GitHub Actions, sync/audit de ambientes |

**Regra:** Nunca misturar `hb-pipeline-orchestrator` (Modo CDD) com `hb-roadmap-executor` (Modo ROADMAP) — são modos distintos e incompatíveis.

---

### Instruções contextuais (`instructions/`)

Instruções injetadas automaticamente pelo Copilot com base no padrão `applyTo`. Carregadas sem intervenção quando o arquivo editado corresponde ao escopo declarado.

| Arquivo | Escopo (`applyTo`) | Propósito |
|---|---|---|
| `hb-contract-guards.instructions.md` | `src/**` | Guardrails CDD: bloqueios antes de editar código sem contrato |
| `hb-derived-not-sovereign.instructions.md` | `*.md` | Lembra que arquivos `.md` são bridge docs, não SSOT |
| `hb-mesclado.instructions.md` | `**` | Instruções globais do HandTracker para todo o workspace |
| `hb-no-manual-schema-edit.instructions.md` | `frontend/src/api/**` | Proíbe edição manual de `schema.d.ts` — regenerar com `npm run api:generate` |
| `hb-roadmap-mode.instructions.md` | `infra/**, config/**, Dockerfile*, .github/workflows/**` | Regras do Modo ROADMAP para artefatos de infraestrutura |

---

### Workflows CI (`workflows/`)

Sete workflows. Os required checks para merge em `main` estão definidos em `merge-policy.md`.

| Workflow | Trigger | Propósito |
|---|---|---|
| `ci.yml` | push/PR | CI principal — delega para `_reusable-ci.yml` |
| `_reusable-ci.yml` | `workflow_call` | Testes, build frontend, validate contracts (checks bloqueantes) |
| `contract-gates.yml` | push/PR + governance changes | Gates de contrato: validate, architecture drift, governance survival-suite |
| `deploy.yml` | `workflow_dispatch` | Pipeline de deploy (staging/produção — requer aprovação humana) |
| `ai-pr-review.yml` | pull_request | AI PR Review automático via Gemini |
| `context-efficiency-audit.yml` | schedule + `workflow_dispatch` | Auditoria periódica de eficiência de contexto dos agentes |
| `domain-completeness-audit.yml` | schedule + `workflow_dispatch` | Auditoria periódica de completude de domínio por módulo |

**Status checks obrigatórios** (bloqueiam merge): ver `merge-policy.md` → seção "Required checks".

---

### AI Review (`ai-review/`)

Configuração do workflow `ai-pr-review.yml` para review automático de PRs via Gemini.

- `config.yaml` — configuração do modelo e parâmetros de review
- `styleguide.md` — guia de estilo aplicado pelo revisor automático

---

### Bridge docs do Copilot

**`copilot-instructions.md`** — Carregado automaticamente pelo GitHub Copilot em toda sessão no workspace. Define o ponto de entrada operacional do agente, os dois modos (CDD e ROADMAP) e as regras de boot. **Não é soberano** — em conflito, prevalecem enforcement executável e canon.

---

### Runbooks de setup

- **`BRANCH_PROTECTION_SETUP.md`** — Runbook detalhado para configuração de branch protection rules no GitHub
- **`QUICK_SETUP_SOLO_DEV.md`** — Setup mínimo de enforcement server-side para cenário solo developer (CI-only, sem aprovações obrigatórias)

---

### Hooks

**`hooks/hb-contract-guards.json`** — Configuração dos guardrails executados como hooks do Copilot para bloquear operações que violam o pipeline CDD.

## Conformidade

Este setup atende aos requisitos de governança do HB Track:

- ✅ Branch protection + required status checks (ruleset `contract-gates`)
- ✅ CODEOWNERS para artefatos normativos
- ✅ Bloqueio de force-push e deleção da branch default
- ✅ CI fail-closed
- ✅ Agentes, skills e instruções contextuais alinhados ao pipeline CDD
- ✅ Paridade entre ruleset declarado e estado live verificável via `check_live_ruleset_parity.py`

**Referências normativas:**
- Governança de agentes: `AGENTS.md` (raiz)
- Instruções canônicas de boot: `docs/_canon/AGENT_INSTRUCTIONS.md`
- Gates obrigatórios: `docs/_canon/gates/GATES_REGISTRY.yaml`
- Bridge doc Copilot: `copilot-instructions.md`

---

*Atualizado: 2026-05-02*
