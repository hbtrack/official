# Architecture Reality Deep Diff — Backend

> Auditoria técnica de repositório contract-driven.
> Data: 2026-04-23
> Escopo: arquitetura do backend — canon vs runtime real
> Regras aplicadas: AGAUDIT v1.1 — Prompt 4

---

## Resumo executivo

| Métrica | Valor |
|---|---|
| Documentos canon analisados | 4 (ARCHITECTURE.md, C4_CONTAINERS.md, CODE_ARCHITECTURE.md, RUNTIME_CURRENT_STATE.md) |
| Arquivos runtime inspecionados | 12 |
| Achados totais | 10 |
| Erros confirmados | 0 |
| Drifts prováveis (canon defasado) | 9 |
| Divergências estruturais | 1 |
| Problemas de código | 0 |
| Falsos positivos | 0 |

**Veredicto geral:** Todos os achados são drift de documentação — o código avançou além do que o canon registra. Nenhum bug de runtime foi identificado nesta análise arquitetural. A causa-raiz consolidada é uma única: `RUNTIME_CURRENT_STATE.md` (e os demais docs de canon) não foram atualizados após a implementação de Celery, Channels/WebSocket, deploy assets, FlowIDMiddleware, JSON logging, frontend e health endpoint. O risco não é técnico — é de desorientação do agente em futuras sessões que leia o canon como verdade de runtime.

---

## Achados

---

### ACHADO-AR-001

```
ACHADO-ID: ACHADO-AR-001
Categoria: Canon defasado — Celery declarado como target-state mas materializado
Módulo: shared / infra
Severidade: alta
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

- `ARCHITECTURE.md` §1: "Workers assíncronos | ausencia de config/celery.py e de src/<module>/tasks.py | workers Celery ainda nao sao runtime comprovado"
- `CODE_ARCHITECTURE.md` §4: "`config/celery.py` — nao existe"
- `C4_CONTAINERS.md` §2: Worker assíncrono — container "não materializado" — motivo: "não existe config/celery.py nem src/<module>/tasks.py"
- `RUNTIME_CURRENT_STATE.md` §1.3: "Redis usado como broker Celery | ausente | nenhuma configuração CELERY_BROKER_URL ou config/celery.py"
- `RUNTIME_CURRENT_STATE.md` §7: Worker Celery listado como target-state não materializado

**Runtime real correspondente:**

`config/celery.py` existe e está implementado:
```python
app = Celery("hbtrack")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```
Com propagação de X-Flow-ID para headers de task (`before_task_publish`) e restauração em workers (`task_prerun`).

`config/settings.py` tem:
```python
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = "django-db"
```

`INSTALLED_APPS` inclui `django_celery_results` e `django_celery_beat`.

7 módulos têm `tasks.py`: `matches`, `video`, `ai_ingestion`, `notifications`, `analytics`, `scout`, `reports`, `audit`.

**Aderente?** NÃO — o canon afirma ausência total; o runtime tem implementação completa.

**Impacto:**

O agente que lê o canon antes de qualquer sessão acredita que Celery não existe e pode:
- Propor re-implementar o que já existe
- Não considerar tasks.py ao auditar módulos que as têm
- Não saber que X-Flow-ID já propaga para workers

**Severidade:** alta (canon afirma estado falso como verdade de runtime)

**Ação:** Atualizar `RUNTIME_CURRENT_STATE.md` para mover Celery de "target-state" para "materializado", listar os 8 módulos com tasks.py, e atualizar `C4_CONTAINERS.md` para marcar o container Worker como "atual comprovado". Remover de `CODE_ARCHITECTURE.md` §4 a afirmação de que `config/celery.py` não existe.

**Bloqueia merge?** não (é drift de doc, não bug de código)

**Classificação:** drift provável — canon desatualizado em relação ao runtime

---

### ACHADO-AR-002

```
ACHADO-ID: ACHADO-AR-002
Categoria: Canon defasado — WebSocket/Channels declarado como target-state mas materializado
Módulo: notifications / shared
Severidade: alta
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

- `ARCHITECTURE.md` §1: "WebSocket | ausencia de CHANNEL_LAYERS e de configuracao Channels | WebSocket/Channels ainda nao e runtime comprovado"
- `RUNTIME_CURRENT_STATE.md` §1.3: "Redis usado por Django Channels | ausente | nenhuma configuração CHANNEL_LAYERS"
- `RUNTIME_CURRENT_STATE.md` §7: WebSocket/Channels listado como target-state não materializado
- `C4_CONTAINERS.md` §2: Endpoint WebSocket — "não materializado"

