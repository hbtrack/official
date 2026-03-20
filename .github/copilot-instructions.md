# HB TRACK — Copilot Instructions

## Produto
HB Track — plataforma de gestão esportiva para handebol.
CDD (Contract-Driven Development): contratos são SSOT antes de qualquer código.
O humano é leigo em desenvolvimento — comunicar em linguagem de produto, nunca jargão técnico.

## Referências canônicas (ler on-demand, não tudo de uma vez)
- **Instruções do agente:** `docs/_canon/AGENT_INSTRUCTIONS.md`
- **Pipeline oficial:** `docs/_canon/CONTRACT_PIPELINE.md`
- **16 módulos:** `docs/_canon/MODULE_REGISTRY.yaml`
- **Task types → workers (SSOT):** `.contract_driven/TASK_CATALOG.yaml`
- **Boot profiles:** `.contract_driven/BOOT_PROFILES.yaml`
- **Gate metadata:** `docs/_canon/gates/GATES_REGISTRY.yaml`
- **Regras detalhadas:** `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- **Layout canônico:** `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`

## Regra de boot obrigatória
1. Se existir `SESSION_HANDOFF.md` na raiz → **ler ANTES de qualquer outra ação**
2. Se não existir → verificar `_reports/SESSION_HANDOFF_CURRENT.md`

## Pipeline CDD — Regra absoluta para tarefas de contrato
**Para QUALQUER tarefa que crie ou modifique contratos (OpenAPI, AsyncAPI, Arazzo, JSON Schema, UI Contract, State Model, docs de módulo, decisões arquiteturais):**

O agente DEVE usar o agent **HB Contract** (`.github/agents/hb-contract.agent.md`), que referencia o skill **hb-pipeline-orchestrator**.

A sequência obrigatória é:
```
BOOT     → Ler AGENT_INSTRUCTIONS.md + SESSION_HANDOFF.md
PRÉ-0    → python3 scripts/hb verify --task-type pre_contract_boot --module <M>
FASE 0   → python3 scripts/hb verify --task-type <T> --module <M>
FASE 1   → python3 scripts/hb check --module <M>
DECISION → Benchmark competitivo + 3 opções A/B/C + aguardar aprovação
FASE 2   → Ler worker prompt + criar artefatos + python3 scripts/hb artifact <path>
COMPILE  → python3 scripts/contracts/validate/api/compile_api_policy.py
FASE 3   → python3 scripts/contracts/validate/validate_contracts.py
FASE 4   → Atualizar MODULE_REGISTRY.yaml + python3 scripts/hb artifact docs/_canon/MODULE_REGISTRY.yaml
FASE 5   → Atualizar SESSION_HANDOFF.md
FASE 6   → git add <artefatos> SESSION_HANDOFF.md && git commit -m "feat(contract): <module> — <task_type> pipeline PASS"
```

**NUNCA pular fases. NUNCA criar artefatos antes de executar `hb verify`. NUNCA terminar sessão sem commit.**

## Bloqueios canônicos
O agente não pode prosseguir quando emitir um código BLOCKED_*. Deve informar o humano em português:
- `BLOCKED_MISSING_MODULE` — módulo fora dos 16 canônicos
- `BLOCKED_MISSING_AGENT_PROMPT` — worker não existe ou task congelada
- `BLOCKED_REQUIRED_ARTIFACT_MISSING` — doc obrigatória ausente
- `BLOCKED_MISSING_ARCH_DECISION` — decisão arquitetural obrigatória aberta
- `BLOCKED_SCOPE_OVERFLOW` — referência cross-module não autorizada
- `BLOCKED_CONTRACT_CONFLICT` — contradição entre artefatos

## Comunicação
- Sempre em português
- Decisões arquiteturais: apresentar "📊 benchmark → 🎯 3 caminhos A/B/C → ⭐ recomendação"
- Bloqueio: explicar em linguagem de produto o que falta
- Nunca jargão técnico sem tradução

## REGRA DE OURO

**MUST NOT** usar: 

```bash
git reset
```
ou

```bash
git rebase 
```
ou

```bash
 git commit --amend
```
**MUST NOT** rodar qualquer comando que apague histórico de commits. 

**O histórico é parte do contrato e da evidência de processo.**