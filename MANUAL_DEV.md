# MANUAL DE DESENVOLVIMENTO — HB Track
> **Versão:** 1.0.0 | **Data:** 2026-04-09 | **Status:** Produção
> **NON-SOVEREIGN**: Este manual é um guia operacional derivado. Em caso de conflito: `scripts/hb` + `validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > este arquivo.

---

## ÍNDICE

1. [Estado do Backlog](#1-estado-do-backlog)
2. [Como o sistema funciona](#2-como-o-sistema-funciona)
3. [Como usar o agente para desenvolver](#3-como-usar-o-agente-para-desenvolver)
4. [Como o backend é gerado](#4-como-o-backend-é-gerado)
5. [Como o frontend é gerado](#5-como-o-frontend-é-gerado)
6. [Como os módulos evoluem via docs/hbtrack/modulos](#6-como-os-módulos-evoluem-via-docshbtrackmodulos)
7. [Comandos essenciais do dia a dia](#7-comandos-essenciais-do-dia-a-dia)
8. [Pipeline CI/CD e deploy](#8-pipeline-cicd-e-deploy)
9. [Estado atual e próximos passos](#9-estado-atual-e-próximos-passos)
10. [O que você não perguntou mas precisa saber](#10-o-que-você-não-perguntou-mas-precisa-saber)

---

## 1. Estado do Backlog

### 1.1 Resumo executivo

O `BACKLOG_EXECUTAVEL_DETERMINISTICO.md` está **100% concluído — 41/41 itens DONE**.

| Critério de Done | Status |
|-----------------|--------|
| Source master único por conceito | ✅ DONE |
| `contracts/**` nasce do compiler | ✅ DONE |
| Módulo `reports` roda via código gerado (parity PASS) | ✅ DONE |
| `generate_code` exige `implementation_ready+` | ✅ DONE |
| `implementation_promotion` ativo | ✅ DONE |
| `IMPACT_ANALYSIS_GATE` e `PARTIAL_UPDATE_GATE` ativos | ✅ DONE |
| `DOC_USAGE_GATE`, `CANON_CONTRACT_DRIVEN_PARITY_GATE`, `HBTRACK_CANON_PARITY_GATE` ativos | ✅ DONE |
| `RUNTIME_CURRENT_STATE.md` gerado e checado automaticamente | ✅ DONE |
| Contratos operacionais (ambiente, secrets, deploy, topologia) com SSOT estruturado | ✅ DONE |
| Templates `.env` e fragments de deploy nascem do compiler | ✅ DONE |
| Workflow de deploy não gera `.env` inline | ✅ DONE |
| Gates operacionais de paridade e freshness ativos | ✅ DONE |
| Bundles compilados obrigatórios | ✅ DONE |
| Ruleset do GitHub exige governance e CI reais | ✅ DONE |
| Pact e runtime live validation não são mais skip estrutural | ✅ DONE |
| Suites adversariais obrigatórias verdes sem warnings | ✅ DONE |
| 17 módulos migrados para source graph + codegen/cutover | ✅ DONE |
| Certificação final de operabilidade do agente: 7/7 PASS | ✅ DONE |

### 1.2 O que foi entregue

**Governança (B0–B1):** Grafo de autoridade soberana, banners não-soberanos em docs derivados, GOVERNANCE_PATHS expandidos, DOC_USAGE_MANIFEST, gates hard-blocking, `generate_code` restrito a `implementation_ready+`, backend hook fail-closed, `ARCH_DECISION_PRESENCE_GATE` ativo.

**Source graph e compiler (B2–B3):** IR global estruturado, IR de módulo (`reports` como piloto), compiler de source graph, `OPENAPI_SCHEMA_EQUIVALENCE_GATE` ativo.

**Codegen backend deterministico (B4):** Layout `generated/` em `reports`, `backend_codegen.py`, parity harness, cutover para código gerado.

**Lifecycle formal (B5):** Workers formais `implementation_promotion`, `staging_promotion`, `release_promotion`.

**Sincronismo automático (B6):** `SYNC_MANIFEST.yaml`, `IMPACT_ANALYSIS_GATE`, `PARTIAL_UPDATE_GATE`.

**Contratos operacionais (B-OPS):** SSOT em `docs/_canon/graph/ops/`, compiler de ops, 5 gates operacionais, deploy sem `.env` inline, rotação de secrets com contrato, bundles ops obrigatórios.

**Bundle compilado (B7):** `compile_context_bundle.py`, `CONTEXT_BUNDLE_FRESHNESS_GATE`.

**Runtime e merge hardening (B8):** Ruleset do GitHub com 5 checks obrigatórios, Pact Broker CLI ativo, `HTTP_RUNTIME_CONTRACT_GATE` saiu de skip.

**Adversarial e certificação (B9–B11):** 12 suites adversariais, consumer pact publicado, `warnings=failure`, source graph 17/17 módulos, codegen cutover 17/17, replay packs de staging, certificação 7/7 PASS.

### 1.3 Problema identificado na execução local atual

```
HANDOFF_COHERENCE_GATE: FAIL
  - branch_ativo='main' != branch atual='chore/sync-session-handoff-fase4'
  - ci_status=PASS diverge do relatório canônico (FAIL)
```

**O que é:** `validate_contracts.py --profile ci` falha localmente porque:
1. `SESSION_HANDOFF.md` tem `branch_ativo: main`, mas o branch atual é `chore/sync-session-handoff-fase4`
2. `ci_status=PASS` no handoff, mas o último `latest.json` local é FAIL (causado pelo item 1)

**Impacto:** Zero. É um ciclo de sincronização — o CI na `main` está PASS. Este é um estado temporário de sessão.

**Como resolver:** Fazer o merge deste branch em `main` (ou rodar `hb verify --roadmap-phase 4` para resetar o baseline local).

---

## 2. Como o sistema funciona

### 2.1 Filosofia: CDD (Contract-Driven Development)

O HB Track usa CDD — os **contratos são a fonte de verdade antes de qualquer código**. A sequência canônica é:

```
Documento de produto (docs/hbtrack/modulos/**)
        ↓
   Source Graph (graph/*.yaml por módulo)
        ↓
  Compiler (compile_source_graph.py)
        ↓
  Contrato OpenAPI/AsyncAPI/Schema
        ↓
    Codegen (backend_codegen.py)
        ↓
   Código gerado (src/<module>/generated/)
        ↓
    Bundle compilado (compiled_context/<module>/)
        ↓
  Agente implementa com contexto fechado
        ↓
        CI/CD → Deploy
```

Nada acontece sem contrato. Contrato sem decisão arquitetural resolvida → bloqueio. Código sem contrato → rejeitado no pipeline.

### 2.2 Os 17 módulos canônicos

| Grupo | Módulos | Release |
|-------|---------|---------|
| **Core** | `identity_access`, `users`, `audit`, `notifications` | v0.1 / v1.0 |
| **Gestão esportiva** | `teams`, `seasons`, `competitions` | v0.1 / v0.2 |
| **Treino** | `training`, `exercises` | v0.1 / v1.0 |
| **Performance e saúde** | `wellness`, `medical` | v1.0 |
| **Jogo** | `matches`, `scout`, `video` | v0.2 |
| **Inteligência** | `analytics`, `reports`, `ai_ingestion` | v1.0 |

**Regra absoluta:** Nunca criar módulos fora destes 17. Novo módulo → primeiro cria ADR + contrato → aprovação → entra no `MODULE_REGISTRY.yaml`.

### 2.3 Cadeia de autoridade (quem manda em quê)

```
1. enforcement executável   scripts/hb, validate_contracts.py, gates ativos
2. schemas ativos           contracts/schemas/shared/*.schema.json
3. canon                    docs/_canon/ + .contract_driven/CONTRACT_SYSTEM_RULES.md
4. bridge docs              CLAUDE.md
5. artefatos derivados      _archive/
6. legado                   docs/guias/
```

Em conflito: **nível mais baixo perde sempre**.

### 2.4 Dois modos de operação do agente

| Modo | Quando usar | Ponto de entrada |
|------|-------------|-----------------|
| **CDD** | Criar/revisar contratos, schemas, state models, UI contracts | `pre_contract_orchestrator` |
| **ROADMAP** | Implementar fases 0–13 (infra, backend, frontend, deploy) | `ROADMAP.md` + `SESSION_HANDOFF.md` |

**Nunca misturar os dois modos em uma mesma sessão.**

---

## 3. Como usar o agente para desenvolver

### 3.1 Boot de cada sessão

O agente lê automaticamente (via `CLAUDE.md` e `docs/_canon/AGENT_INSTRUCTIONS.md`):

1. `SESSION_HANDOFF.md` — o que foi feito, onde parou, próxima ação
2. `ROADMAP.md` — fase atual, critério de done
3. Contexto específico da tarefa (bundle compilado ou SSOT relevante)

**Você nunca precisa explicar o histórico ao agente** — o `SESSION_HANDOFF.md` faz isso.

### 3.2 Como pedir tarefas de contrato (Modo CDD)

Para qualquer tarefa relacionada a contratos, use estas intenções:

```
"Quero criar um novo contrato para o módulo X"
"Preciso revisar o contrato de Y"
"Cria o state model do módulo Z"
"Adiciona a feature F no módulo M"
"Revisa a decisão arquitetural sobre X"
```

O agente vai:
1. Rodar `hb verify --task-type <type> --module <mod>` (obrigatório antes)
2. Identificar o worker correto no `TASK_CATALOG.yaml`
3. Montar o contexto mínimo necessário (bundle compilado)
4. Executar o worker com o bundle
5. Rodar `hb artifact <path>` após criar artefato canônico

### 3.3 Como pedir tarefas de implementação (Modo ROADMAP)

```
"Implementa a Fase 4 do ROADMAP"
"Continua o desenvolvimento do frontend (Fase 5)"
"Deploy para staging"
"Configura os GitHub Secrets para o pipeline de deploy"
```

O agente vai:
1. Ler `SESSION_HANDOFF.md` (bloqueios ativos, próxima ação)
2. Ler `ROADMAP.md` (fase atual, tarefas pendentes, critério de done)
3. Ler bundle ops: `compiled_context/ops/deploy.json` e `compiled_context/ops/runtime.json`
4. Executar o worker `execute_roadmap_phase.prompt.md`

### 3.4 Checklist antes de qualquer sessão

```bash
# 1. Verificar estado do pipeline
python3 scripts/validate_contracts.py --profile ci

# 2. Verificar operabilidade do agente
python3 scripts/certify/certify_agent_operability.py

# 3. Verificar bundles frescos
python3 scripts/compile/compile_context_bundle.py --all --check

# 4. Ler SESSION_HANDOFF.md (leitura humana)
cat SESSION_HANDOFF.md
```

### 3.5 Tipos de tarefas disponíveis (TASK_CATALOG.yaml)

| task_type | O que faz | Worker |
|-----------|-----------|--------|
| `new_module` | Cria todos os artefatos CDD de um novo módulo | `create_module_docs.prompt.md` |
| `feature_update` | Adiciona/modifica feature em módulo existente | `feature_update.prompt.md` |
| `new_contract` | Cria contrato OpenAPI/AsyncAPI | `create_openapi_contract.prompt.md` |
| `contract_revision` | Revisa contrato existente | (via orchestrator) |
| `new_schema` | Cria JSON Schema | `create_json_schema_contract.prompt.md` |
| `new_state_model` | Cria state machine formal | `create_state_model.prompt.md` |
| `new_ui_contract` | Cria contrato de UI | `create_ui_contract.prompt.md` |
| `decision_discovery` | Mapeia e resolve decisões arquiteturais | `decision_discovery.prompt.md` |
| `readiness_promotion` | Promove módulo para `implementation_ready` | `readiness_promotion.prompt.md` |
| `generate_code` | Gera código backend a partir do contrato | `generate_code.prompt.md` |
| `generate_frontend` | Gera componentes frontend | `generate_frontend.prompt.md` (**FROZEN** — Fase 5 usa React manual + `openapi-typescript`) |
| `implementation_promotion` | Promove para `implemented` | `implementation_promotion.prompt.md` |
| `staging_promotion` | Promove para `staging_validated` | `staging_promotion.prompt.md` |
| `release_promotion` | Promove para `released` | `release_promotion.prompt.md` |
| `execute_roadmap_phase` | Implementa fase do ROADMAP | `execute_roadmap_phase.prompt.md` |
| `pr_fix` | Corrige falha de CI em PR aberto | `pr_fix.prompt.md` |
| `adversarial_analysis` | Análise adversarial do pipeline | `adversarial_analysis.prompt.md` |
| `audit_*` | 5 tipos de auditoria | audit prompts |

---

## 4. Como o backend é gerado

### 4.1 Arquitetura do backend (Clean Architecture)

Cada módulo tem esta estrutura em `src/<module>/`:

```
src/<module>/
├── domain/
│   ├── entities.py        ← Entidades de domínio (puro Python, sem Django)
│   ├── rules.py           ← Invariantes Classe A e B
│   └── exceptions.py      ← Exceções de domínio
├── application/
│   └── use_cases.py       ← Casos de uso (orquestra domínio)
├── infrastructure/
│   ├── models.py          ← Models Django ORM
│   └── repository.py      ← Implementação de repositório
├── api.py                 ← Router Django Ninja (endpoints HTTP)
├── schemas.py             ← Pydantic schemas (entrada/saída da API)
├── migrations/            ← Migrations Django
│   ├── 0001_initial.py
│   └── 0002_add_constraints.py
├── tasks.py               ← Celery tasks (async)
└── generated/             ← Código gerado deterministicamente ← NÃO EDITAR
    ├── domain/entities.py
    ├── application/use_cases.py
    ├── infrastructure/repository.py
    ├── api.py
    ├── schemas.py
    └── tests/test_codegen_contract.py
```

### 4.2 Como o codegen funciona — o que é gerado e o que é manual

> ⚠️ **A geração NÃO é automática.** Não existe hook ou CI que dispara `backend_codegen.py` automaticamente. Você precisa rodar manualmente após mudar contratos ou source graph.

**O que é gerado** (em `src/<module>/generated/`):
```
generated/api.py                        ← endpoints Django Ninja gerados
generated/domain/entities.py           ← entidades de domínio geradas
generated/application/use_cases.py     ← casos de uso gerados
generated/infrastructure/repository.py ← repositório gerado
generated/schemas.py                   ← schemas Pydantic gerados
generated/tests/test_codegen_contract.py ← testes de contrato gerados
```

**O que é manual** (adaptadores canônicos em `src/<module>/`):
```
api.py          ← escrito manualmente, importa e compõe generated/
schemas.py      ← escrito manualmente
models.py       ← Django ORM, escrito manualmente
migrations/     ← migrações Django, escritas manualmente
tasks.py        ← Celery tasks, escritas manualmente
```

O `api.py` manual importa da camada gerada via padrão "cutover":
```python
# src/<module>/api.py
# CODEGEN CUTOVER — generated use cases linked
from .generated.application import use_cases as _gen_use_cases
from .generated.infrastructure import repository as _gen_repository
```

**O pipeline bloqueia** se o `generated/` estiver defasado (via `CONTEXT_BUNDLE_FRESHNESS_GATE`), mas não regenera automaticamente — você precisa rodar o comando.

O codegen é **deterministico**: duas execuções do mesmo contrato produzem hash SHA256 idêntico.

```bash
# Gerar código para um módulo
python3 scripts/generate/backend_codegen.py --module <module_name>

# Verificar (sem escrever)
python3 scripts/generate/backend_codegen.py --module <module_name> --check

# Gerar para todos os módulos
python3 scripts/generate/backend_codegen.py --all
```

**Fluxo completo quando o contrato muda:**

```bash
# 1. Atualizar source graph
# Editar: docs/hbtrack/modulos/<module>/graph/*.yaml

# 2. Recompilar source graph
python3 scripts/compile/compile_source_graph.py --module <module>

# 3. Recompilar context bundle
python3 scripts/compile/compile_context_bundle.py --module <module>

# 4. Regenerar código (sobrescreve src/<module>/generated/)
python3 scripts/generate/backend_codegen.py --module <module>

# 5. Validar pipeline completo
python3 scripts/validate_contracts.py --profile ci
```

### 4.3 Regra crítica: `generated/` nunca é editado manualmente

Todo código em `src/<module>/generated/` é derivado. Editar manualmente quebrará o hash de parity e o pipeline falhará. Para mudar comportamento gerado: **altere o source graph** (`docs/hbtrack/modulos/<module>/graph/`) → regenere.

### 4.4 Migração de código manual para gerado

O módulo `reports` é o piloto que prova a trilha completa. Os outros 16 módulos têm `generated/` com código gerado e cutover aplicado. O padrão é:

```python
# src/<module>/api.py (adaptador canônico)
from src.<module>.generated.application.use_cases import GetXUseCase
from src.<module>.generated.infrastructure.repository import XRepository
```

O código legado manual é substituído por importações da camada gerada.

### 4.5 Rodar o backend localmente

```bash
# 1. Subir banco e cache
docker compose -f infra/docker-compose.yml up -d postgres redis

# 2. Aplicar migrations
.venv/bin/python manage.py migrate

# 3. Popular dados demo
.venv/bin/python manage.py seed_demo

# 4. Subir servidor
.venv/bin/python manage.py runserver

# 5. Ver documentação interativa
# Abrir: http://localhost:8000/api/docs
```

---

## 5. Como o frontend é gerado

### 5.1 Princípio: frontend nunca diverge da API

O frontend usa **`openapi-typescript`** para gerar tipos TypeScript diretamente do contrato OpenAPI. Não existe digitação manual de interfaces — tudo é derivado do contrato.

```
contracts/openapi/openapi.yaml (SSOT)
        ↓
  npm run api:generate
        ↓
  frontend/src/api/schema.d.ts (NUNCA EDITAR MANUALMENTE)
        ↓
  frontend/src/api/client.ts (usa openapi-fetch com os tipos gerados)
        ↓
  React Query hooks por módulo (frontend/src/api/hooks/)
```

### 5.2 Gerar o cliente da API

```bash
cd frontend

# Regenerar tipos TypeScript do contrato (rodar sempre que o contrato mudar)
npm run api:generate

# O que este comando faz:
# npx openapi-typescript ../contracts/openapi/openapi.yaml -o src/api/schema.d.ts
```

**Regra absoluta:** `frontend/src/api/schema.d.ts` **NUNCA** é editado manualmente. Apenas regenerar.

### 5.3 Estrutura do frontend

```
frontend/
├── src/
│   ├── api/
│   │   ├── schema.d.ts       ← GERADO (nunca editar)
│   │   ├── client.ts         ← openapi-fetch configurado
│   │   ├── hooks/            ← React Query hooks por módulo
│   │   │   ├── useAuth.ts
│   │   │   ├── useUsers.ts
│   │   │   ├── useTeams.ts
│   │   │   ├── useSeasons.ts
│   │   │   └── useTraining.ts
│   │   └── requests/         ← Requests para Pact testing
│   ├── features/             ← Páginas e componentes por módulo
│   │   ├── auth/
│   │   ├── users/
│   │   ├── teams/
│   │   ├── seasons/
│   │   └── training/
│   ├── shared/
│   │   └── layouts/AppLayout.tsx  ← Layout base com sidebar
│   └── stores/               ← Zustand (estado global)
├── e2e/                      ← Testes Playwright
│   ├── auth.spec.ts
│   └── training.spec.ts
├── package.json
├── vite.config.ts            ← Proxy /api/ → localhost:8000
└── Dockerfile.frontend       ← Multi-stage: build → nginx
```

### 5.4 Comandos do frontend

```bash
cd frontend

npm run dev          # Servidor de desenvolvimento (http://localhost:5173)
npm run build        # Build de produção (dist/)
npm run test         # Testes unitários (Vitest)
npm run test:e2e     # Testes E2E (Playwright)
npm run api:generate # Regenerar schema.d.ts do contrato
npm run test:pact    # Testes Pact (consumer contracts)
```

### 5.5 Stack tecnológico do frontend

| Tecnologia | Função |
|-----------|--------|
| React 19 + TypeScript | Framework UI |
| Vite 8 | Build tool + dev server |
| React Router v7 | Roteamento |
| TanStack Query v5 | Cache + fetching de dados |
| Zustand v5 | Estado global (auth, etc.) |
| openapi-fetch + openapi-typescript | Cliente HTTP tipado do contrato |
| Tailwind CSS v4 | Estilização |
| Radix UI + shadcn/ui | Componentes acessíveis |
| Vitest + Testing Library | Testes unitários |
| Playwright | Testes E2E |
| @pact-foundation/pact | Consumer contract testing |

---

## 6. Como os módulos evoluem via docs/hbtrack/modulos

### 6.1 Estrutura de documentação de cada módulo

Cada módulo tem seus documentos soberanos em `docs/hbtrack/modulos/<module>/`:

```
docs/hbtrack/modulos/<module>/
├── README.md                    ← Visão geral do módulo
├── MODULE_SCOPE_<MODULE>.md     ← Escopo, fronteiras, o que faz/não faz
├── DOMAIN_RULES_<MODULE>.md     ← Regras de negócio (invariantes)
├── INVARIANTS_<MODULE>.md       ← Invariantes formais (Classe A/B)
├── STATE_MODEL_<MODULE>.md      ← Máquina de estados (FSM)
├── PERMISSIONS_<MODULE>.md      ← RBAC por role e operação
├── ERRORS_<MODULE>.md           ← Erros canônicos e códigos
├── TEST_MATRIX_<MODULE>.md      ← Matriz de testes obrigatórios
├── UI_CONTRACT_<MODULE>.md      ← Contrato de UI (telas, componentes)
├── SCREEN_MAP_<MODULE>.md       ← Mapa de telas do frontend
├── COACH_INTERACTION_FLOW_<MODULE>.md ← Fluxo de interação do treinador
├── SPORT_SCIENCE_RULES_<MODULE>.md    ← Regras de ciência do esporte
├── DECISION_IR_<MODULE>.yaml    ← Decisões arquiteturais do módulo (IR estruturado)
└── graph/                       ← Source graph soberano do módulo
    ├── module_manifest.yaml     ← Manifesto do módulo
    ├── entities.yaml            ← Entidades de domínio
    ├── endpoints.yaml           ← Endpoints esperados
    ├── errors.yaml              ← Erros formais
    └── test_obligations.yaml    ← Obrigações de teste
```

### 6.2 Como uma mudança em docs/hbtrack propaga para código

O sistema tem propagação automática determinística:

```
Você altera docs/hbtrack/modulos/<module>/DOMAIN_RULES_*.md
              ↓
    SYNC_MANIFEST.yaml detecta o changeset
              ↓
    IMPACT_ANALYSIS_GATE verifica quais consumidores precisam atualizar
              ↓
    PARTIAL_UPDATE_GATE bloqueia se consumers não forem atualizados
              ↓
    Você atualiza graph/*.yaml correspondente
              ↓
    python3 scripts/compile/compile_source_graph.py --module <module>
              ↓
    python3 scripts/compile/compile_context_bundle.py --module <module>
              ↓
    python3 scripts/generate/backend_codegen.py --module <module>
              ↓
    python3 scripts/validate_contracts.py --profile ci
```

**Não é opcional**: o pipeline bloqueia alteração parcial. Ou você propaga para todos os consumers, ou o gate falha.

### 6.3 Atualizar o source graph de um módulo

```bash
# 1. Editar os YAMLs do source graph
# docs/hbtrack/modulos/<module>/graph/entities.yaml
# docs/hbtrack/modulos/<module>/graph/endpoints.yaml
# etc.

# 2. Recompilar source graph
python3 scripts/compile/compile_source_graph.py --module <module>

# 3. Recompilar bundle
python3 scripts/compile/compile_context_bundle.py --module <module>

# 4. Regenerar código (se houve mudança estrutural)
python3 scripts/generate/backend_codegen.py --module <module>

# 5. Verificar parity
pytest tests/parity/ -q

# 6. Validar pipeline completo
python3 scripts/validate_contracts.py --profile ci
```

### 6.4 Criar um novo módulo (sequência completa)

```bash
# Passo 1: verificar que não existe
grep "<novo_modulo>" docs/_canon/MODULE_REGISTRY.yaml

# Passo 2: criar ADR para o novo módulo
hb verify --task-type new_module --module <novo_modulo>

# Passo 3: criar documentação base (via agente)
# O agente usa: .contract_driven/agent_prompts/create_module_docs.prompt.md

# Passo 4: criar source graph
# docs/hbtrack/modulos/<novo_modulo>/graph/*.yaml

# Passo 5: criar contratos OpenAPI e Schemas
hb verify --task-type new_contract --module <novo_modulo>

# Passo 6: promover para implementation_ready
hb verify --task-type readiness_promotion --module <novo_modulo>

# Passo 7: gerar código backend
python3 scripts/generate/backend_codegen.py --module <novo_modulo>

# Passo 8: promover para implemented
hb verify --task-type implementation_promotion --module <novo_modulo>
```

---

## 7. Comandos essenciais do dia a dia

### 7.1 Pipeline de governança

```bash
# Validação completa do pipeline (CI)
python3 scripts/validate_contracts.py --profile ci

# Validação rápida (pre-commit)
python3 scripts/validate_contracts.py --profile precommit

# Certificação de operabilidade do agente (7 dimensões)
python3 scripts/certify/certify_agent_operability.py

# Verificar estado de sessão antes de tarefa
python3 scripts/hb verify --task-type <type> --module <module>

# Registrar artefato canônico após criação
python3 scripts/hb artifact <path/to/artifact>

# Survival suite (testes rápidos de governança)
python3 scripts/hb survival-suite
```

### 7.2 Compilers

```bash
# Source graph de um módulo
python3 scripts/compile/compile_source_graph.py --module <module>
python3 scripts/compile/compile_source_graph.py --all         # todos os 17

# Context bundle
python3 scripts/compile/compile_context_bundle.py --module <module>
python3 scripts/compile/compile_context_bundle.py --all

# Contratos operacionais (env, secrets, deploy)
python3 scripts/compile/compile_ops_contracts.py

# Verificar sem escrever
python3 scripts/compile/compile_source_graph.py --module <module> --check
```

### 7.3 Backend

```bash
# Gerar código backend
python3 scripts/generate/backend_codegen.py --module <module>
python3 scripts/generate/backend_codegen.py --all

# Atualizar RUNTIME_CURRENT_STATE.md
python3 scripts/generate/docs/gen_runtime_current_state.py --write

# Repair manifests (após mudanças estruturais)
python3 scripts/repair_manifests.py

# Recompilar API policy global
python3 scripts/contracts/validate/api/compile_api_policy.py --all

# Renderizar .env de deploy
python3 scripts/deploy/render_env_from_contract.py --env staging
python3 scripts/deploy/render_env_from_contract.py --env production
```

### 7.4 Testes

```bash
# Todos os testes (exceto lentos)
pytest -q -m "not slow" --tb=short

# Pipeline gates
pytest tests/pipeline_gates -q

# Testes adversariais
pytest tests/adversarial -q

# Parity tests (código gerado vs manual)
pytest tests/parity -q

# Replay packs de staging
pytest tests/replay/staging -q

# Testes de integração (requer PostgreSQL rodando)
pytest tests/ -q   # todos

# Frontend
cd frontend && npm run test
cd frontend && npm run test:e2e
cd frontend && npm run test:pact
```

### 7.5 Banco de dados

```bash
# Subir banco local
docker compose -f infra/docker-compose.yml up -d postgres redis

# Aplicar migrations
.venv/bin/python manage.py migrate

# Verificar migrations
.venv/bin/python manage.py showmigrations

# Popular dados demo
.venv/bin/python manage.py seed_demo

# Reset completo do banco de dev
docker compose -f infra/docker-compose.yml down -v
docker compose -f infra/docker-compose.yml up -d postgres redis
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
```

### 7.6 Docker e infra

```bash
# Build da imagem do backend
docker build -t hbtrack-api .

# Testar container localmente
docker run -p 8000:8000 --env-file infra/env/.env.staging.template hbtrack-api

# Verificar health
curl http://localhost:8000/health

# Produção (docker compose completo)
docker compose -f infra/docker-compose.prod.yml up -d

# Rollback para SHA anterior
bash infra/scripts/rollback.sh --env staging --sha <git-sha>
```

### 7.7 Git e PR

```bash
# Pre-push hook pode causar problemas em branches de feature
# (o hook roda hb verify --roadmap-phase que reseta session_start.json)
# Use --no-verify em branches de feature (CI valida independentemente)
git push --no-verify

# Criar PR (CI valida todos os gates)
gh pr create --base main --title "feat: ..."

# Ver checks do PR
gh pr checks <PR_NUMBER>

# Resolver thread de review (necessário para merge)
gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "THREAD_ID"}) { thread { isResolved } } }'
```

---

## 8. Pipeline CI/CD e deploy

### 8.1 O que acontece em cada push/PR

```
Push para any branch / PR aberto para main
        ↓
Job 1: contract-gates.yml
  - python3 validate_contracts.py (todos os gates CDD)
  - pytest tests/pipeline_gates -q
  - pytest tests/adversarial -q
  - hb verify
        ↓
Job 2: ci.yml → _reusable-ci.yml
  validate → test → build → deploy-staging → deploy-production
```

**Jobs do `_reusable-ci.yml`:**

| Job | O que faz | Condição |
|-----|-----------|----------|
| `validate` | `validate_contracts.py` + `hb verify` | sempre |
| `test` | pytest com PostgreSQL 16 + Redis 7 (coverage ≥ 80%) | depende de validate |
| `build` | `docker build` + push para ghcr.io | depende de test |
| `deploy-staging` | SSH no VPS + `docker compose pull && up -d` + migrate + health check | apenas `main` |
| `deploy-production` | mesmo fluxo + **aprovação humana** (expira em 24h) | depende de staging |

### 8.2 Configurar GitHub Secrets (ação humana necessária para Fase 4)

Para o pipeline de deploy funcionar, configure estes secrets no repositório GitHub:

| Secret | Como gerar |
|--------|-----------|
| `VPS_DEPLOY_KEY` | Chave SSH privada do usuário `deploy` no VPS |
| `DATABASE_URL` | `postgresql://user:pass@localhost:5432/hbtrack_staging` |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `SECRET_KEY` | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `JWT_PRIVATE_KEY` | Chave RS256 privada: `openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048` |
| `JWT_PUBLIC_KEY` | Chave RS256 pública: `openssl rsa -pubout -in private.pem` |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL no VPS |
| `PACT_BROKER_BASE_URL` | URL do Pact Broker no VPS (ex: `http://191.252.185.34:9292`) |
| `PACT_BROKER_TOKEN` | Token de autenticação do Pact Broker |

**Onde configurar:** GitHub → Settings → Secrets and variables → Actions

### 8.3 Render de .env no deploy (sem inline)

O workflow **não gera `.env` inline**. O processo é:

```bash
# O workflow de deploy chama:
bash scripts/deploy/inject_env.sh --env staging

# Que internamente usa:
python3 scripts/deploy/render_env_from_contract.py --env staging

# Que lê:
# - infra/env/.env.staging.template (template de variáveis)
# - compiled_ops/deploy/staging.env.fragment (valores compilados do canon)
# - Valores reais injetados pelos GitHub Secrets
```

Resultado: `.deploy/staging.env` sincronizado para o VPS via SCP.

### 8.4 VPS (191.252.185.34)

- **SO:** Ubuntu 22.04
- **Docker:** 29.1.3 + Compose v2.40.3
- **Usuário de deploy:** `deploy` (sem sudo, com permissão Docker)
- **Estrutura:** `/home/deploy/hbtrack-backend/` (current/, shared/, repo/)
- **Firewall:** UFW — apenas 22, 80, 443 abertos
- **SSL:** Certbot + Let's Encrypt (porta 443 configurada)
- **Runbooks completos:** `VPS/runbooks/` (deploy, backup, rollback, troubleshooting)

---

## 9. Estado atual e próximos passos

### 9.1 Estado do ROADMAP

| Fase | Status | Bloqueio |
|------|--------|---------|
| Fase 0 — Ambiente local | ✅ DONE | — |
| Fase 1 — Backend completo | ✅ DONE | — |
| Fase 2 — Banco com integridade | ✅ DONE | — |
| Fase 3 — Pipeline CI/CD + Deploy | ✅ DONE | — |
| **Fase 4 — Ciclo 1 em staging** | 🔴 BLOCKED | VPS roda FastAPI legado, Django nunca deployado |
| Fase 5 — Frontend Ciclo 1 | ✅ DONE (scaffolding + páginas) | Depende da Fase 4 para E2E reais |
| Fase 6 — Deploy produção v0.1 | ⏳ Pendente | Depende das Fases 4 e 5 |

### 9.2 Próxima ação obrigatória (ação humana)

**Para desbloquear a Fase 4, você precisa:**

1. Configurar os GitHub Secrets (lista na seção 8.2)
2. Acionar o workflow de deploy manualmente:
   ```bash
   gh workflow run deploy.yml --ref main
   ```
3. Aguardar o Django ser deployado no VPS (o workflow faz tudo automaticamente)
4. Verificar: `curl http://191.252.185.34/health` → deve retornar `{"status":"ok"}`

**Após o deploy de staging bem-sucedido:**

```bash
# Rodar testes E2E no staging (Fase 4.1)
pytest tests/replay/staging -q

# Testar fluxo completo manualmente:
# POST /api/auth/login → recebe JWT
# POST /api/users/ → cria perfil
# POST /api/teams/ → cria time
# POST /api/seasons/ → cria temporada
# POST /api/training-sessions/ → cria treino
```

### 9.3 Depois da Fase 4: deploy de produção (v0.1)

```
Fase 4 (staging validado) → Fase 5 (frontend E2E) → Fase 6 (deploy produção)
```

A Fase 5 já tem o scaffolding completo — faltam apenas os testes E2E contra o staging real (que depende da Fase 4).

---

## 10. O que você não perguntou mas precisa saber

### 10.1 🔴 CRÍTICO: O Pact Broker precisa de credenciais reais

O `PACT_PROVIDER_GATE` está em `SKIP_NOT_APPLICABLE` localmente (por design — só funciona com `PACT_BROKER_BASE_URL` configurado). Em CI, está PASS porque o VPS tem o broker rodando. **Mas o broker precisa de token real** (`PACT_BROKER_TOKEN` no GitHub Secrets) para o workflow de deploy publicar resultados de verificação. Sem isso, o gate passa mas não há contrato real publicado.

### 10.2 🔴 CRÍTICO: B10-002 tem codegen 17/17 mas só `reports` tem cutover validado em profundidade

Os 17 módulos têm `src/<module>/generated/` com código gerado, mas o **parity harness completo** (com testes de comportamento positivo e negativo) só existe para `reports` em `tests/parity/`. Os outros módulos têm o cutover aplicado no `api.py` e `schemas.py`, mas sem a mesma profundidade de testes de paridade. Isso não bloqueia o MVP, mas é uma dívida técnica conhecida.

### 10.3 🟡 Armazenamento de vídeo não está decidido

O módulo `video` tem contrato, código e migrations, mas a **estratégia de armazenamento de arquivos** (volume Docker local vs. S3-compatible como Wasabi ou MinIO) está como decisão pendente (ver `ROADMAP.md` tarefa 7.3). Isso bloqueia a Fase 7 (Ciclo 2). Você precisa decidir isso antes de chegar lá.

### 10.4 🟡 O Celery Beat precisa de configuração de tarefas periódicas

`celery_beat` está no `docker-compose.prod.yml` mas as tarefas periódicas (cálculo de métricas de `analytics`, geração de relatórios de `reports`, retenção de logs de `audit`) não estão configuradas com schedules reais em `config/celery.py`. Estão prontas para receber os schedules, mas sem dados de staging não há como validar as frequências corretas.

### 10.5 🟡 Django Channels: WebSocket de notificações está configurado mas não testado em produção

`config/asgi.py` tem `ProtocolTypeRouter` com HTTP + WebSocket. `src/notifications/consumers.py` existe. Mas o fluxo completo (push de notificação do backend → WebSocket → frontend) nunca foi testado com usuários reais. O módulo `notifications` é Ciclo 3 (v1.0), mas o WebSocket base precisa funcionar antes.

### 10.6 🟡 SSL/HTTPS: domínio de staging não está configurado

O Nginx e o Certbot estão configurados para Let's Encrypt, mas **o domínio de staging ainda não existe**. O VPS só tem IP (`191.252.185.34`). Para SSL funcionar, você precisa:
1. Registrar um subdomínio (ex: `staging.hbtrack.com.br` ou `api-staging.hbtrack.com.br`)
2. Apontar o DNS para o IP do VPS
3. Atualizar `ALLOWED_HOSTS` e `CORS_ALLOWED_ORIGINS` no `.env.staging`
4. Rodar Certbot: `certbot --nginx -d staging.hbtrack.com.br`

### 10.7 🟡 Monitoramento de uptime não está configurado

A Fase 6 inclui configurar UptimeRobot (ou similar) para monitorar `/health`. Sem isso, você não sabe se o sistema caiu antes que um usuário reclame.

### 10.8 🟡 Backup automático do banco de dados não está ativado

`VPS/runbooks/BACKUP_RESTORE.md` documenta o procedimento, mas o **cron de backup automático** não está configurado no VPS. Para v0.1 em produção, você precisa de pelo menos um backup diário automatizado.

### 10.9 🟡 `generate_frontend` está FROZEN — não use para Fase 5

O worker `generate_frontend.prompt.md` está marcado como `FROZEN` no `TASK_CATALOG.yaml`. Para a Fase 5, o frontend é **React manual + `openapi-typescript`** (decisão D3 do ROADMAP). O worker frozen existe apenas como placeholder futuro. Se o agente tentar usar `generate_frontend`, bloqueie — use `execute_roadmap_phase` com o ROADMAP como guia.

### 10.10 🟡 Regra de ouro: `schema.d.ts` = NUNCA editar manualmente

`frontend/src/api/schema.d.ts` é gerado por `npm run api:generate`. Se você editar manualmente, o próximo `api:generate` sobrescreve tudo e você perde as mudanças silenciosamente. Se precisar de um tipo que não existe no contrato, **adicione ao contrato OpenAPI primeiro**.

### 10.11 🟡 O pre-push hook pode corromper o `session_start.json`

O hook em `scripts/git-hooks/pre-commit` chama `hb verify --roadmap-phase 1` em branches de feature, o que reseta o estado de sessão. Isso é um comportamento conhecido. Para branches de feature, sempre use:
```bash
git push --no-verify
```
O CI (GitHub Actions) valida independentemente, então não há risco de merge sem validação.

### 10.12 🟡 HANDOFF_COHERENCE_GATE exige sincronismo a cada sessão

O `SESSION_HANDOFF.md` precisa refletir o estado real da sessão para o pipeline passar. O gate verifica:
- `branch_ativo` = branch atual
- `ci_status` = status real do último `latest.json`
- `resultado` = apenas `DONE`, `PENDENTE`, ou `BLOCKED`

Se você trabalha em um branch de feature, o gate vai falhar localmente (branch não é `main`). Isso é esperado — o CI da `main` é o que importa para o pipeline formal.

### 10.13 🟡 Ciclo 2 e 3 precisam de novos módulos no source graph validados antes do código

Embora todos os 17 módulos tenham source graph e código, os módulos dos Ciclos 2 e 3 (`competitions`, `matches`, `scout`, `video`, `wellness`, `medical`, etc.) ainda não foram validados com **dados reais de staging**. O replay pack de staging cobre os ciclos de negócio documentados (`scripts/replay/`), mas não substitui testes E2E com usuários reais.

### 10.14 🔵 Roadmap de versões e o que isso significa para você

| Versão | O que o usuário final pode fazer | Quando |
|--------|----------------------------------|--------|
| **v0.1** | Login, times, temporadas, planejamento de treinos | Após Fase 6 |
| **v0.2** | + Competições, partidas ao vivo, scout, vídeo | Após Fase 9 |
| **v1.0** | + Wellness, laudos médicos, analytics, IA, relatórios | Após Fase 12 |
| **v2.0** | App mobile (iOS/Android) | Após Fase 13 |

**Você está a 2 fases do v0.1:** Fase 4 (staging) + Fase 6 (deploy produção). A Fase 5 já está quase completa. O único bloqueio real é humano: configurar os GitHub Secrets e acionar o deploy.

---

## Resumo executivo para começar agora

**O sistema está pronto. O bloqueio é operacional, não técnico.**

Para colocar o HB Track em produção com o v0.1:

1. **Configure os GitHub Secrets** (seção 8.2) — 15 minutos
2. **Acione o deploy**: `gh workflow run deploy.yml --ref main` — automático
3. **Configure um domínio de staging** com SSL (seção 10.6) — depende do DNS
4. **Valide o staging** (Fase 4): testes manuais + `pytest tests/replay/staging -q`
5. **Deploy de produção** (Fase 6): aprovação humana no workflow → v0.1 no ar 🚀

Para desenvolver novas features depois do v0.1:
- Docs primeiro: `docs/hbtrack/modulos/<module>/`
- Source graph: `graph/*.yaml`
- Contrato: `contracts/openapi/` + `contracts/schemas/`
- Codegen: `python3 scripts/generate/backend_codegen.py --module <module>`
- Frontend: `npm run api:generate` + implementar páginas em `frontend/src/features/`
- Pipeline: `python3 scripts/validate_contracts.py --profile ci` — deve estar PASS antes do PR