**Runtime real correspondente:**

`config/settings.py` tem:
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379/0")]},
    }
}
```

`config/asgi.py` implementa:
```python
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": _get_websocket_application(),  # AllowedHostsOriginValidator + TokenAuthMiddlewareStack
})
```

`src/notifications/routing.py`:
```python
websocket_urlpatterns = [path("ws/notifications/", NotificationConsumer.as_asgi())]
```

`src/notifications/consumers.py`: `AsyncWebsocketConsumer` implementado com grupos por `notifications.<user_id>`.

`INSTALLED_APPS` inclui `"channels"`.

**Aderente?** NÃO — o canon afirma ausência; o runtime tem implementação completa de WebSocket com autenticação.

**Impacto:** Agente pode propor recriar infraestrutura WebSocket já existente ou ignorar o consumer existente ao auditar notifications.

**Ação:** Atualizar `RUNTIME_CURRENT_STATE.md` §1.3 e §7, `C4_CONTAINERS.md` §2, `ARCHITECTURE.md` §1 e §5 para refletir que Channels está materializado.

**Bloqueia merge?** não

**Classificação:** drift provável — canon desatualizado

---

### ACHADO-AR-003

```
ACHADO-ID: ACHADO-AR-003
Categoria: Canon defasado — GET /health declarado ausente mas implementado
Módulo: config
Severidade: alta
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

- `ARCHITECTURE.md` §1: "Health endpoint | ausencia de /health em config/urls.py | deploy ponta a ponta ainda nao pode ser tratado como operacional"
- `RUNTIME_CURRENT_STATE.md` §4: "Endpoint GET /health | ausente"
- `RUNTIME_CURRENT_STATE.md` §7: "`GET /health` listado como target-state não materializado"

**Runtime real correspondente:**

`config/urls.py` implementa:
```python
def health_check(request):
    """GET /health — verifica PostgreSQL e Redis."""
    # Testa django.db.connection.ensure_connection()
    # Testa redis.from_url(redis_url).ping()
    # Retorna {"status": "ok"|"degraded", "db": ..., "redis": ..., "buildSha": ...}

urlpatterns = [
    path("health", health_check),
    path("api/", api.urls),
]
```

`Dockerfile` tem `HEALTHCHECK` interno usando `curl -f http://localhost:8000/health`.
`infra/docker-compose.staging.yml` usa o mesmo endpoint para healthcheck do container api.

**Aderente?** NÃO — o canon afirma ausência; o runtime tem endpoint funcional com checks reais de DB e Redis.

**Impacto:** Canon afirma que deploy end-to-end não é operacional por falta do `/health` — mas o endpoint existe e é usado pelo Dockerfile e pelo compose de staging.

**Ação:** Atualizar `RUNTIME_CURRENT_STATE.md` §4 e §7 para marcar `GET /health` como materializado. Remover a afirmação de ARCHITECTURE.md §1 de que está ausente.

**Bloqueia merge?** não

**Classificação:** drift provável

---

### ACHADO-AR-004

```
ACHADO-ID: ACHADO-AR-004
Categoria: Canon defasado — Dockerfile e assets de deploy declarados ausentes mas implementados
Módulo: infra
Severidade: alta
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

- `RUNTIME_CURRENT_STATE.md` §4: "Dockerfile de produção | ausente | nenhum Dockerfile na raiz ou em infra/"; "docker-compose.prod.yml | ausente"; "nginx.conf | ausente"
- `ARCHITECTURE.md` §2: Dockerfile listado como target-state

**Runtime real correspondente:**

Arquivos presentes no repo:
- `Dockerfile` (raiz) — multi-stage (builder + runtime), `python:3.12-slim`, Gunicorn + UvicornWorker, usuário não-root (`hbtrack`), `HEALTHCHECK` via curl
- `Dockerfile.frontend` — multi-stage (node:22-alpine → nginx), build React/Vite
- `infra/docker-compose.prod.yml` — compose de produção com api, frontend, celery_worker, celery_beat, postgres:16, redis:7
- `infra/docker-compose.staging.yml` — compose de staging análogo
- `infra/docker-compose.edge.yml` — proxy Nginx de borda (termina TLS, roteia prod/staging)
- `infra/nginx/` — 6 configs nginx: nginx.conf, nginx.edge.conf, nginx.production.conf, nginx.staging.conf, nginx.bootstrap.conf, nginx.edge.bootstrap.conf, nginx-spa.conf

**Aderente?** NÃO — o canon afirma ausência total; o runtime tem todos os assets de deploy implementados.

**Impacto:** Canon implica que o sistema não está apto para deploy; na realidade os assets de deploy estão presentes e configurados (multi-stage build, edge proxy, staging e produção separados).

**Ação:** Atualizar `RUNTIME_CURRENT_STATE.md` §4 com todos os arquivos de infra presentes. Atualizar `C4_CONTAINERS.md` para refletir a existência de proxy de borda e frontend container.

**Bloqueia merge?** não

**Classificação:** drift provável — múltiplos assets de infra não refletidos no canon

---

### ACHADO-AR-005

```
ACHADO-ID: ACHADO-AR-005
Categoria: Canon defasado — X-Flow-ID middleware declarado ausente mas implementado
Módulo: shared / config
Severidade: média
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

