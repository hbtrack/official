---
task_type: execute_roadmap_phase
version: "1.0.0"
status: active
---

# execute_roadmap_phase — Worker de Execução de Fases do ROADMAP

> **Modo:** ROADMAP (implementação) — NÃO rotear por `pre_contract_orchestrator`
> **SSOT de fases:** `ROADMAP.md` (raiz do repositório)
> **Regra cardinal:** fases são bloqueantes — fase N não inicia sem Critério de Done de N-1 confirmado

---

## Pré-requisitos obrigatórios

Antes de executar qualquer tarefa desta fase:

1. **SESSION_HANDOFF.md** existe na raiz? → ler ANTES de qualquer ação
2. **Fase declarada** está entre 0 e 13?
3. **Fase > 0?** → verificar Critério de Done da fase N-1 conforme ROADMAP.md
4. **Pipeline CDD PASS?** → `python scripts/contracts/validate/validate_contracts.py`
   - Fases 0–3 (infraestrutura): verificar mas não bloquear se infra ainda ausente
   - Fases 4+: PASS obrigatório antes de continuar
5. **Waivers ativos?** → verificar `.contract_driven/waivers.json` antes de iniciar pipeline
6. **Bundle compilado fresco** para o módulo-foco existe em `compiled_context/<module>/`
   - Verificar: `ls compiled_context/<module>/` retorna ao menos um arquivo `.json`
   - Se ausente: executar `python3 scripts/compile/compile_context_bundle.py --module <module>` e aguardar PASS
   - Bundle é a única entrada operacional autorizada para tarefas de implementação e evolução de módulo (B11-001)
   - Exceção: fases 0–3 (infraestrutura pura, sem módulo-foco) não requerem bundle de módulo

Se qualquer pré-requisito crítico falhar → reportar ao humano e aguardar instrução. Nunca inventar o estado da fase anterior.

---

## Input esperado

```
phase:    <número inteiro de 0 a 13>
task_id:  <ex: "1.1", "2.3"> (opcional — se ausente, executar todas as tarefas da fase)
```

---

## Estado de sessão (opcional — recomendado)

Para registrar o estado operacional desta fase em `_reports/session_start.json`:
```bash
python3 scripts/hb verify --task-type execute_roadmap_phase --roadmap-phase <N>
# Opcional: --roadmap-task-id <task_id>
```
Grava `operation_mode=ROADMAP`, `roadmap_phase=<N>` e `roadmap_task_id` na sessão.
Não substitui os pré-requisitos acima. Não usar `hb check` nem `hb artifact` para artefatos de infra.

---

## Mapa de fases

Ler a seção correspondente no ROADMAP.md antes de executar:

| Fase | Escopo | Ciclo |
|------|--------|-------|
| 0 | Ambiente local funcional (Docker, migrations, runserver, pytest) | — |
| 1 | Backend infra (Celery, Channels, JWT, X-Flow-ID, CORS, /health, logging) | — |
| 2 | Banco de dados com integridade (constraints, triggers, seed, Schemathesis) | — |
| 3 | CI/CD + deploy (Dockerfile, GitHub Actions, Nginx, VPS, rollback) | — |
| 4 | Ciclo 1 integrado em staging (E2E, RBAC, performance, segurança) | Ciclo 1 |
| 5 | Frontend Ciclo 1 (React + Vite, API client, login, teams, seasons, training) | Ciclo 1 |
| 6 | Deploy produção → v0.1 | Ciclo 1 |
| 7 | Ciclo 2 integrado em staging (competitions, matches, scout, video) | Ciclo 2 |
| 8 | Frontend Ciclo 2 (partidas ao vivo, scout, vídeo) | Ciclo 2 |
| 9 | Deploy produção → v0.2 | Ciclo 2 |
| 10 | Ciclo 3 integrado em staging (wellness, medical, analytics, reports, ai_ingestion, notifications, audit) | Ciclo 3 |
| 11 | Frontend Ciclo 3 (dashboards, saúde, relatórios, notificações) | Ciclo 3 |
| 12 | Deploy produção → v1.0 | Ciclo 3 |
| 13 | Mobile v2.0 (React Native + Expo) | Mobile |

---

## Paths canônicos de artefatos de infraestrutura

Estes paths são obrigatórios. Não criar artefatos fora deles.

```
# Dev local (FASE 0 — já existentes)
infra/docker-compose.yml

# Backend infraestrutura (FASE 1 — criar)
config/celery.py                                         # Celery 5.x + Redis broker
config/asgi.py                                           # ProtocolTypeRouter (HTTP + WebSocket)
src/shared/middleware.py                                 # FlowIDMiddleware
src/identity_access/middleware.py                        # JWTAuthMiddleware
src/notifications/consumers.py                           # WebSocket consumer
src/notifications/tasks.py
src/ai_ingestion/tasks.py
src/analytics/tasks.py
src/reports/tasks.py
src/audit/tasks.py

# Banco de dados (FASE 2 — criar por módulo)
src/<module>/migrations/0002_add_constraints.py
scripts/seed.py

# Containerização e deploy (FASE 3 — criar)
Dockerfile                                               # multi-stage, raiz do repositório
infra/docker-compose.prod.yml                            # serviços de produção completos
infra/nginx/nginx.conf                                   # reverse proxy + SSL
infra/env/.env.staging.template                          # apenas chaves, sem valores reais
infra/env/.env.production.template                       # apenas chaves, sem valores reais
infra/scripts/rollback.sh                                # script de rollback
.github/workflows/ci.yml                                 # 5 jobs do pipeline

# Frontend (FASE 5+ — criar)
frontend/                                                # raiz do projeto React + Vite
frontend/src/api/schema.d.ts                             # GERADO — nunca editar manualmente
frontend/src/api/client.ts                               # openapi-fetch configurado
frontend/src/api/hooks/                                  # React Query hooks por módulo
frontend/Dockerfile.frontend                             # multi-stage: build → Nginx

# Mobile (FASE 13 — criar)
mobile/                                                  # raiz React Native + Expo
packages/shared/                                         # lógica compartilhada web + mobile
```

