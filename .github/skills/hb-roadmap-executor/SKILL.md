---
name: hb-roadmap-executor
description: >
  HB Track ROADMAP Phase Executor. USE FOR: execute_roadmap_phase (phases 0-13).
  Infra, CI/CD, frontend, deploy, mobile. Does NOT use hb verify/artifact/pre_contract_orchestrator.
  Enforces: Boot → Pré-execução (N-1 done criteria) → Execução → Fechamento (SESSION_HANDOFF).
  DO NOT USE FOR: contract tasks (new_contract, new_event, etc) — use hb-pipeline-orchestrator.
  For audits (audit_*): load worker directly, skip orchestration.
---

# HB Track — ROADMAP Phase Executor

> ⚠️ **BRIDGE ONLY — NON-SOVEREIGN**: Este skill é uma ponte operacional. Não define regras, schemas, gates ou políticas canônicas. Em caso de conflito, prevalecem nesta ordem: enforcement executável (`scripts/hb`, `validate_contracts.py`) > schemas ativos (`contracts/schemas/`) > canon (`docs/_canon/`) > este skill.

Este skill implementa o protocolo completo de execução de fases do ROADMAP.
**Toda execução de fase DEVE seguir esta checklist na ordem exata.**

Worker = prompt especializado carregado pelo mesmo agente.
Não presumir subagentes autônomos, fila ou runtime distribuído.

O humano é leigo em desenvolvimento — comunicar SEMPRE em português, linguagem de produto.

---

## FASE BOOT — Contexto de Sessão

**Obrigatório ANTES de qualquer outra ação.**

### Checklist Boot

- [ ] **B1** — Ler `docs/_canon/AGENT_INSTRUCTIONS.md` (§0 e §2)
- [ ] **B2** — Verificar se existe `SESSION_HANDOFF.md` na raiz do workspace
  - Se existe → ler ANTES de qualquer outra ação
  - Se não existe → continuar sem contexto anterior (registrar)
- [ ] **B3** — Ler `ROADMAP.md` — identificar fase declarada (`phase`) e task_id (se fornecido)
  - Se fase não especificada → perguntar ao humano qual fase executar (nunca inferir)
  - Fase válida: inteiro entre 0 e 13
- [ ] **B4** — Ler o worker prompt:
  `.contract_driven/agent_prompts/execute_roadmap_phase.prompt.md`
- [ ] **B5** — Confirmar ao humano:
  ```
  ✅ Modo ROADMAP iniciado: fase=<N>, task_id=<ID ou "completa">
  ```

---

## PRÉ-EXECUÇÃO — Validação de Pré-requisitos (Bloqueante)

**Verificar antes de executar qualquer tarefa da fase.**

### Checklist Pré-execução

- [ ] **P1** — Se `phase > 0`: verificar Critério de Done da fase N-1 conforme `ROADMAP.md`
  - Se N-1 não atingido → emitir `BLOCKED_PHASE_DEPENDENCY` e informar humano
  - Nunca inventar o estado da fase anterior
- [ ] **P2** — Se `phase >= 4`: verificar pipeline CDD
  ```bash
  python scripts/contracts/validate/validate_contracts.py
  ```
  - Se FAIL → emitir `BLOCKED_CDD_PIPELINE_FAIL`
  - Fases 0-3 (infra): verificar mas não bloquear se infra ainda ausente
- [ ] **P3** — Verificar waivers ativos em `.contract_driven/waivers.json`
- [ ] **P4** — Se `phase in [6, 9, 12]` (deploy de produção):
  - Emitir `BLOCKED_DEPLOY_REQUIRES_HUMAN`
  - Informar humano: preparar artefatos e confirmar staging verde; o acionamento do deploy é humano via GitHub Actions com `required_reviewers`

### Bloqueios possíveis nesta fase

| Código | Condição | Ação |
|---|---|---|
| `BLOCKED_PHASE_DEPENDENCY` | Critério de Done da fase N-1 não atingido | Listar o que falta, informar humano |
| `BLOCKED_CDD_PIPELINE_FAIL` | Pipeline CDD em FAIL (fase ≥ 4) | Informar humano, aguardar correção |
| `BLOCKED_DEPLOY_REQUIRES_HUMAN` | Fase 6, 9 ou 12 — deploy de produção | Preparar artefatos, aguardar aprovação humana |

---

## EXECUÇÃO — Tarefas da Fase

**Executar cada tarefa da fase conforme ROADMAP.md.**

### Checklist Execução