- `ARCHITECTURE.md` §5: "Middleware X-Flow-ID end-to-end (ADR-013) nao existe no runtime atual; apenas correlation_id pontual no modulo audit"
- `RUNTIME_CURRENT_STATE.md` §5: "Middleware de propagação X-Flow-ID end-to-end | ausente | nenhum middleware em config/"
- `RUNTIME_CURRENT_STATE.md` §7: "Middleware X-Flow-ID end-to-end" listado como target-state não materializado

**Runtime real correspondente:**

`src/shared/middleware.py` implementa `FlowIDMiddleware` que:
- Aceita `X-Flow-ID` do request (validando UUID v4)
- Gera novo UUID v4 se header ausente ou inválido
- Armazena no thread-local via `set_flow_id()`
- Propaga em todas as responses via header `X-Flow-ID`

`config/settings.py` MIDDLEWARE list inclui:
```python
"shared.middleware.FlowIDMiddleware",
```

`config/celery.py` propaga o flow_id para tasks:
```python
@before_task_publish.connect
def inject_flow_id_into_task_headers(headers: dict, **kwargs):
    headers.setdefault("X-Flow-ID", get_current_flow_id())
```

**Aderente?** NÃO — o canon afirma que apenas `correlation_id` pontual existe; o runtime tem FlowIDMiddleware completo ativo end-to-end incluindo propagação para Celery workers.

**Ação:** Atualizar `RUNTIME_CURRENT_STATE.md` §5 e §7 para marcar X-Flow-ID como materializado. Atualizar `ARCHITECTURE.md` §5 e §6.

**Bloqueia merge?** não

**Classificação:** drift provável

---

### ACHADO-AR-006

```
ACHADO-ID: ACHADO-AR-006
Categoria: Canon defasado — Logging JSON estruturado declarado ausente mas implementado
Módulo: shared / config
Severidade: média
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

- `ARCHITECTURE.md` §5: "Logging estruturado em JSON (ADR-013) nao esta configurado em config/settings.py"
- `RUNTIME_CURRENT_STATE.md` §5: "Logging estruturado em JSON (structlog ou equivalente) | ausente"
- `RUNTIME_CURRENT_STATE.md` §7: Logging JSON listado como target-state não materializado

**Runtime real correspondente:**

`src/shared/logging_formatters.py` implementa `FlowIDFormatter(logging.Formatter)` que emite JSON estruturado incluindo `flow_id` em cada linha.

`config/settings.py` configura:
```python
LOGGING = {
    "formatters": {
        "flow_json": {
            "()": "shared.logging_formatters.FlowIDFormatter",
        },
    },
    "handlers": {"console": {..., "formatter": "flow_json"}},
    # Em produção (não DEBUG): adiciona handler "file" com TimedRotatingFileHandler
}
```

**Aderente?** NÃO (com nuance): a implementação usa formatter customizado JSON (não `structlog`). O canon diz "structlog ou equivalente" — o runtime usa equivalente funcional. O logging JSON está materializado, não é target-state.

**Nota de precisão:** A implementação não usa `structlog` (biblioteca) mas usa Python `logging` com formatter JSON customizado. Isso atende ao ADR-013 semanticamente (logs estruturados em JSON com flow_id) mas difere da implementação de referência. Não é um erro.

**Ação:** Atualizar `RUNTIME_CURRENT_STATE.md` §5 para marcar logging JSON como materializado, com nota de que usa `FlowIDFormatter` customizado (não structlog).

**Bloqueia merge?** não

**Classificação:** drift provável

---

### ACHADO-AR-007

```
ACHADO-ID: ACHADO-AR-007
Categoria: Canon defasado — Frontend declarado ausente mas materializado
Módulo: frontend
Severidade: alta
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

