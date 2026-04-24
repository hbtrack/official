---
doc_type: canon
version: "1.1.0"
last_reviewed: "2026-04-24"
status: active
state_semantics: current-state
---

# Runtime Atual — HB Track

## 0. Objetivo e limite de autoridade

Este documento é o **inventário factual e verificável do que existe e funciona no workspace atual**
do HB Track. Ele responde, de forma objetiva e sem target-state:

- o que está implementado e testado;
- o que está provisionado mas incompleto;
- o que é apenas contrato ou target-state aprovado.

Qualquer afirmação sobre "estado atual" deve ser reconciliável com este documento.  
Este documento **não substitui** contratos, ADRs ou lifecycle — ele apenas espelha o repo.

Fonte de verdade: `src/`, `config/`, `infra/`, `tests/`, `contracts/`, `migrations/`.

---

## 1. Backend — o que existe

### 1.1 Framework e runtime HTTP

| Item | Estado | Evidência |
|------|--------|-----------|
| Django 5.x + Django Ninja 1.x | **materializado** | `config/settings.py`, `config/urls.py`, `pyproject.toml` |
| NinjaAPI central com 17 routers montados | **materializado** | `config/urls.py` — todos os 17 módulos importados |
| Python 3.12 | **materializado** | `pyproject.toml` |
| Gerenciamento pelo `manage.py` | **materializado** | `manage.py` na raiz |

### 1.2 Banco de dados

| Item | Estado | Evidência |
|------|--------|-----------|
| PostgreSQL via Django ORM | **materializado** | `config/settings.py` (conexão via env `DATABASE_URL` / `DATABASES`) |
| PostgreSQL local em container | **materializado** | `infra/docker-compose.yml` — serviço `postgres:16` |
| Migrations para todos os 17 módulos | **materializado** | `src/<module>/migrations/` presentes em todos os módulos |

**Nota:** o target-state aprovado é PostgreSQL 16. O compose local usa `postgres:16` (alinhado ao target — PR-2/parity/toolchain-manifest).

### 1.3 Redis

| Item | Estado | Evidência |
|------|--------|-----------|
| Redis local em container | **provisionado** | `infra/docker-compose.yml` — serviço `redis` |
| Redis usado como broker Celery | **materializado** | `config/settings.py` — `CELERY_BROKER_URL` configurado; `config/celery.py` existe |
| Redis usado por Django Channels | **materializado** | `config/settings.py` — `CHANNEL_LAYERS` configurado com backend Redis |

### 1.4 Módulos backend (17/17)

Todos os 17 módulos canônicos possuem app Django materializado:

| Módulo | Tipo | Backend app | Migrations | Testes |
|--------|------|-------------|------------|--------|
| `identity_access` | transversal | ✓ | ✓ | ✓ |
| `audit` | transversal | ✓ | ✓ | ✓ |
| `notifications` | transversal | ✓ | ✓ | ✓ |
| `users` | funcional | ✓ | ✓ | ✓ |
| `seasons` | funcional | ✓ | ✓ | ✓ |
| `teams` | funcional | ✓ | ✓ | ✓ |
| `training` | funcional | ✓ | ✓ | ✓ |
| `wellness` | funcional | ✓ | ✓ | ✓ |
| `medical` | funcional | ✓ | ✓ | ✓ |
| `competitions` | funcional | ✓ | ✓ | ✓ |
| `matches` | funcional | ✓ | ✓ | ✓ |
| `scout` | funcional | ✓ | ✓ | ✓ |
| `exercises` | funcional | ✓ | ✓ | ✓ |
| `analytics` | funcional | ✓ | ✓ | ✓ |
| `reports` | funcional | ✓ | ✓ | ✓ |
| `ai_ingestion` | funcional | ✓ | ✓ | ✓ |
| `video` | funcional | ✓ | ✓ | ✓ |

Cada módulo possui as camadas: `Interface/API → Application → Domain → Infrastructure`.

---

## 2. Contratos — o que existe

| Tipo | Cobertura | Evidência |
|------|-----------|-----------|
| OpenAPI paths por módulo | 17/17 | `contracts/openapi/paths/<module>.yaml` |
| JSON Schema por módulo | 17/17 | `contracts/schemas/<module>/` |
| AsyncAPI (eventos) | parcial | `contracts/asyncapi/` — módulos com eventos declarados |
| State models (FSM) | 2 ( `training`, `video`) | `contracts/state_models/` |
| UI Contracts | parcial | módulos selecionados |