---

## Regras invariantes de implementação

### R1 — D3: API client gerado (nunca editar manualmente)
`frontend/src/api/schema.d.ts` é gerado por `openapi-typescript`. **Nunca editar este arquivo.**
Regenerar sempre com: `npm run api:generate`

### R2 — generate_frontend FROZEN ≠ bloquear FASE 5
O worker `generate_frontend` está `frozen` no TASK_CATALOG.
**FASE 5 não usa este worker.** FASE 5 = código React escrito diretamente,
usando `contracts/openapi/openapi.yaml` como contrato de referência via `openapi-typescript`.

### R3 — Deploy produção: aprovação humana obrigatória
Deploy de produção (FASEs 6, 9, 12) **nunca é executado autonomamente pelo agente.**
O pipeline GitHub Actions usa `environment: production` com `required_reviewers` configurado.
O agente prepara os artefatos e confirma que staging está verde — o acionamento do deploy é humano.

### R4 — Stack obrigatória
Não desviar do stack definido no ROADMAP.md e em `docs/_canon/ARCHITECTURE.md`:
- Backend: Python 3.12 + Django 5.x + Django Ninja 1.x + PostgreSQL 16 + Redis 7
- Frontend: React + Vite + TypeScript + Tailwind CSS + shadcn/ui + Zustand + openapi-fetch
- Containerização: Docker multi-stage, Gunicorn + UvicornWorker
- Mobile (FASE 13): React Native + Expo

### R5 — 17 módulos canônicos
Nunca criar código ou configuração para módulo fora dos 17 canônicos em `docs/_canon/MODULE_REGISTRY.yaml`.

### R6 — Infra não é contrato CDD
Arquivos de infraestrutura (Dockerfile, nginx.conf, celery.py, etc.) não passam pelo pipeline CDD.
Não executar `hb verify` nem `hb artifact` sobre eles.
O pipeline CDD valida contratos — a verificação de infra é via health checks e testes.

---

## Sequência de execução por fase

1. Ler seção completa da fase declarada em `ROADMAP.md`
2. Verificar Critério de Done da fase anterior (se fase > 0)
3. Para cada tarefa listada na fase:
   a. Verificar se já está concluída (arquivo existe / teste passa)
   b. Executar a tarefa
   c. Verificar critério local da tarefa
   d. Emitir status
4. Ao final: verificar Critério de Done da fase completa conforme ROADMAP.md
5. Criar ou atualizar `SESSION_HANDOFF.md` na raiz usando o template `docs/_canon/templates/SESSION_HANDOFF.template.md`.
   O front matter YAML é validado pelo `HANDOFF_COHERENCE_GATE` contra `session_handoff.schema.json`. Campos obrigatórios:
   `data_ultima_sessao`, `branch_ativo`, `modo_operacao: ROADMAP`, `ci_status`, `modulo_foco`, `fase_roadmap`,
   `roadmap_phase` (obrigatório — mesmo valor inteiro de `fase_roadmap`; validado pelo HANDOFF_COHERENCE_GATE contra `session_start.roadmap_phase`),
   `task_type: execute_roadmap_phase`, `boot_profile_id: roadmap_execution`, `task_id`, `resultado`,
   `proxima_acao_permitida` (mín. 10 chars), `bloqueios_ativos`, `evidence_paths` (mín. 1 entrada).
   Seções obrigatórias no corpo: `## Estado Geral`, `## O que foi feito`, `## Evidências`,
   `## Próxima ação permitida`, `## Bloqueios ativos`.

---

## Observabilidade

Emitir ao final de cada tarefa:

```
[ROADMAP] fase:<N> tarefa:<task_id> status:<DONE|BLOCKED|SKIP>
  resultado: <o que foi feito ou por que está bloqueado>
  artefato:  <path do artefato criado/modificado, se houver>
```

Emitir ao final da fase:

```
[ROADMAP] fase:<N> COMPLETA
  criterio_de_done: <ATINGIDO|PENDENTE — listar o que falta>
  proxima_fase: <N+1 ou "aguardar instrução humana">
```

---

## Bloqueios canônicos

| Código | Condição |
|--------|----------|
| `BLOCKED_PHASE_DEPENDENCY` | Critério de Done da fase N-1 não atingido |
| `BLOCKED_CDD_PIPELINE_FAIL` | Pipeline CDD em FAIL e fase ≥ 4 |
| `BLOCKED_DEPLOY_REQUIRES_HUMAN` | Fase 6, 9 ou 12 — deploy de produção requer aprovação |
| `BLOCKED_MISSING_STACK_DECISION` | Stack não definida para o artefato a criar |

Nunca prosseguir ignorando bloqueio. Reportar ao humano em linguagem de produto.