- `RUNTIME_CURRENT_STATE.md` §6: "Diretório frontend/ | ausente"; "Toolchain React/Vite | ausente"; "Tipos gerados schema.d.ts | ausente"
- `C4_CONTAINERS.md` §2: Frontend web SPA — "não materializado" — motivo: "frontend/ não existe e package.json não declara toolchain de frontend real"
- `ARCHITECTURE.md` §2: Frontend listado como target-state

**Runtime real correspondente:**

`frontend/` existe com estrutura completa:
- `package.json`, `vite.config.ts`, `tailwind.config.ts`, `tsconfig.json`, `tsconfig.node.json`
- `index.html`, `src/`, `e2e/` (Playwright), `scripts/`
- `node_modules/` (dependências instaladas)
- `playwright.config.ts` (testes e2e)
- `dist/` (build compilado presente)

Stack: React + Vite + TypeScript + TailwindCSS (alinhado ao que ADR-030 aprovava).

**Aderente?** NÃO — o canon afirma que `frontend/` não existe; o diretório existe com toolchain completa, dependências instaladas e até um build `dist/` presente.

**Impacto:** Agente pode propor criar frontend que já existe. CI que checa RUNTIME_CURRENT_STATE.md pode concluir incorretamente que o frontend não está pronto.

**Ação:** Atualizar `RUNTIME_CURRENT_STATE.md` §6 com estado real do frontend. Atualizar `C4_CONTAINERS.md` §2 para mover Frontend para "containers atuais comprovados". Verificar se `schema.d.ts` está gerado (`npm run api:generate`).

**Bloqueia merge?** não

**Classificação:** drift provável

---

### ACHADO-AR-008

```
ACHADO-ID: ACHADO-AR-008
Categoria: ARCHITECTURE.md cita postgres:12 — versão incorreta
Módulo: infra
Severidade: baixa
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

`ARCHITECTURE.md` §1, tabela de eixos:
> "o ambiente dev materializado usa PostgreSQL em container local; o compose ainda esta em `postgres:12`, apesar do target-state aprovado apontar para PostgreSQL 16"

**Runtime real correspondente:**

`infra/docker-compose.yml`:
```yaml
postgres:
  image: postgres:16
```

`RUNTIME_CURRENT_STATE.md` §1.2 (corretamente): "PostgreSQL local em container | materializado | infra/docker-compose.yml — serviço postgres:16"

**Aderente?** NÃO — ARCHITECTURE.md diz `postgres:12`; o runtime usa `postgres:16`. RUNTIME_CURRENT_STATE.md está correto; ARCHITECTURE.md está defasado neste ponto específico.

**Ação:** Atualizar `ARCHITECTURE.md` §1 para remover a menção a `postgres:12`.

**Bloqueia merge?** não

**Classificação:** drift provável — referência histórica não atualizada em ARCHITECTURE.md

---

### ACHADO-AR-009

```
ACHADO-ID: ACHADO-AR-009
Categoria: Divergência estrutural — CODE_ARCHITECTURE.md assume flat files, training usa sub-pacotes
Módulo: training (e possivelmente outros)
Severidade: média
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

`CODE_ARCHITECTURE.md` §1 documenta a estrutura esperada como:
```
src/<module>/
  api.py        ← arquivo flat
  schemas.py    ← arquivo flat
```

**Runtime real correspondente:**

O módulo `training` usa:
- `src/training/api/` — diretório com sub-routers: `blocks.py`, `sessions.py`, `attendance.py`, `wellness.py`, `eligibility.py`, `execution.py`, `feedback.py`, `planning.py`, `analytics.py`, `recommendations.py`, `mappers.py`, `errors.py`, `deps.py`
- `src/training/schemas/` — diretório com: `sessions.py`, `blocks.py`, `attendance.py`, `wellness.py`

O `config/urls.py` importa `from training.api import router as training_router` — o módulo expõe um router agregado, mas a estrutura interna é de diretório, não arquivo flat.

**Aderente?** PARCIAL — o padrão de `api.py` flat provavelmente se aplica a módulos simples; `training` (com 10+ sub-recursos) evoluiu para sub-pacotes. O canon não documenta este padrão evolutivo e pode confundir o agente ao navegar em módulos complexos.

**Impacto:** Agente procurando `src/training/api.py` não o encontrará e pode concluir erroneamente que o módulo não tem API.

