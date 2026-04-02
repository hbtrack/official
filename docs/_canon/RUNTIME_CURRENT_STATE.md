---
doc_type: canon
version: "2.0.0"
last_reviewed: "auto-generated"
status: active
state_semantics: current-state
generator: "scripts/generate/docs/gen_runtime_current_state.py"
manual_edits: forbidden
---

# Runtime Atual — HB Track

> **Gerado automaticamente** a partir do estado real do workspace.
> **Não editar manualmente**. Atualize o sistema real e rode `python3 scripts/generate/docs/gen_runtime_current_state.py --write`.

## 0. Objetivo e limite de autoridade

Este documento registra apenas **fatos materializados no repositório atual**.
Ele não promove target-state, não substitui ADRs e não inventa roadmap.

Fontes executáveis observadas por este gerador:

- `src/`
- `config/`
- `infra/`
- `frontend/`
- `contracts/`
- `tests/`
- `docs/_canon/MODULE_REGISTRY.yaml`

## 1. Snapshot Executivo

| Item | Estado atual | Evidência |
|------|--------------|-----------|
| Backend Django/Ninja | materializado | `config/settings.py`, `config/urls.py`, `manage.py` |
| Routers HTTP montados | `17` routers | `config/urls.py` |
| Módulos backend canônicos | `17/17` materializados | `src/<module>/api.py`, `migrations/`, `tests/` |
| PostgreSQL dev | materializado (`postgres:12`) | `infra/docker-compose.yml` |
| Redis dev | materializado | `infra/docker-compose.yml` |
| Celery runtime | materializado (8 `tasks.py`) | `config/celery.py`, `src/*/tasks.py` |
| Channels/WebSocket config | materializado (1 `consumers.py`) | `config/settings.py`, `src/*/consumers.py` |
| Endpoint `GET /health` | materializado | `config/urls.py` |
| Frontend | materializado | `frontend/`, `frontend/package.json`, `frontend/src/` |
| Deploy assets | materializado | `Dockerfile`, `infra/docker-compose.prod.yml`, `infra/nginx/nginx.conf` |

## 2. Backend e Runtime

| Item | Estado | Evidência |
|------|--------|-----------|
| `DATABASES` em Django settings | configurado | `config/settings.py` |
| `CHANNEL_LAYERS` | configurado | `config/settings.py` |
| Celery app | configurado | `config/celery.py` |
| Módulos com `tasks.py` | `8` | `src/*/tasks.py` |
| Módulos com `consumers.py` | `1` | `src/*/consumers.py` |
| Health check HTTP | presente | `config/urls.py` |

## 3. Módulos Canônicos

| Módulo | Status no registry | API | Migrations | Tests |
|--------|--------------------|-----|------------|-------|
| `ai_ingestion` | `implemented` | ✓ | ✓ | ✓ |
| `analytics` | `implemented` | ✓ | ✓ | ✓ |
| `audit` | `implemented` | ✓ | ✓ | ✓ |
| `competitions` | `implemented` | ✓ | ✓ | ✓ |
| `exercises` | `implemented` | ✓ | ✓ | ✓ |
| `identity_access` | `implemented` | ✓ | ✓ | ✓ |
| `matches` | `implemented` | ✓ | ✓ | ✓ |
| `medical` | `implemented` | ✓ | ✓ | ✓ |
| `notifications` | `implemented` | ✓ | ✓ | ✓ |
| `reports` | `implemented` | ✓ | ✓ | ✓ |
| `scout` | `implemented` | ✓ | ✓ | ✓ |
| `seasons` | `implemented` | ✓ | ✓ | ✓ |
| `teams` | `implemented` | ✓ | ✓ | ✓ |
| `training` | `implemented` | ✓ | ✓ | ✓ |
| `users` | `implemented` | ✓ | ✓ | ✓ |
| `video` | `implemented` | ✓ | ✓ | ✓ |
| `wellness` | `implemented` | ✓ | ✓ | ✓ |

## 4. Contratos e Superfícies

| Artefato | Cobertura atual | Evidência |
|----------|-----------------|-----------|
| OpenAPI paths por módulo | `17/17` | `contracts/openapi/paths/` |
| JSON Schema por módulo de domínio | `17/17` | `contracts/schemas/<module>/` |
| JSON Schema compartilhado | `1` diretórios | `contracts/schemas/shared/` |
| AsyncAPI channels | `61` arquivos | `contracts/asyncapi/channels/` |
| Arazzo workflows | `24` arquivos | `contracts/workflows/` |
| State model docs | `2` arquivos | `docs/hbtrack/modulos/*/STATE_MODEL_*.md` |
| UI contract docs | `1` arquivos | `docs/hbtrack/modulos/*/UI_CONTRACT_*.md` |

## 5. Frontend e Deploy

| Item | Estado | Evidência |
|------|--------|-----------|
| Diretório `frontend/` | presente | `frontend/` |
| `frontend/package.json` | presente | `frontend/package.json` |
| `frontend/src/` | presente | `frontend/src/` |
| Tipos `schema.d.ts` | `4` arquivo(s) | `frontend/**/schema.d.ts` |
| `Dockerfile` raiz | presente | `Dockerfile` |
| `infra/docker-compose.prod.yml` | presente | `infra/docker-compose.prod.yml` |
| `infra/nginx/nginx.conf` | presente | `infra/nginx/nginx.conf` |
| Rollback script | presente | `infra/scripts/rollback.sh` |

## 6. Testes e Governança

| Item | Estado | Evidência |
|------|--------|-----------|
| Diretórios `tests/unit` por módulo | `17/17` | `src/*/tests/unit/` |
| Diretórios `tests/integration` por módulo | `17/17` | `src/*/tests/integration/` |
| Arquivos em `tests/pipeline_gates/` | `80` | `tests/pipeline_gates/` |
| Gates no `GATES_REGISTRY.yaml` | `68` (59 bloqueantes, 1 skip-allowed) | `docs/_canon/gates/GATES_REGISTRY.yaml` |
| Validador de drift arquitetural | presente | `scripts/audit/check_architecture_docs.py` |
| Validador principal de contratos | presente | `scripts/contracts/validate/validate_contracts.py` |

## 7. Regras de uso

- Este documento é derivado; qualquer edição manual deve ser tratada como drift.
- Divergência entre este arquivo e o workspace atual deve falhar via `gen_runtime_current_state.py --check`.
- ADRs e docs de arquitetura continuam normativos para target-state e decisões; este arquivo cobre somente estado materializado.
