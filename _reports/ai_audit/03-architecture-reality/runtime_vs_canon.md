# Runtime vs Canon — Tabela de Aderência

> Auditoria técnica de repositório contract-driven.
> Data: 2026-04-23
> Escopo: comparação elemento a elemento entre canon e runtime
> Regras aplicadas: AGAUDIT v1.1 — Prompt 4

---

## Como ler esta tabela

- **Aderente: SIM** — canon descreve corretamente o runtime atual
- **Aderente: NÃO** — canon descreve estado diferente do runtime (geralmente canon defasado)
- **Aderente: PARCIAL** — canon descreve parte da realidade, mas com lacunas
- **Fonte do canon** — qual documento faz a afirmação
- **Evidência runtime** — arquivo ou trecho que comprova o estado real

---

## 1. Backend HTTP

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| Django 5.x + Django Ninja 1.x | RUNTIME_CURRENT_STATE §1.1 | materializado | existe | `config/settings.py`, `config/urls.py` | ✓ SIM | — |
| NinjaAPI com 17 routers | RUNTIME_CURRENT_STATE §1.1 | materializado | existe | `config/urls.py:86-103` | ✓ SIM | — |
| Python 3.12 | RUNTIME_CURRENT_STATE §1.1 | materializado | existe | `Dockerfile` FROM python:3.12-slim | ✓ SIM | — |
| `manage.py` na raiz | RUNTIME_CURRENT_STATE §1.1 | materializado | existe | arquivo presente | ✓ SIM | — |
| `ASGI_APPLICATION` configurado | CODE_ARCHITECTURE | implícito | existe | `settings.py:86` ASGI_APPLICATION | ✓ SIM | — |

---

## 2. Banco de dados

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| PostgreSQL via Django ORM | RUNTIME_CURRENT_STATE §1.2 | materializado | existe | `settings.py` DATABASES | ✓ SIM | — |
| PostgreSQL local em container | RUNTIME_CURRENT_STATE §1.2 | materializado | postgres:16 | `infra/docker-compose.yml` | ✓ SIM | — |
| Compose usa postgres:12 | ARCHITECTURE.md §1 | afirmado como corrente | FALSO — usa postgres:16 | `infra/docker-compose.yml:5` | ✗ NÃO | ACHADO-AR-008 |
| Migrations em todos os 17 módulos | RUNTIME_CURRENT_STATE §1.2 | materializado | verdadeiro (+ 1 pendente em training) | `src/*/migrations/` | ✓ SIM (com ressalva ACHADO-007) | — |

---

## 3. Redis e Celery

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| Redis local em container | RUNTIME_CURRENT_STATE §1.3 | provisionado | redis:7-alpine | `infra/docker-compose.yml:18` | ✓ SIM | — |
| `config/celery.py` | RUNTIME_CURRENT_STATE §1.3 e §7 | AUSENTE (target-state) | EXISTE | `config/celery.py` — Celery 5.x completo | ✗ NÃO | ACHADO-AR-001 |
| CELERY_BROKER_URL | RUNTIME_CURRENT_STATE §1.3 | AUSENTE | configurado | `settings.py:134` | ✗ NÃO | ACHADO-AR-001 |
| `src/<module>/tasks.py` | CODE_ARCHITECTURE §4 | AUSENTE | 8 módulos têm | matches, video, ai_ingestion, notifications, analytics, scout, reports, audit | ✗ NÃO | ACHADO-AR-001 |
| django_celery_results | RUNTIME_CURRENT_STATE | não mencionado | instalado | `settings.py:50` INSTALLED_APPS | ✗ PARCIAL | ACHADO-AR-001 |

---

## 4. WebSocket / Channels

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| `CHANNEL_LAYERS` | RUNTIME_CURRENT_STATE §1.3 e §7 | AUSENTE | CONFIGURADO | `settings.py:144-151` channels_redis | ✗ NÃO | ACHADO-AR-002 |
| `config/asgi.py` com Channels | ARCHITECTURE.md §1 | ausente | IMPLEMENTADO | `config/asgi.py` ProtocolTypeRouter | ✗ NÃO | ACHADO-AR-002 |
| `notifications/routing.py` | RUNTIME_CURRENT_STATE | não mencionado | EXISTE | ws/notifications/ path | ✗ NÃO | ACHADO-AR-002 |
| `notifications/consumers.py` | RUNTIME_CURRENT_STATE | não mencionado | EXISTE | AsyncWebsocketConsumer | ✗ NÃO | ACHADO-AR-002 |
| "channels" em INSTALLED_APPS | não mencionado | — | INSTALADO | `settings.py:47` | ✗ NÃO | ACHADO-AR-002 |

---

## 5. Health endpoint

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| `GET /health` | RUNTIME_CURRENT_STATE §4 e §7 | AUSENTE | IMPLEMENTADO | `config/urls.py:105-141` | ✗ NÃO | ACHADO-AR-003 |
| Check PostgreSQL em /health | RUNTIME_CURRENT_STATE | não mencionado | IMPLEMENTADO | `urls.py:116-121` | ✗ NÃO | ACHADO-AR-003 |
| Check Redis em /health | RUNTIME_CURRENT_STATE | não mencionado | IMPLEMENTADO | `urls.py:123-129` | ✗ NÃO | ACHADO-AR-003 |