**Ação:** Atualizar `CODE_ARCHITECTURE.md` §1 para documentar ambos os padrões: flat (`api.py`) para módulos simples e sub-pacote (`api/`) para módulos com múltiplos sub-recursos. Listar `training` como exemplo do padrão sub-pacote.

**Bloqueia merge?** não

**Classificação:** drift provável — estrutura documentada incompleta para módulos avançados

---

### ACHADO-AR-010

```
ACHADO-ID: ACHADO-AR-010
Categoria: README desatualizado — referencia setup desalinhado com runtime
Módulo: docs
Severidade: baixa
Estado: drift provável
Camadas em conflito: documentação canônica ← runtime
```

**Elemento documentado no canon:**

`README.md` (última revisão 2026-03-11):
- Instrui: `python3 -m venv .venv` e `source .venv/bin/activate`
- Estrutura do repo lista apenas `infra/docker-compose.yml` (sem staging, prod, edge)
- Não menciona Celery, Channels, health endpoint

**Runtime real correspondente:**

- Virtualenv real está em `.venv-contract` (não `.venv`)
- `infra/` tem 4 compose files: `docker-compose.yml`, `docker-compose.staging.yml`, `docker-compose.prod.yml`, `docker-compose.edge.yml`
- Backend tem Celery, Channels, health endpoint — nenhum mencionado no README

**Aderente?** NÃO (parcial) — README está defasado em setup e estrutura

**Impacto:** Menor para runtime, maior para onboarding de novos devs/agentes.

**Ação:** Atualizar README com virtualenv correto (`.venv-contract`), listar todos os compose files, mencionar Celery e Channels como parte do stack atual.

**Bloqueia merge?** não

**Classificação:** drift provável — README desatualizado

---

## Agrupamento por causa-raiz

### CR-AR-001 — Implementação avançou sem atualização dos docs de canon de estado

Todos os 10 achados têm a mesma causa-raiz: `RUNTIME_CURRENT_STATE.md`, `ARCHITECTURE.md`, `C4_CONTAINERS.md` e `CODE_ARCHITECTURE.md` foram revisados pela última vez em 2026-03-23 mas a implementação continuou sem atualização correspondente dos docs de estado.

**Achados originados:** ACHADO-AR-001 a ACHADO-AR-010

**Módulo:** governança/docs

**Severidade consolidada:** alta (o canon é a fonte de orientação do agente — se descreve estado falso, o agente toma decisões erradas)

**Prioridade:** 1

**Ação consolidada:**
1. Atualizar `RUNTIME_CURRENT_STATE.md` com todos os items movidos de "ausente/target-state" para "materializado" (Celery, Channels, health endpoint, Dockerfile, docker-compose.prod.yml, nginx configs, FlowIDMiddleware, logging JSON, frontend)
2. Atualizar `ARCHITECTURE.md` §1 (postgres:12→16), §5 (deltas abertos já fechados)
3. Atualizar `C4_CONTAINERS.md` §1 e §2
4. Atualizar `CODE_ARCHITECTURE.md` §1 e §4 (estrutura sub-pacote training, celery.py existe)
5. Atualizar `README.md` (virtualenv, compose files, stack atual)

---

## O que o canon está CORRETO sobre

Para clareza e evitar falsos positivos, os seguintes itens do canon estão alinhados com o runtime:

| Item | Canon | Runtime | Aderente? |
|---|---|---|---|
| Django 5.x + Django Ninja 1.x | materializado | `config/settings.py`, `config/urls.py` | ✓ SIM |
| PostgreSQL via Django ORM | materializado | `settings.py` DATABASES | ✓ SIM |
| Python 3.12 | materializado | `Dockerfile` FROM python:3.12-slim | ✓ SIM |
| 17 módulos no INSTALLED_APPS | materializado | `settings.py` lista 17 módulos | ✓ SIM |
| Arquitetura em 4 camadas (Interface→Application→Domain→Infrastructure) | canon | existente em training/* | ✓ SIM |
| `frontend/` ausente no repositório (segundo RUNTIME_CURRENT_STATE data 2026-03-23) | provavelmente correto à época | hoje existe | delta temporal |
| `secret_key` fail-fast em DEBUG=False | implementado | `settings.py` l.235-255 | ✓ SIM |
| CORS configuração segura (DEBUG-only allow-all) | implementado | `settings.py` l.155 | ✓ SIM |
| Sem django.contrib.admin em INSTALLED_APPS | correto implicitamente | não está listado | ✓ SIM |