---

## 3. Testes — o que existe

| Tipo | Estado | Evidência |
|------|--------|-----------|
| Testes unitários por módulo | **materializados** | `src/<module>/tests/unit/` |
| Testes de integração por módulo | **materializados** | `src/<module>/tests/integration/` |
| Testes de pipeline/gates | **materializados** | `tests/pipeline_gates/` |
| Testes de invariantes globais | **materializados** | `tests/` raiz, `conftest.py` |
| CI local (`pytest`) | **materializado** | `pyproject.toml`, task `Verify Invariants Tests` |

---

## 4. Infraestrutura e tooling — o que existe

| Item | Estado | Evidência |
|------|--------|-----------|
| `infra/docker-compose.yml` (dev) | **materializado** | `infra/docker-compose.yml` |
| Dockerfile de produção | **materializado** | `Dockerfile` na raiz do repositório |
| `docker-compose.prod.yml` / staging | **materializado** | `infra/docker-compose.staging.yml` existe |
| `nginx.conf` | **materializado** | `infra/nginx.conf`, `infra/nginx.production.conf`, `infra/nginx.staging.conf` e variantes |
| Endpoint `GET /health` | **materializado** | `config/urls.py:144` — `path("health", health_check)` |

---

## 5. Observabilidade — o que existe

| Item | Estado | Evidência |
|------|--------|-----------|
| `correlation_id` no módulo `audit` | **implementado** (pontual) | `src/audit/domain/entities.py`, `schemas.py`, `infrastructure/models.py` |
| Middleware de propagação `X-Flow-ID` end-to-end | **materializado** | `config/settings.py:80` — `shared.middleware.FlowIDMiddleware` em `MIDDLEWARE` |
| Logging estruturado em JSON (`structlog` ou equivalente) | **materializado** | `config/settings.py:208` — `FlowIDFormatter` configurado; `src/shared/logging_formatters.py` |
| Rastreabilidade de requests entre módulos | **materializado** | `X-Flow-ID` propagado via `FlowIDMiddleware` em todos os requests |

---

## 6. Frontend — o que existe

| Item | Estado | Evidência |
|------|--------|-----------|
| Diretório `frontend/` | **materializado** | `frontend/` existe com `src/`, `package.json`, `vite.config.ts` |
| Toolchain React/Vite | **materializado** | `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tailwind.config.ts` |
| Tipos gerados `schema.d.ts` | **parcial** | `frontend/src/` existe; execução de `npm run api:generate` pendente de verificação |

---

## 7. Target-state aprovado (não materializado)

Os itens abaixo têm aprovação arquitetural formal mas **ainda não estão completamente materializados** ou dependem de provisionamento externo:

| Item | Aprovação | Bloqueio atual |
|------|-----------|----------------|
| Worker Celery em produção (container separado) | ADR-031 | `config/celery.py` e `tasks.py` existem; container de worker precisa de provisionamento infra |
| WebSocket / Channels em produção | ADR-031 | `CHANNEL_LAYERS` configurado; requer ASGI server (Daphne/uvicorn) em produção |
| Tipos gerados `schema.d.ts` via `npm run api:generate` | ADR-030 | `frontend/` existe; geração precisa ser executada no CI |

---

## 8. Regras de uso deste documento

- Este documento só é atualizado quando existir evidência concreta no repo (arquivo, código, migration, teste).
- Target-state aprovado não migra para este documento sem materialização correspondente.
- Conflito entre este documento e qualquer outro doc arquitetural deve ser resolvido a favor das evidências do repo.
- Data de última revisão deve ser atualizada quando qualquer item mudar de estado.

---

## 9. Referências

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [C4_CONTAINERS.md](./C4_CONTAINERS.md)
- [C4_COMPONENTS_BACKEND.md](./C4_COMPONENTS_BACKEND.md)
- [MODULE_REGISTRY.yaml](./MODULE_REGISTRY.yaml)
- [DEPLOY_PIPELINE.md](./DEPLOY_PIPELINE.md)
- [decisions/ADR-013-logging-policy.md](./decisions/ADR-013-logging-policy.md)
- [decisions/ADR-031-backend-framework.md](./decisions/ADR-031-backend-framework.md)