- [ ] **E1** — Ler seção completa da fase declarada em `ROADMAP.md`
- [ ] **E2** — Ler `docs/_canon/CODE_ARCHITECTURE.md` para stack canônica antes de criar código
- [ ] **E3** — Para cada tarefa listada na fase:
  - a. Verificar se já está concluída (arquivo existe / teste passa)
  - b. Se concluída → emitir `[ROADMAP] fase:<N> tarefa:<ID> status:SKIP` e continuar
  - c. Se não concluída → executar a tarefa
  - d. Verificar critério local da tarefa
  - e. Emitir status:
    ```
    [ROADMAP] fase:<N> tarefa:<ID> status:<DONE|BLOCKED|SKIP>
      resultado: <o que foi feito ou por que está bloqueado>
      artefato:  <path do artefato criado/modificado, se houver>
    ```
- [ ] **E4** — Se task_id foi especificado → executar apenas essa tarefa e parar

### Paths canônicos de artefatos por fase

Usar os paths canônicos definidos em `execute_roadmap_phase.prompt.md`. Nunca criar artefatos fora deles.

| Fase | Artefatos principais |
|------|---------------------|
| 0 | `infra/docker-compose.yml` (já existente) |
| 1 | `config/celery.py`, `config/asgi.py`, `src/shared/middleware.py`, `src/identity_access/middleware.py` |
| 2 | `src/<module>/migrations/0002_add_constraints.py`, `scripts/seed.py` |
| 3 | `Dockerfile`, `infra/docker-compose.prod.yml`, `infra/nginx/nginx.conf`, `.github/workflows/ci.yml` |
| 5+ | `frontend/` (React + Vite) |
| 13 | `mobile/` (React Native + Expo) |

### Bloqueio possível nesta fase

| Código | Condição |
|---|---|
| `BLOCKED_MISSING_STACK_DECISION` | Stack não definida para o artefato a criar |

---

## FECHAMENTO — Critério de Done e Handoff

**Obrigatório ao final de toda execução de fase.**

### Checklist Fechamento

- [ ] **F1** — Verificar Critério de Done da fase completa conforme `ROADMAP.md`
- [ ] **F2** — Criar ou atualizar `SESSION_HANDOFF.md` na raiz com front matter YAML válido (obrigatório — validado por `HANDOFF_COHERENCE_GATE`):
  ```markdown
  ---
  data_ultima_sessao: "YYYY-MM-DD"
  branch_ativo: "<branch>"
  modo_operacao: ROADMAP
  ci_status: PASS
  modulo_foco: "<módulo ou área principal>"
  fase_roadmap: <N>
  task_type: execute_roadmap_phase
  boot_profile_id: roadmap_execution
  task_id: "<task_id ou 'completa'>"
  resultado: DONE
  proxima_acao_permitida: "<próxima ação objetiva — mín. 10 chars>"
  bloqueios_ativos: []
  evidence_paths:
    - "_reports/runs/<run_id>/contract_gates.json"
  ---
  # SESSION HANDOFF — HB TRACK

  ## Estado Geral
  **Data:** <YYYY-MM-DD> | **Branch:** <branch>
  **Fase ROADMAP:** <N> | **task_id:** <ID ou "completa">
  **Resultado:** <DONE|PENDENTE>

  ## O que foi feito
  - [lista de artefatos criados/modificados]

  ## Evidências
  - `_reports/runs/<run_id>/contract_gates.json`

  ## Próxima ação permitida
  [fase N+1 ou aguardar instrução humana]

  ## Bloqueios ativos
  Nenhum.
  ```
- [ ] **F3** — Emitir ao humano:
  ```
  [ROADMAP] fase:<N> COMPLETA
    criterio_de_done: <ATINGIDO|PENDENTE — listar o que falta>
    proxima_fase: <N+1 ou "aguardar instrução humana">
  ```
- [ ] **F4** — Informar humano do resultado final em linguagem de produto

---

## REGRAS DE OURO

1. **NUNCA iniciar fase N** sem confirmar Critério de Done da fase N-1
2. **NUNCA editar** `frontend/src/api/schema.d.ts` manualmente — regenerar com `npm run api:generate`
3. **NUNCA executar deploy** de produção autonomamente (fases 6, 9, 12 — requer aprovação humana)
4. **NUNCA criar artefatos** fora dos paths canônicos definidos em `execute_roadmap_phase.prompt.md`
5. **NUNCA criar código** para módulo fora dos 17 canônicos do `MODULE_REGISTRY.yaml`
6. **`generate_frontend` está FROZEN** — FASE 5 usa código React escrito diretamente, não este worker
7. **Infra não é CDD** — `Dockerfile`, `nginx.conf`, `celery.py` não passam por `hb verify`/`hb artifact`
8. **NUNCA misturar modos** — este skill não executa contratos; para contratos usar `hb-pipeline-orchestrator`
9. **Stack obrigatória** — não desviar: Python 3.12 + Django 5.x + Django Ninja 1.x + PostgreSQL 16 + Redis 7 + React + Vite + TypeScript + Tailwind CSS + shadcn/ui + Zustand
10. **Comunicação em português**, linguagem de produto, nunca jargão técnico
