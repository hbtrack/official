---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-23"
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
| Redis usado como broker Celery | **ausente** | nenhuma configuração `CELERY_BROKER_URL` ou `config/celery.py` |
| Redis usado por Django Channels | **ausente** | nenhuma configuração `CHANNEL_LAYERS` |

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
| Dockerfile de produção | **ausente** | nenhum `Dockerfile` na raiz ou em `infra/` |
| `docker-compose.prod.yml` | **ausente** | ausência confirmada |
| `nginx.conf` | **ausente** | ausência confirmada |
| Endpoint `GET /health` | **ausente** | `config/urls.py` não declara rota `/health` |

---

## 5. Observabilidade — o que existe

| Item | Estado | Evidência |
|------|--------|-----------|
| `correlation_id` no módulo `audit` | **implementado** (pontual) | `src/audit/domain/entities.py`, `schemas.py`, `infrastructure/models.py` |
| Middleware de propagação `X-Flow-ID` end-to-end | **ausente** | nenhum middleware em `config/` |
| Logging estruturado em JSON (`structlog` ou equivalente) | **ausente** | nenhuma configuração de structlog em `config/settings.py` |
| Rastreabilidade de requests entre módulos | **ausente** | substituída por `correlation_id` opcional no `audit` |

Leitura correta: ADR-013 define `X-Flow-ID` como target-state. A implementação atual consiste
apenas no campo `correlation_id` no módulo `audit`, sem propagação automática de header.

---

## 6. Frontend — o que existe

| Item | Estado | Evidência |
|------|--------|-----------|
| Diretório `frontend/` | **ausente** | não existe no workspace |
| Toolchain React/Vite | **ausente** | `package.json` contém apenas ferramentas de contratos |
| Tipos gerados `schema.d.ts` | **ausente** | sem `npm run api:generate` executado ainda |

---

## 7. Target-state aprovado (não materializado)

Os itens abaixo têm aprovação arquitetural formal mas **não existem ainda no repo**:

| Item | Aprovação | Bloqueio atual |
|------|-----------|----------------|
| Worker Celery + Redis broker | ADR-031 | sem `config/celery.py` e sem `tasks.py` |
| WebSocket / Channels | ADR-031 | sem `CHANNEL_LAYERS` no settings |
| Frontend React + Vite | ADR-030 | `frontend/` inexiste |
| `GET /health` | DEPLOY_PIPELINE.md | ausente em `config/urls.py` |
| Middleware X-Flow-ID end-to-end | ADR-013 | nenhuma implementação de middleware |
| Logging JSON estruturado | ADR-013 | nenhuma config de structlog |
| Dockerfile + deploy assets | DEPLOY_PIPELINE.md | ausência confirmada |

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