---

## 6. Deploy assets (Dockerfile, compose, nginx)

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| `Dockerfile` | RUNTIME_CURRENT_STATE §4 | AUSENTE | EXISTE | `Dockerfile` na raiz — multi-stage | ✗ NÃO | ACHADO-AR-004 |
| `Dockerfile.frontend` | RUNTIME_CURRENT_STATE | não mencionado | EXISTE | `Dockerfile.frontend` na raiz | ✗ NÃO | ACHADO-AR-004 |
| `docker-compose.prod.yml` | RUNTIME_CURRENT_STATE §4 | AUSENTE | EXISTE | `infra/docker-compose.prod.yml` | ✗ NÃO | ACHADO-AR-004 |
| `docker-compose.staging.yml` | RUNTIME_CURRENT_STATE | não mencionado | EXISTE | `infra/docker-compose.staging.yml` | ✗ NÃO | ACHADO-AR-004 |
| `docker-compose.edge.yml` | RUNTIME_CURRENT_STATE | não mencionado | EXISTE | `infra/docker-compose.edge.yml` — proxy TLS | ✗ NÃO | ACHADO-AR-004 |
| `nginx.conf` | RUNTIME_CURRENT_STATE §4 | AUSENTE | EXISTE (6 configs) | `infra/nginx/*.conf` | ✗ NÃO | ACHADO-AR-004 |
| Usuário não-root no container | RUNTIME_CURRENT_STATE | não mencionado | IMPLEMENTADO | `Dockerfile:44` useradd hbtrack | ✗ NÃO | ACHADO-AR-004 |
| Gunicorn + UvicornWorker | RUNTIME_CURRENT_STATE | não mencionado | IMPLEMENTADO | `Dockerfile:76` ENTRYPOINT | ✗ NÃO | ACHADO-AR-004 |
| Celery worker no compose prod/staging | RUNTIME_CURRENT_STATE | não mencionado | IMPLEMENTADO | `docker-compose.staging.yml:89` | ✗ NÃO | ACHADO-AR-001 |

---

## 7. Observabilidade (X-Flow-ID, Logging)

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| X-Flow-ID middleware | RUNTIME_CURRENT_STATE §5 e §7 | AUSENTE | IMPLEMENTADO | `shared/middleware.py` FlowIDMiddleware | ✗ NÃO | ACHADO-AR-005 |
| FlowIDMiddleware no MIDDLEWARE | RUNTIME_CURRENT_STATE | não mencionado | ATIVO | `settings.py:82` lista MIDDLEWARE | ✗ NÃO | ACHADO-AR-005 |
| X-Flow-ID propagado para Celery | RUNTIME_CURRENT_STATE | não mencionado | IMPLEMENTADO | `config/celery.py:18-23` | ✗ NÃO | ACHADO-AR-005 |
| Logging JSON estruturado | RUNTIME_CURRENT_STATE §5 e §7 | AUSENTE | IMPLEMENTADO | `shared/logging_formatters.py` FlowIDFormatter | ✗ NÃO | ACHADO-AR-006 |
| LOGGING config em settings.py | RUNTIME_CURRENT_STATE | não mencionado | CONFIGURADO | `settings.py:203-229` | ✗ NÃO | ACHADO-AR-006 |
| correlation_id no módulo audit | RUNTIME_CURRENT_STATE §5 | implementado (pontual) | existe | `src/audit/` | ✓ SIM | — |

---

## 8. Frontend

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| `frontend/` diretório | RUNTIME_CURRENT_STATE §6 | AUSENTE | EXISTE | `frontend/` com React/Vite/Tailwind | ✗ NÃO | ACHADO-AR-007 |
| Toolchain React/Vite | RUNTIME_CURRENT_STATE §6 | AUSENTE | INSTALADA | `frontend/package.json`, `vite.config.ts` | ✗ NÃO | ACHADO-AR-007 |
| TypeScript | RUNTIME_CURRENT_STATE §6 | AUSENTE | INSTALADO | `frontend/tsconfig.json` | ✗ NÃO | ACHADO-AR-007 |
| TailwindCSS | RUNTIME_CURRENT_STATE §6 | AUSENTE | INSTALADO | `frontend/tailwind.config.ts` | ✗ NÃO | ACHADO-AR-007 |
| Playwright (e2e) | RUNTIME_CURRENT_STATE | não mencionado | INSTALADO | `frontend/playwright.config.ts`, `frontend/e2e/` | ✗ NÃO | ACHADO-AR-007 |
| dist/ (build compilado) | RUNTIME_CURRENT_STATE | não mencionado | EXISTE | `frontend/dist/` | ✗ NÃO | ACHADO-AR-007 |

---

## 9. Estrutura de código

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| `src/<module>/api.py` (flat) | CODE_ARCHITECTURE §1 | padrão universal | PARCIAL — training usa api/ | `src/training/api/` com 13 arquivos | ✗ PARCIAL | ACHADO-AR-009 |
| `src/<module>/schemas.py` (flat) | CODE_ARCHITECTURE §1 | padrão universal | PARCIAL — training usa schemas/ | `src/training/schemas/` com 4 arquivos | ✗ PARCIAL | ACHADO-AR-009 |
| `src/<module>/domain/` | CODE_ARCHITECTURE §1 | materializado | existe em todos módulos | `src/*/domain/` | ✓ SIM | — |
| `src/<module>/application/` | CODE_ARCHITECTURE §1 | materializado | existe | `src/*/application/` | ✓ SIM | — |
| `src/<module>/infrastructure/` | CODE_ARCHITECTURE §1 | materializado | existe | `src/*/infrastructure/` | ✓ SIM | — |
| Testes em `src/<module>/tests/` | CODE_ARCHITECTURE §5 | padrão | existe | `src/*/tests/unit/` e `integration/` | ✓ SIM | — |

---

## 10. Segurança (settings)

| Elemento documentado | Fonte do canon | Estado no canon | Runtime real | Evidência runtime | Aderente? | Achado |
|---|---|---|---|---|---|---|
| Fail-fast SECRET_KEY em DEBUG=False | não mencionado explicitamente | — | IMPLEMENTADO | `settings.py:235-244` | ✓ SIM | — |
| CORS bloqueado em DEBUG=False | SECURITY_RULES | esperado | IMPLEMENTADO | `settings.py:155,251-254` | ✓ SIM | — |
| SecurityHeadersMiddleware | SECURITY_RULES | esperado | IMPLEMENTADO | `settings.py:79`, `shared/middleware.py` | ✓ SIM | — |
| Sem django.contrib.admin | implícito | — | CORRETO | `settings.py` INSTALLED_APPS sem admin | ✓ SIM | — |
| JWTClaimsMiddleware | não mencionado | — | IMPLEMENTADO | `settings.py:82` | ✗ PARCIAL | — |

---

## Sumário de aderência

| Categoria | Total itens verificados | Aderentes (SIM) | Não aderentes (NÃO/PARCIAL) |
|---|---|---|---|
| Backend HTTP | 5 | 5 | 0 |
| Banco de dados | 4 | 3 | 1 (postgres:12 claim) |
| Redis e Celery | 5 | 1 | 4 |
| WebSocket / Channels | 5 | 0 | 5 |
| Health endpoint | 3 | 0 | 3 |
| Deploy assets | 9 | 0 | 9 |
| Observabilidade | 6 | 1 | 5 |
| Frontend | 6 | 0 | 6 |
| Estrutura de código | 7 | 5 | 2 |
| Segurança | 5 | 4 | 1 (parcial) |
| **TOTAL** | **55** | **19 (35%)** | **36 (65%)** |

---

## Classificação dos gaps

**Todos os gaps têm a mesma natureza:** o canon documenta estado da implementação em ~2026-03-23; a implementação avançou significativamente após essa data sem atualização correspondente dos docs de estado. **Nenhum gap representa bug de código ou divergência de regras de negócio.**

| Gap | Achado | Tipo | Prioridade |
|---|---|---|---|
| Celery/tasks.py declarados ausentes | ACHADO-AR-001 | drift (doc desatualizado) | alta |
| Channels/WebSocket declarado ausente | ACHADO-AR-002 | drift (doc desatualizado) | alta |
| GET /health declarado ausente | ACHADO-AR-003 | drift (doc desatualizado) | alta |
| Dockerfile/compose/nginx declarados ausentes | ACHADO-AR-004 | drift (doc desatualizado) | alta |
| X-Flow-ID middleware declarado ausente | ACHADO-AR-005 | drift (doc desatualizado) | média |
| Logging JSON declarado ausente | ACHADO-AR-006 | drift (doc desatualizado) | média |
| Frontend declarado ausente | ACHADO-AR-007 | drift (doc desatualizado) | alta |
| postgres:12 em ARCHITECTURE.md | ACHADO-AR-008 | drift (versão errada no doc) | baixa |
| flat api.py vs sub-pacote api/ | ACHADO-AR-009 | drift (estrutura incompleta) | média |
| README setup desatualizado | ACHADO-AR-010 | drift (doc desatualizado) | baixa |

---

## Ação recomendada (única sessão)

Uma sessão de atualização de `RUNTIME_CURRENT_STATE.md` elimina 8 dos 10 achados em cascata. O documento tem `state_semantics: current-state` e é o ponto de entrada do agente para decisões de runtime — mantê-lo defasado é o risco maior desta análise.

```
Prioridade 1: atualizar RUNTIME_CURRENT_STATE.md
Prioridade 2: atualizar ARCHITECTURE.md §1, §5
Prioridade 3: atualizar C4_CONTAINERS.md §1, §2
Prioridade 4: atualizar CODE_ARCHITECTURE.md §1, §4
Prioridade 5: atualizar README.md
```
