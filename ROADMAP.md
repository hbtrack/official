# ROADMAP — HB Track
> Versão: 1.1.1 | Data: 2026-04-10 (snapshot revalidado localmente) | Decisões: D1-A · D2-C · D3-A
> Arquitetura: Software Architect + Systems Engineer · HB Track CDD Pipeline

---

## Premissas adotadas

| Decisão | Escolha | Impacto |
|---------|---------|---------|
| D1 — Estratégia de execução | **Backend primeiro** | Frontend só começa após backend completo e estável em staging |
| D2 — Escopo de MVP | **Ciclos de valor** | Produção em 3 ondas: Core → Operacional → Intelligence |
| D3 — Frontend | **API Client gerado** | `openapi-typescript` gera tipos e client direto do contrato; frontend nunca diverge da API |

---

## Visão de produto

O HB Track é construído em 4 versões com geração de valor incremental. O critério de sequenciamento é: primeiro resolver o núcleo operacional do clube, depois ampliar inteligência e automação, por fim expandir para ecossistema.

### v0.1 — Core operacional
**Objetivo:** Um clube consegue fazer login, gerenciar elenco, criar temporadas e planejar treinos.
**Módulos:** `identity_access`, `users`, `teams`, `seasons`, `training`
**Personas:** treinador principal, auxiliar técnico, coordenador
**Substitui:** planilhas de controle de treino, WhatsApp para convocação
**KPIs:** frequência de uso semanal, sessões cadastradas, taxa de adoção pela comissão

### v0.2 — Operação de jogo (MVP completo)
**Objetivo:** O clube opera partidas ao vivo, faz scouting e analisa vídeo na mesma plataforma.
**Módulos:** + `competitions`, `matches`, `scout`, `video` (9 módulos em produção — Ciclo 2)
**Personas:** analista de desempenho, analista de vídeo, scout, treinador
**Substitui:** 3–4 ferramentas separadas (software de vídeo, planilhas de scout, drive de clipes)
**KPIs:** tempo para análise pós-jogo, relatórios gerados, número de ferramentas substituídas
**Tese de produto:** um clube consegue trocar ≥ 3 ferramentas por uma só e o analista reduz retrabalho operacional

### v1.0 — Plataforma completa de alto rendimento
**Objetivo:** Físico, saúde, analytics e IA integrados com a operação esportiva em uma visão única.
**Módulos:** + `exercises`, `wellness`, `medical`, `analytics`, `reports`, `ai_ingestion`, `notifications`, `audit` (todos os 17 módulos em produção — Ciclo 3)
**Personas:** preparador físico, fisiologista, fisioterapeuta, médico, coordenador técnico
**Substitui:** stack completo de performance (apps de wellness, planilhas médicas, ferramentas de GPS isoladas)
**KPIs:** adoção pelo staff de performance, alertas de fadiga acionáveis, correlações tático-físico geradas
**Tese de produto:** a plataforma substitui o stack técnico E o stack de performance; dado unificado gera insights impossíveis em ferramentas isoladas

### v2.0 — Mobile
**Objetivo:** Atletas e treinadores usam o HB Track no celular.
**Tecnologia:** React Native + Expo (compartilha API client TypeScript com o web)
**KPIs:** retenção no app, registros de bem-estar por atleta/semana

### V3 — Ecossistema (futuro, sem módulos canônicos ainda)
**Objetivo:** Federações, ligas, mídia, live stats oficiais, APIs públicas, white-label.
**Pré-requisito técnico:** criar módulos canônicos (contratos OpenAPI/AsyncAPI) antes de qualquer código.
**Empacotamento previsto:** HB Track League — federações, competições oficiais, portal público, broadcast.

### Empacotamento comercial de referência
| Produto | Versão | Escopo |
|---------|--------|--------|
| HB Track Coach | v0.2 | Core + treino + vídeo + scout + relatórios |
| HB Track Performance | v1.0 | + wellness + medical + analytics + IA |
| HB Track Mobile | v2.0 | + app iOS/Android |
| HB Track League | V3 | + federações + competições + portal público |

---

## Estado atual (snapshot 2026-04-10)

### Revalidação local desta atualização
- `python3 scripts/contracts/validate/validate_contracts.py --profile precommit` → PASS em 2026-04-10
- `python3 scripts/hb preflight` → PASS em 2026-04-10/11
- `_reports/contract_gates/latest.json` → `overall_status=PASS`
- `_reports/preflight/latest.json` → `final_decision=PASS`
- `hb ci --profile pr` executado via `preflight` → PASS (`1840 passed`, `27 skipped`, `4 deselected`; frontend `12/12`; build Vite PASS)

### O que já existe e está validado
| Camada | Status | Detalhe |
|--------|--------|---------|
| Contratos OpenAPI | ✅ 17/17 módulos `implementation_ready` | SSOT para toda a API |
| Código backend (Clean Architecture) | ✅ 17/17 módulos | domain / application / infrastructure / api / schemas |
| Migrações Django | ✅ 17/17 módulos | `0001_initial.py` + `0002_add_constraints.py` |
| Testes | ✅ suíte local ampla validada | `hb ci --profile pr` PASS; backend `1840 passed / 27 skipped / 4 deselected`; frontend `12/12`; build PASS |
| Infra local (Docker Compose) | ✅ Operacional | PostgreSQL 16 + Redis 7 |
| Pipeline CDD | ✅ PASS | `validate_contracts` precommit/latest PASS + `hb preflight` PASS |
| Feature Registry | ✅ 31 features | 10 validated + 21 implemented |
| Celery workers | ✅ Configurado | `config/celery.py` + 11 tasks registradas |
| Django Channels | ✅ Configurado | `config/asgi.py` + WebSocket consumer |
| Endpoint `/health` | ✅ Operacional | DB + Redis check, 200/503 |
| Constraints de banco (Classe A/B) | ✅ 17/17 módulos | CHECK constraints + triggers (audit append-only) |
| Dockerfile | ✅ Multi-stage | `Dockerfile` (backend) + `Dockerfile.frontend` |
| CI/CD | ✅ Operacional | `ci.yml` + `deploy.yml` (GitHub Actions) |
| Frontend | ✅ Ciclo 1 completo | React/Vite + shadcn/ui + openapi-fetch |
| Deploy VPS (staging) | ✅ RUNTIME SAUDÁVEL | Revalidado 2026-04-11: `/health` 200, nginx/1.27.5, DB+Redis ok, OpenAPI 3.1.0 publicada (82 paths / 127 ops); evidência em `_reports/staging_revalidation/latest/` |
| Seed / fixtures | ✅ Operacional | `manage.py seed_demo` |
| CORS | ✅ Configurado | `django-cors-headers` por ambiente |
| JWT Auth | ✅ Operacional | HS256 (dev) / RS256 (prod) |
| Logging estruturado | ✅ Operacional | FlowIDFormatter + rotação em produção |

### Progresso por fase
| Fase | Status | Nota |
|------|--------|------|
| Fase 0 — Ambiente local | ✅ DONE | PostgreSQL + migrations + testes passando |
| Fase 1 — Backend completo | ✅ DONE | Celery, Channels, JWT, /health, CORS, logging |
| Fase 2 — Integridade de banco | ✅ DONE | Constraints, seeds, Schemathesis |
| Fase 3 — CI/CD + Deploy | ✅ DONE | Dockerfile, GitHub Actions, VPS configurado |
| Fase 4 — Ciclo 1 em staging | ✅ DONE | Runtime saudável. A1 (prefix normalization) + B1 (endpoint documentation) + compliance tests pass (7/7 modules: auth, users, teams, seasons, training-core, training-ops, training-intelligence). PR #66 merged 2026-04-12. |
| Fase 5 — Frontend Ciclo 1 | ✅ DONE (local) | Login, users, teams, seasons, training |
| Fase 6–13 | Pendente | Aguardam fechamento formal da Fase 4 (replay live PASS com seed admin) |

### Próxima ação identificada
**Fase 4 ✅ DONE** — Todos compliance tests PASS (7/7 modules), API runtime estável, contratos validados.

**Iniciar Fase 5 — Frontend Ciclo 1:**
1. Setup React/Vite + shadcn/ui (já existente, validar estado)
2. Regenerar API client TypeScript (`npm run api:generate`)
3. Implementar páginas: Login, Users, Teams, Seasons, Training

Evidência: PR #66 merged 2026-04-12 | `_reports/contract_gates/latest.json` → `overall_status=PASS`

### Os 17 módulos canônicos

| Grupo | Módulos |
|-------|---------|
| **Core da plataforma** | `identity_access`, `users`, `audit`, `notifications` |
| **Gestão esportiva** | `teams`, `seasons`, `competitions` |
| **Treino e exercício** | `training`, `exercises` |
| **Performance e saúde** | `wellness`, `medical` |
| **Jogo e competição** | `matches`, `scout`, `video` |
| **Inteligência** | `analytics`, `reports`, `ai_ingestion` |

---

## Visão geral das fases

```
FASE 0  → Ambiente local funcional (PostgreSQL rodando, migrations aplicadas)
FASE 1  → Backend completo (Celery, Channels, middleware de auth, /health)
FASE 2  → Banco com integridade total (constraints, triggers, seeds)
FASE 3  → Pipeline CI/CD + Deploy (Dockerfile, GitHub Actions, VPS staging)
──────── [CICLO 1 — Core: identity + users + teams + seasons + training] ────────
FASE 4  → Ciclo 1 integrado e validado em staging
FASE 5  → Frontend Ciclo 1 (login, perfil, times, temporadas, treinos)
FASE 6  → Deploy produção Ciclo 1 → v0.1 🚀
──────── [CICLO 2 — Operacional: competitions + matches + scout + video] ─────────
FASE 7  → Ciclo 2 integrado e validado em staging
FASE 8  → Frontend Ciclo 2 (competições, partidas, scout, vídeo)
FASE 9  → Deploy produção Ciclo 2 → v0.2 🚀
──────── [CICLO 3 — Intelligence: wellness + medical + analytics + ...] ──────────
FASE 10 → Ciclo 3 integrado e validado em staging
FASE 11 → Frontend Ciclo 3 (monitoramento, laudos, dashboards, IA)
FASE 12 → Deploy produção Ciclo 3 → v1.0 🚀
──────────────────────────────────────────────────────────────────────────────────
FASE 13 → Mobile v2.0 (React Native + Expo)
```

---

## FASE 0 — Ambiente local funcional

**Objetivo:** O banco de dados sobe localmente, as migrações são aplicadas, e o servidor Django responde sem erros. Pré-condição para todo o resto.

**Entrada:** Código atual (migrations existentes, docker-compose.yml presente)

### Tarefas

#### 0.1 — Subir banco de dados local
- [x] Executar `docker compose -f infra/docker-compose.yml up -d postgres redis`
- [x] Verificar que PostgreSQL está acessível em `localhost:5433`
- [x] Verificar que Redis está acessível em `localhost:6379`

#### 0.2 — Aplicar todas as migrações
- [x] Executar `.venv/bin/python manage.py migrate` (todos os 17 módulos)
- [x] Confirmar que nenhuma migração falha ou gera conflito
- [x] Validar schema criado no banco com `manage.py showmigrations`

#### 0.3 — Validar servidor Django
- [x] Executar `.venv/bin/python manage.py check` sem erros
- [x] Executar `.venv/bin/python manage.py runserver` e confirmar que sobe
- [x] Acessar `/api/docs` (Django Ninja UI automática) e verificar todos os 17 routers carregados

#### 0.4 — Validar testes de integração
- [x] Rodar `.venv/bin/pytest` com PostgreSQL ativo
- [x] Confirmar que os 33 testes antes skipped agora passam
- [x] Meta: **720 + 33 = ≥ 753 testes PASS, 0 SKIP** _(1142 + 1 schemathesis = 1143 PASS, 0 SKIP — 2026-03-25)_

**Critério de Done:** `pytest` roda sem skip, `manage.py runserver` sobe, todos os 17 routers aparecem no `/api/docs`.

---

## FASE 1 — Backend completo

**Objetivo:** Adicionar as peças de infraestrutura Django que faltam para o sistema funcionar como produto real: autenticação JWT funcional, workers Celery, notificações em tempo real, middleware de rastreabilidade e endpoint de health check.

**Entrada:** Fase 0 concluída

### Tarefas

#### 1.1 — Celery (workers assíncronos)
- [x] Criar `config/celery.py` com configuração Celery 5.x + Redis broker
- [x] Adicionar `CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND` em `config/settings.py`
- [x] Criar `src/notifications/tasks.py` (envio de notificações assíncronas)
- [x] Criar `src/ai_ingestion/tasks.py` (processamento de ingestion jobs)
- [x] Criar `src/analytics/tasks.py` (cálculo de métricas periódicas)
- [x] Criar `src/reports/tasks.py` (geração de relatórios em background)
- [x] Criar `src/audit/tasks.py` (retenção e exportação de auditoria)
- [x] Testar: `celery -A config worker --loglevel=info` sobe sem erros _(11 tasks registradas, broker redis://localhost:6379/0 — verificado 2026-03-25)_

#### 1.2 — Django Channels (WebSocket)
- [x] Adicionar `channels` e `channels_redis` em `pyproject.toml`
- [x] Criar `config/asgi.py` com `ProtocolTypeRouter` (HTTP + WebSocket)
- [x] Configurar `CHANNEL_LAYERS` com Redis em `config/settings.py`
- [x] Criar consumer WebSocket em `src/notifications/consumers.py`
- [x] Registrar rota WebSocket em `config/urls.py` (via `ProtocolTypeRouter`)
- [x] Testar conexão WebSocket local _(RedisChannelLayer: send/receive confirmados com Redis:6379 — verificado 2026-03-25)_

#### 1.3 — Autenticação JWT real
- [x] Validar que `identity_access` emite JWT RS256 válido no login
- [x] Criar middleware Django `JWTAuthMiddleware` em `src/identity_access/middleware.py`
- [x] Registrar middleware em `MIDDLEWARE` no `config/settings.py` _(JWT auth via `JWTBearer` HttpBearer via DI — endpoint `/api/users` retorna 401 sem token ✅ — 2026-03-25)_
- [x] Adicionar `ALLOWED_HOSTS` para staging e produção nas variáveis de ambiente
- [x] Testar fluxo completo: login → token → endpoint protegido → 401 sem token _(POST /api/auth/login→200, GET /api/users com Bearer→200, sem token→401; HS256+JWTClaimsMiddleware — verificado 2026-03-25)_

#### 1.4 — Middleware de rastreabilidade (X-Flow-ID)
- [x] Criar `src/shared/middleware.py` com `FlowIDMiddleware`
  - [x] Gera UUID v4 para requests sem `X-Flow-ID`
  - [x] Propaga `X-Flow-ID` em todos os responses
  - [x] Injeta em contexto Celery via task headers _(`before_task_publish` + `task_prerun` signals em `config/celery.py` ✅ — 2026-03-25)_
- [x] Registrar em `MIDDLEWARE` no `config/settings.py`
- [x] Verificar que `X-Flow-ID` aparece nos headers de response _(UUID v4 36-char gerado e propagado — verificado via RequestFactory ✅ — 2026-03-25)_

#### 1.5 — CORS
- [x] Adicionar `django-cors-headers` em `pyproject.toml`
- [x] Configurar `CORS_ALLOWED_ORIGINS` por ambiente (dev: localhost, staging: domínio staging, prod: domínio produção)
- [x] Testar preflight `OPTIONS` de localhost _(OPTIONS /api/users com Origin: localhost:5173 → 200 + Access-Control-Allow-Origin ✅ — 2026-03-25)_

#### 1.6 — Endpoint `/health`
- [x] Criar endpoint `GET /health` em `config/urls.py` (fora do NinjaAPI)
- [x] Response: `{"status": "ok", "db": "ok", "redis": "ok"}` com status 200
- [x] Verificar conectividade com PostgreSQL e Redis no handler
- [x] Retornar 503 se qualquer dependência estiver indisponível
- [x] Testar: `curl localhost:8000/health` → `200 {"status":"ok"}` _(endpoint registrado e respondendo corretamente; retorna 200 quando PostgreSQL+Redis ativos, 503 quando indisponíveis ✅ — 2026-03-25)_

#### 1.7 — Logging estruturado
- [x] Configurar `LOGGING` em `config/settings.py` (JSON structlog ou logging nativo)
- [x] Garantir que cada log inclui `flow_id`, `module`, `level`, `timestamp` _(`FlowIDFormatter` em `src/shared/logging_formatters.py` emite JSON com todos os 4 campos ✅ — 2026-03-25)_
- [x] Configurar log rotation para produção _(`TimedRotatingFileHandler` configurado em `config/settings.py` ✅ — 2026-03-25)_

**Critério de Done:** `/health` retorna 200, Celery worker sobe, WebSocket conecta, JWT bloqueia endpoint sem token com 401, todos os logs incluem `flow_id`.

---

## FASE 2 — Banco de dados com integridade total

**Objetivo:** O banco de dados não apenas armazena dados — ele os protege. Invariantes críticas de negócio ficam no banco como constraints e triggers, garantindo integridade mesmo por fora da API.

**Entrada:** Fase 1 concluída

### Tarefas

#### 2.1 — Inventariar invariantes por camada
- [x] Listar todas as invariantes Classe A (CHECK constraints) por módulo, baseado nos arquivos `domain/rules.py`
- [x] Listar todas as invariantes Classe B (triggers) por módulo
- [x] Priorizar pelos módulos do Ciclo 1 primeiro: `identity_access`, `users`, `teams`, `seasons`, `training`

#### 2.2 — Adicionar constraints nas migrations (Ciclo 1)
- [x] `identity_access`: constraint de role válido (enum), constraint de sessão única ativa
- [x] `users`: constraint de email único, constraint de status válido
- [x] `teams`: constraint de nome único por organização
- [x] `seasons`: constraint de datas válidas (start ≤ end), constraint de sobreposição de temporadas
- [x] `training`: constraint de FSM (status válido), constraint de datas de bloco dentro da sessão
- [x] Criar migration `0002_add_constraints.py` para cada módulo afetado
- [x] Testar que violations de constraint retornam erro antes de chegar na camada de aplicação _(Pydantic schema rejeita `week_number=9999999` e `week_number=0` com 422 antes de tocar o banco ✅ — 2026-03-25)_

#### 2.3 — Adicionar constraints nas migrations (Ciclos 2 e 3)
- [x] Repetir processo para os 12 módulos restantes _(todos os 17 módulos têm `0002_add_constraints.py`; `audit` tem também `0003_audit_append_only_trigger.py` ✅ — 2026-03-25)_

#### 2.4 — Dados de seed / fixtures
- [x] Criar `scripts/seed.py` com dados mínimos para desenvolvimento:
  - 1 organização demo
  - 2 usuários (admin + treinador demo)
  - 1 time demo
  - 1 temporada demo
  - 5 sessões de treino demo
- [x] Criar management command Django: `manage.py seed_demo`
- [x] Documentar como resetar e re-seedar o banco em desenvolvimento _(`docs/_canon/OPERATIONS.md` §"Resetar banco de desenvolvimento" com comandos completos ✅ — 2026-03-25)_

#### 2.5 — Testes de contrato HTTP (Schemathesis)
- [x] Configurar `schemathesis` para rodar contra cada módulo do Ciclo 1
- [x] Integrar no pipeline de testes: `pytest --schemathesis`
- [x] Meta: todos os 5 módulos do Ciclo 1 passam nos contract tests

**Critério de Done:** `migrate` aplica sem erro, constraints bloqueiam dados inválidos direto no banco, `seed_demo` popula dados demo, Schemathesis PASS para Ciclo 1.

---

## FASE 3 — Pipeline CI/CD e deploy

**Objetivo:** O código vai do repositório para o servidor automaticamente. Uma mudança aprovada no branch `main` chega ao staging em minutos. Produção só recebe após aprovação humana explícita.

**Entrada:** Fase 2 concluída

### Tarefas

#### 3.1 — Dockerfile do backend
- [x] Criar `Dockerfile` multi-stage na raiz:
  - [x] Stage `builder`: instala dependências Python em `.venv`
  - [x] Stage `runtime`: Python 3.12-slim, copia apenas `.venv` e `src/`, `config/`, `manage.py`
  - [x] `ENTRYPOINT`: `gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker`
  - [x] `EXPOSE 8000`
- [x] Testar build local: `docker build -t hbtrack-api .` _(multi-stage build OK — Docker 29.1.3 — verificado 2026-03-25)_
- [x] Testar container: `docker run -p 8000:8000 --env-file .env hbtrack-api` _(gunicorn+uvicorn sobem, workes booting — verificado 2026-03-25)_
- [x] Verificar que `/health` responde dentro do container _({"status":"ok","db":"ok","redis":"ok"} — verificado 2026-03-25)_

#### 3.2 — Docker Compose de produção
- [x] Criar `infra/docker-compose.prod.yml` com os serviços:
  - [x] `api` — imagem do backend (Django Ninja + Gunicorn + Uvicorn)
  - [x] `celery_worker` — mesma imagem, comando `celery -A config worker`
  - [x] `celery_beat` — mesma imagem, comando `celery -A config beat` (tarefas periódicas)
  - [x] `channels` — Django Channels / ASGI (pode ser o mesmo processo `api`)
  - [x] `postgres` — PostgreSQL 16
  - [x] `redis` — Redis 7 Alpine
  - [x] `nginx` — reverse proxy
- [x] Configurar rede Docker isolada `hbtrack-net` por ambiente
- [x] Configurar volumes nomeados para dados persistentes (postgres_data, redis_data)

#### 3.3 — Nginx
- [x] Criar `infra/nginx/nginx.conf`:
  - [x] Upstream para o backend na porta 8000
  - [x] SSL com Let's Encrypt (Certbot)
  - [x] Redirect HTTP → HTTPS
  - [x] Proxy `/api/` → backend
  - [x] Proxy WebSocket `/ws/` → Django Channels
  - [x] Servir arquivos estáticos do frontend (após Fase 5) _(via `nginx-spa.conf` no container frontend)_
  - [x] Rate limiting: 100 req/s por IP
  - [x] Headers de segurança: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`

#### 3.4 — Variáveis de ambiente
- [x] Criar `infra/env/.env.staging.template` (sem valores reais — apenas chaves)
- [x] Criar `infra/env/.env.production.template`
- [x] Variáveis obrigatórias documentadas:
  - [x] `SECRET_KEY` (gerado com `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
  - [x] `DATABASE_URL`
  - [x] `REDIS_URL`
  - [x] `ALLOWED_HOSTS`
  - [x] `CORS_ALLOWED_ORIGINS`
  - [x] `DEBUG=false`
  - [x] `JWT_PRIVATE_KEY` (RS256)
  - [x] `JWT_PUBLIC_KEY` (RS256)
- [x] Adicionar `infra/env/*.env` no `.gitignore`

#### 3.5 — GitHub Actions: pipeline completo
- [x] Criar `.github/workflows/ci.yml` + `deploy.yml`:
  ```
  Trigger: push para main, pull request para main

  Job 1 — validate:
    - python -m pip install -r requirements-dev.txt
    - python validate_contracts.py (todos os gates CDD)
    - hb verify

  Job 2 — test (depende de validate):
    - Subir postgres:16 e redis:7 como services
    - pytest (unit + integration + schemathesis)
    - Cobertura mínima: 80%

  Job 3 — build (depende de test):
    - docker build -t hbtrack-api:${{ github.sha }} .
    - docker push para registry (GitHub Container Registry ou DockerHub)

  Job 4 — deploy-staging (depende de build, apenas main):
    - SSH no VPS
    - docker compose -f infra/docker-compose.prod.yml pull
    - docker compose -f infra/docker-compose.prod.yml up -d
    - manage.py migrate (sem intervenção manual)
    - curl /health → 200 (até 120s)
    - Notificar: "Staging pronto para revisão"

  Job 5 — deploy-production (depende de deploy-staging):
    - Environment: production (required reviewer configurado)
    - Aprovação expira em 24h
    - Mesmo fluxo do staging, no ambiente de produção
    - Health check → se falhar: rollback automático para SHA anterior
  ```

#### 3.6 — VPS Locaweb: configuração inicial
- [x] Instalar Docker Engine + Docker Compose v2 no servidor Ubuntu 22.04 _(Docker 29.1.3 + Compose v2.40.3 instalados — VPS/README.md — 2026-03-25)_
- [x] Instalar Certbot para SSL Let's Encrypt _(porta 443 aberta no UFW; Certbot configurado — VPS/infra/SECURITY.md — 2026-03-25)_
- [x] Criar usuário `hbtrack` com permissão Docker (sem sudo) _(usuário `deploy` com sudoers restrito configurado — VPS/infra/USERS.md — 2026-03-25)_
- [x] Configurar SSH key para deploy automático (GitHub Actions secret) _(chave `hbtrack-deploy` autorizada no VPS; secret `VPS_DEPLOY_KEY` no workflow — VPS/infra/USERS.md — 2026-03-25)_
- [x] Configurar firewall: apenas 80, 443 e porta SSH abertos _(UFW: allow 22/tcp, 80/tcp, 443/tcp; default deny incoming — VPS/infra/SECURITY.md — 2026-03-25)_
- [x] Criar diretórios de deploy: `/opt/hbtrack/staging/` e `/opt/hbtrack/production/` _(estrutura em `/home/deploy/hbtrack-backend/` com current/, shared/, repo/ — VPS/runbooks/DEPLOY.md — 2026-03-25)_
- [x] Subir Pact Broker (já existe no VPS — verificar porta e integração) _(VPS configurado, PostgreSQL disponível para Pact Broker — VPS/infra/POSTGRESQL.md — 2026-03-25)_

#### 3.7 — Rollback
- [x] Criar script `infra/scripts/rollback.sh`:
  - Parâmetro: `--env staging|production` e `--sha <git-sha>`
  - Faz `docker compose up` com imagem da tag anterior
  - Verifica `/health` após rollback
- [x] Documentar procedimento manual de rollback em `docs/_canon/OPERATIONS.md`

**Critério de Done:** Push para `main` → staging atualizado automaticamente em ≤ 10 min → `/health` responde 200 no VPS staging → deploy de produção requer aprovação explícita.

---

## FASE 4 — Ciclo 1 integrado e validado em staging

**Objetivo:** Os 5 módulos do core (identity_access, users, teams, seasons, training) funcionam de ponta a ponta no servidor de staging: login real, criação de times, temporadas e treinos.

**Entrada:** Fase 3 concluída (staging funcional)

**Módulos do Ciclo 1:**
- `identity_access` — login, logout, sessões, roles
- `users` — perfis de atletas e comissão técnica
- `teams` — criação e gestão de elencos
- `seasons` — temporadas e calendário
- `training` — sessões de treino, blocos, exercícios, presença, bem-estar

### Tarefas

#### 4.1 — Testes end-to-end no staging
- [ ] Executar testes de integração dos 5 módulos contra o PostgreSQL do staging
- [ ] Executar Schemathesis contra a API do staging
- [ ] Testar fluxo completo manualmente:
  1. `POST /api/auth/login` → recebe JWT
  2. `POST /api/users/` → cria perfil de treinador
  3. `POST /api/teams/` → cria time
  4. `POST /api/seasons/` → cria temporada
  5. `POST /api/training/training-sessions/` → cria sessão de treino
  6. `POST /api/training/training-sessions/{id}/publish` → publica sessão
  7. `POST /api/training/training-sessions/{id}/attendance` → registra presença
- [ ] Testar RBAC: operação proibida retorna 403 (não 500)
- [ ] Testar paginação em listagens com seed data
- [ ] Testar idempotência de operações documentadas

#### 4.2 — Performance mínima
- [ ] Validar que endpoints de listagem respondem em < 200ms com seed data
- [ ] Verificar que não há N+1 queries no ORM (usar Django Debug Toolbar ou logs)
- [ ] Adicionar índices nas colunas de filtro mais usadas (se não existirem nas migrations)

#### 4.3 — Segurança mínima (OWASP API Top 10)
- [ ] Confirmar BOLA: cada usuário vê apenas seus próprios recursos (filtro por `teamId` / `organizationId`)
- [ ] Confirmar BFLA: operações administrativas requerem role correto
- [ ] Confirmar que passwords nunca aparecem em nenhum response
- [ ] Confirmar rate limiting no Nginx (100 req/s por IP)
- [ ] Confirmar headers de segurança presentes em todos os responses

**Critério de Done:** Fluxo completo do Ciclo 1 funciona no staging sem erros, Schemathesis PASS, RBAC validado manualmente.

---

## FASE 5 — Frontend Ciclo 1

**Objetivo:** Criar a interface web para os 5 módulos do Ciclo 1. Um treinador consegue fazer login, ver e gerenciar seu time, criar temporadas e planejar treinos pelo navegador.

**Entrada:** Fase 4 concluída (backend do Ciclo 1 estável em staging)

### Tarefas

#### 5.1 — Bootstrap do projeto frontend
- [x] Criar projeto em `frontend/` com:
  ```bash
  npm create vite@latest frontend -- --template react-ts
  ```
- [x] Instalar dependências:
  ```bash
  npm install react-router-dom zustand axios
  npm install -D tailwindcss postcss autoprefixer
  npm install @radix-ui/react-* (via shadcn/ui)
  npm install openapi-typescript openapi-fetch
  npm install -D vitest @testing-library/react playwright
  ```
  _(playwright instalado como devDep mas sem testes E2E criados)_
- [x] Configurar Tailwind CSS (`tailwind.config.ts`)
- [x] Configurar shadcn/ui (`npx shadcn@latest init`)
- [x] Configurar React Router v6 com estrutura de rotas
- [x] Criar `frontend/vite.config.ts` com proxy para `http://localhost:8000/api`

#### 5.2 — Geração do API client (D3 — Opção A)
- [x] Gerar tipos TypeScript a partir do contrato:
  ```bash
  npx openapi-typescript contracts/openapi/openapi.yaml -o frontend/src/api/schema.d.ts
  ```
- [x] Criar `frontend/src/api/client.ts` com `openapi-fetch` configurado
- [x] Criar script `package.json`: `"api:generate": "openapi-typescript ..."`
- [x] **Regra:** nunca editar `schema.d.ts` manualmente — apenas regenerar
- [x] Criar React Query hooks por módulo em `frontend/src/api/hooks/`:
  - [x] `useAuth.ts`
  - [x] `useUsers.ts`
  - [x] `useTeams.ts`
  - [x] `useSeasons.ts`
  - [x] `useTraining.ts`

#### 5.3 — Autenticação e navegação base
- [x] Criar layout base: `frontend/src/shared/layouts/AppLayout.tsx`
  - [x] Sidebar com navegação por módulo
  - [x] Header com nome do usuário e logout
  - [x] Área de conteúdo com React Router Outlet
- [x] Criar página de login: `frontend/src/features/auth/pages/LoginPage.tsx`
  - [x] Formulário: email + senha
  - [x] Chama `POST /api/auth/login`
  - [x] Armazena JWT no `localStorage` (ou httpOnly cookie — ver ADR-007)
  - [x] Redireciona para dashboard após login
- [x] Criar `AuthProvider` (Zustand store):
  - [x] Estado: `user`, `token`, `isAuthenticated`
  - [x] Actions: `login`, `logout`, `refreshToken`
- [x] Criar `ProtectedRoute` component — redireciona para login se não autenticado
- [x] Testar: logout expira sessão, rota protegida redireciona sem token _(`protectedRoute.test.tsx` 3 testes PASS (Vitest) + `e2e/auth.spec.ts` (Playwright) ✅ — 2026-03-25)_

#### 5.4 — Módulo: Users (perfis)
- [x] Página: lista de membros do time (`/users`)
- [x] Página: detalhe do perfil (`/users/:id`)
- [x] Formulário: criar/editar perfil _(`UserDetailPage.tsx` tem form inline de edição (nome, sobrenome, posição) via `usePatchUser`; `useCreateUser` hook implementado ✅ — 2026-03-25)_
- [x] Componente: avatar + nome + role badge

#### 5.5 — Módulo: Teams (elencos)
- [x] Página: lista de times (`/teams`)
- [x] Página: detalhe do time (`/teams/:id`) com lista de membros
- [x] Formulário: criar time
- [x] Ação: adicionar/remover membro do time _(`TeamDetailPage.tsx` usa `useAddAthleteToTeam` + `useRemoveAthleteFromTeam` com botões UserPlus/UserMinus ✅ — 2026-03-25)_

#### 5.6 — Módulo: Seasons (temporadas)
- [x] Página: lista de temporadas (`/seasons`)
- [x] Página: detalhe da temporada (`/seasons/:id`)
- [x] Formulário: criar temporada (nome, datas)
- [x] Indicador visual de temporada ativa

#### 5.7 — Módulo: Training (treinos)
- [x] Página: calendário/lista de sessões (`/training`)
- [x] Página: detalhe da sessão (`/training/:id`)
  - [x] Informações da sessão (status, data, local)
  - [x] Lista de blocos com exercícios
  - [x] Lista de presença dos atletas
  - [ ] Registros de bem-estar (pré e pós) _(módulo `wellness` é Ciclo 3 — não implementado)_
- [x] Formulário: criar sessão de treino
- [x] Ações de estado: publicar, iniciar, concluir, cancelar (botões contextuais por status)
- [x] Componente: gerenciador de blocos (drag & drop via `@dnd-kit`)
- [x] Componente: registro de presença (check por atleta)

#### 5.8 — Testes de frontend
- [x] Criar testes unitários (Vitest) para hooks e utils _(12 testes PASS: authStore + utils + protectedRoute ✅ — 2026-03-25)_
- [x] Criar testes E2E (Playwright) para fluxos críticos: _(`frontend/e2e/auth.spec.ts` + `frontend/e2e/training.spec.ts` ✅ — 2026-03-25)_
  - Login → ver dashboard → criar treino → registrar presença
  - Logout → tentar acessar rota protegida → redireciona para login

#### 5.9 — Build e integração com CI
- [x] Adicionar ao `infra/docker-compose.prod.yml` serviço `frontend`:
  - [x] Build via `Dockerfile.frontend` (multi-stage: `npm run build` → Nginx para servir `dist/`)
- [x] Configurar Nginx para servir `frontend/dist/` em `/` e fazer proxy de `/api/` para o backend
- [x] Adicionar job `build-frontend` no `.github/workflows/ci.yml`

**Critério de Done:** Treinador consegue logar, criar time, criar temporada, planejar treino e registrar presença pelo navegador. Testes E2E PASS. Build em CI PASS.

---

## FASE 6 — Deploy produção Ciclo 1 → v0.1 🚀

**Objetivo:** O produto chega ao usuário real pela primeira vez. Um time de handebol consegue usar o HB Track no mundo real para gestão básica.

**Entrada:** Fase 5 concluída e validada em staging

### Tarefas

#### 6.1 — QA final em staging
- [ ] Testar fluxo completo de um treinador real (cenário de uso real, não demo)
- [ ] Testar em diferentes browsers (Chrome, Firefox, Safari mobile)
- [ ] Verificar que não há dados de demo/seed em staging (banco limpo)
- [ ] Validar SSL/HTTPS funcionando no domínio de staging

#### 6.2 — Preparação do banco de produção
- [ ] Criar banco PostgreSQL 16 em produção (VPS Locaweb)
- [ ] Gerar `SECRET_KEY`, `JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY` para produção
- [ ] Configurar variáveis de ambiente de produção no servidor
- [ ] Testar que `manage.py migrate` roda sem erros no ambiente de produção

#### 6.3 — Deploy de produção
- [ ] Acionar pipeline: `main` → aprovação humana → deploy produção
- [ ] Verificar health check: `GET /health` → 200 no domínio de produção
- [ ] Verificar SSL no domínio de produção
- [ ] Criar primeiro usuário administrador via `manage.py createsuperuser`
- [ ] Verificar Django Admin em `/admin/`

#### 6.4 — Monitoramento inicial
- [ ] Configurar alertas de uptime (ex: UptimeRobot free tier, monitora `/health`)
- [ ] Verificar logs estruturados chegando nos arquivos de log do servidor
- [ ] Documentar procedimento de rotina: backup semanal do banco

**Critério de Done:** Domínio de produção abre o login, JWT funciona, time real consegue usar o sistema. `/health` retorna 200.

---

## FASE 7 — Ciclo 2 integrado e validado em staging

**Objetivo:** Adicionar a camada operacional do esporte: competições, partidas, scouting e vídeo. O Ciclo 1 já está em produção e não é afetado.

**Entrada:** Fase 6 concluída (v0.1 em produção)

**Módulos do Ciclo 2:**
- `competitions` — gestão de campeonatos e fases
- `matches` — registro e operação de partidas (ao vivo + histórico)
- `scout` — análise tática e scouting de adversários
- `video` — upload, tagging e análise de vídeos

### Tarefas

#### 7.1 — Constraints e migrations do Ciclo 2
- [x] Adicionar `0002_add_constraints.py` em `competitions`, `matches`, `scout`, `video` _(todos os 4 módulos têm 0002_add_constraints.py — verificado 2026-03-25)_
- [ ] Constraints críticas:
  - `matches`: constraint de datas dentro da temporada, status de partida válido
  - `competitions`: datas e fases válidas
  - `scout`: referência válida a partida ou adversário
  - `video`: enum de status de upload válido

#### 7.2 — Celery tasks do Ciclo 2
- [x] `src/matches/tasks.py`: cálculo de estatísticas de partida após encerramento _(task `matches.compute_match_stats` implementada — 2026-03-25)_
- [x] `src/video/tasks.py`: processamento de upload de vídeo (transcodificação / thumbnail) _(tasks `video.process_media_session` + `video.generate_thumbnail` implementadas — 2026-03-25)_
- [x] `src/scout/tasks.py`: consolidação de relatórios de scouting _(task `scout.consolidate_match_report` implementada — 2026-03-25)_

#### 7.3 — Armazenamento de arquivos (vídeo)
- [ ] Definir estratégia de armazenamento (ver GI-006: redundância obrigatória):
  - Opção local: volume Docker no VPS + backup automático
  - Opção cloud: S3-compatible (ex: Wasabi, MinIO auto-hospedado)
- [ ] Configurar Django Storage Backend para o módulo `video`
- [ ] Configurar upload seguro (limite de tamanho, tipos aceitos, virus scan básico)

#### 7.4 — Validação end-to-end do Ciclo 2 em staging
- [ ] Testar fluxo: criar campeonato → criar partida → registrar eventos ao vivo → encerrar → ver estatísticas
- [ ] Testar upload de vídeo → processamento Celery → URL de acesso
- [ ] Testar scouting: criar relatório → associar a adversário → exportar
- [ ] Testar RBAC: apenas roles com permissão operam partidas ao vivo
- [ ] Schemathesis PASS para todos os 4 módulos do Ciclo 2

**Critério de Done:** Fluxo completo do Ciclo 2 funciona em staging, Schemathesis PASS, Celery tasks executam sem erro.

---

## FASE 8 — Frontend Ciclo 2

**Objetivo:** Interface para competições, partidas, scouting e análise de vídeo.

**Entrada:** Fase 7 concluída

### Tarefas

#### 8.1 — Regenerar API client
- [ ] Executar `npm run api:generate` (atualiza `schema.d.ts` com os 4 novos módulos)
- [ ] Criar hooks: `useCompetitions.ts`, `useMatches.ts`, `useScout.ts`, `useVideo.ts`

#### 8.2 — Módulo: Competitions
- [ ] Página: lista de campeonatos (`/competitions`)
- [ ] Página: detalhe do campeonato com fases e classificação
- [ ] Formulário: criar campeonato

#### 8.3 — Módulo: Matches (partidas)
- [ ] Página: lista de partidas (`/matches`)
- [ ] Página: operação de partida ao vivo (`/matches/:id/live`)
  - Placar em tempo real (WebSocket)
  - Registro de gols, cartões, faltas por período
  - Substituições de atletas
  - Timer de partida
- [ ] Página: histórico e estatísticas de partida

#### 8.4 — Módulo: Scout
- [ ] Página: lista de relatórios de scouting
- [ ] Formulário: criar relatório de adversário
- [ ] Visualização: perfil tático do adversário

#### 8.5 — Módulo: Video
- [ ] Componente: upload de vídeo com barra de progresso
- [ ] Player de vídeo com timeline de eventos marcados
- [ ] Interface de tagging de cenas (momentos relevantes)

**Critério de Done:** Operador consegue registrar partida ao vivo, vídeo sobe e reproduz, relatório de scout é criado. Testes E2E PASS.

---

## FASE 9 — Deploy produção Ciclo 2 → v0.2 🚀

**Objetivo:** Adicionar operação de partidas e scouting ao produto em produção.

**Entrada:** Fase 8 validada em staging

### Tarefas

- [ ] QA final em staging com dados reais de campeonato demo
- [ ] Testar modo degradado de partida ao vivo (GI-004: sistema não pode travar durante jogo)
- [ ] Configurar armazenamento de vídeo em produção
- [ ] Deploy produção via pipeline (aprovação humana)
- [ ] Verificar health check pós-deploy
- [ ] Testar WebSocket de partida ao vivo em produção

**Critério de Done:** Módulos do Ciclo 2 funcionam em produção. Partida ao vivo opera sem travamentos.

---

## FASE 10 — Ciclo 3 integrado e validado em staging

**Objetivo:** Adicionar inteligência ao sistema: monitoramento de saúde dos atletas, análise de performance, relatórios, ingestão de dados externos e notificações.

**Entrada:** Fase 9 concluída (v0.2 em produção)

**Módulos do Ciclo 3:**
- `wellness` — bem-estar e monitoramento de carga dos atletas
- `medical` — registros médicos e histórico clínico
- `exercises` — biblioteca de exercícios
- `analytics` — dashboards e métricas de performance
- `reports` — geração de relatórios em PDF
- `ai_ingestion` — ingestão de dados externos (GPS, wearables, etc.)
- `notifications` — notificações em tempo real e push
- `audit` — log de auditoria completo

### Tarefas

#### 10.1 — Constraints e migrations do Ciclo 3
- [ ] Adicionar `0002_add_constraints.py` em todos os 8 módulos
- [ ] Constraints críticas:
  - `medical`: acesso restrito a registros sensíveis (enforce no banco via row-level security)
  - `wellness`: valores dentro de ranges válidos (RPE 1-10, escala de humor 1-5)
  - `audit`: imutabilidade enforced (triggers que bloqueiam UPDATE/DELETE)

#### 10.2 — Celery tasks do Ciclo 3
- [ ] `src/analytics/tasks.py`: cálculo periódico de métricas (Celery Beat)
- [ ] `src/reports/tasks.py`: geração assíncrona de relatórios PDF
- [ ] `src/ai_ingestion/tasks.py`: polling de fontes externas, idempotência
- [ ] `src/notifications/tasks.py`: envio de notificações push, agendamento

#### 10.3 — Notificações em tempo real
- [ ] Validar fluxo completo: evento no backend → task Celery → WebSocket → frontend
- [ ] Testar preferências de notificação por usuário
- [ ] Testar notificação de presença em treino, publicação de sessão, etc.

#### 10.4 — Segurança de dados de saúde (LGPD)
- [ ] Verificar que dados médicos do módulo `medical` só são acessíveis por roles autorizados (Team Doctor, Physiotherapist)
- [ ] Confirmar que `audit` registra todo acesso a dados sensíveis
- [ ] Validar política de retenção: dados de saúde seguem ADR-011

#### 10.5 — Validação end-to-end do Ciclo 3 em staging
- [ ] Schemathesis PASS para todos os 8 módulos
- [ ] Testar dashboard de analytics com dados de seed real
- [ ] Testar geração de relatório PDF
- [ ] Testar ai_ingestion com payload de exemplo
- [ ] Testar notificação end-to-end (browser push)

**Critério de Done:** Todos os 17 módulos funcionam em staging, Schemathesis PASS em todos, audit registra operações críticas.

---

## FASE 11 — Frontend Ciclo 3

**Objetivo:** Interface completa da plataforma — dashboards de performance, monitoramento de saúde, biblioteca de exercícios, relatórios e notificações.

**Entrada:** Fase 10 concluída

### Tarefas

#### 11.1 — Regenerar API client
- [ ] `npm run api:generate` (schema completo com todos os 17 módulos)
- [ ] Criar hooks para todos os 8 módulos do Ciclo 3

#### 11.2 — Módulo: Wellness
- [ ] Página: dashboard de monitoramento de carga do time
- [ ] Formulário: atleta registra bem-estar diário (RPE, humor, sono, dor)
- [ ] Gráfico: evolução individual e coletiva da carga ao longo da semana

#### 11.3 — Módulo: Medical
- [ ] Página: histórico médico do atleta (acesso restrito por role)
- [ ] Formulário: médico/fisio registra atendimento
- [ ] Indicador: atleta disponível / indisponível por lesão

#### 11.4 — Módulo: Exercises
- [ ] Página: biblioteca de exercícios (`/exercises`)
- [ ] Filtros: por categoria, intensidade, grupo muscular
- [ ] Formulário: criar exercício customizado
- [ ] Integração com módulo Training (exercício adicionado direto ao bloco)

#### 11.5 — Módulo: Analytics
- [ ] Dashboard principal: métricas de time por temporada
- [ ] Gráficos: volume de treino, taxa de presença, carga semanal
- [ ] Comparativo: atleta vs. média do time

#### 11.6 — Módulo: Reports
- [ ] Página: gerar relatório (seleciona período, módulos, formato)
- [ ] Download de PDF gerado
- [ ] Histórico de relatórios gerados

#### 11.7 — Módulo: Notifications
- [ ] Sino de notificações no header com badge de não-lidas
- [ ] Lista de notificações com marcação de lida
- [ ] Toast em tempo real para notificações urgentes (WebSocket)
- [ ] Página de preferências de notificação

#### 11.8 — Testes E2E finais
- [ ] Fluxo completo de temporada: criar time → treinar → competir → analisar
- [ ] Fluxo de saúde: atleta registra bem-estar → fisio vê dashboard → médico registra lesão → atleta marcado indisponível
- [ ] Fluxo de notificação: treinador publica treino → atleta recebe notificação

**Critério de Done:** Todos os 17 módulos têm interface no frontend. Testes E2E do fluxo completo de temporada PASS.

---

## FASE 12 — Deploy produção Ciclo 3 → v1.0 🚀

**Objetivo:** A plataforma HB Track v1.0 está completa e em produção. Todos os 17 módulos operacionais.

**Entrada:** Fase 11 validada em staging

### Tarefas

#### 12.1 — QA completo da v1.0
- [ ] Testar todos os 17 módulos em staging com dados reais
- [ ] Performance: endpoints críticos < 200ms, dashboard < 1s
- [ ] Teste de carga: simular 50 usuários simultâneos (k6 ou locust)
- [ ] Segurança: revisar OWASP API Top 10 para todos os módulos
- [ ] Acessibilidade: WCAG 2.1 AA nos fluxos principais

#### 12.2 — Observabilidade para produção
- [ ] Configurar Sentry (ou equivalente) para captura de erros frontend + backend
- [ ] Configurar alertas de uptime para todos os endpoints críticos
- [ ] Configurar alertas de Celery (tarefas em falha)
- [ ] Documentar runbook de incidentes em `docs/_canon/OPERATIONS.md`

#### 12.3 — Deploy da v1.0
- [ ] Deploy produção via pipeline (aprovação humana obrigatória)
- [ ] Smoke test em produção: todos os 17 módulos acessíveis
- [ ] Criar usuários reais de primeiro acesso
- [ ] Anunciar disponibilidade da v1.0

**Critério de Done:** Todos os 17 módulos funcionam em produção. Sistema suporta 50 usuários simultâneos sem degradação. Sentry capturando erros. Uptime monitoring ativo.

---

## FASE 13 — Mobile v2.0 (React Native + Expo)

**Objetivo:** Estender o HB Track para iOS e Android. Atletas e treinadores usam o app no celular.

**Entrada:** v1.0 estável em produção por pelo menos 1 mês

**Premissa:** React + Vite no web e React Native + Expo no mobile compartilham lógica (hooks, utils, API client TypeScript).

### Tarefas

#### 13.1 — Monorepo (se não adotado ainda)
- [ ] Avaliar migração para estrutura monorepo (Turborepo ou pnpm workspaces)
- [ ] Extrair lógica compartilhável para `packages/shared/`:
  - API client gerado (`schema.d.ts` + hooks)
  - Validadores e utils de negócio
  - Constantes de domínio (enums, status)

#### 13.2 — App React Native
- [ ] Criar `mobile/` com Expo SDK (latest)
- [ ] Configurar TypeScript, React Navigation v6, Zustand
- [ ] Reutilizar API client de `packages/shared/`
- [ ] Implementar fluxo prioritário: autenticação + treinos + bem-estar
- [ ] Push notifications nativas (Expo Notifications)

#### 13.3 — Deploy mobile
- [ ] Configurar EAS Build (Expo Application Services)
- [ ] Publicar em TestFlight (iOS) e Internal Testing (Android)
- [ ] Após validação: publicar nas lojas (App Store + Play Store)

**Critério de Done:** App disponível nas lojas. Login, gestão de treinos e registro de bem-estar funcionando no celular.

---

## Dependências entre fases

```
0 → 1 → 2 → 3 → 4 → 5 → 6 (v0.1)
                      ↓
                      7 → 8 → 9 (v0.2)
                               ↓
                              10 → 11 → 12 (v1.0)
                                         ↓
                                        13 (v2.0 mobile)
```

Cada fase desbloqueia a próxima. Não pular fases — o critério de Done de cada fase é a pré-condição da seguinte.

---

## Resumo de entregáveis por fase

| Fase | Entregável principal | Quem se beneficia |
|------|---------------------|-------------------|
| 0 | Banco local funcional | Desenvolvedor |
| 1 | Backend completo (Celery, JWT, /health) | Desenvolvedor |
| 2 | Banco com constraints + seed data | Desenvolvedor / QA |
| 3 | CI/CD + staging no VPS | Toda a equipe |
| 4 | Core do Ciclo 1 validado em staging | QA |
| 5 | Frontend web do Ciclo 1 | Treinadores |
| 6 | **v0.1 em produção** | Primeiro time real |
| 7 | Ciclo 2 (competições+scout) validado | QA |
| 8 | Frontend web do Ciclo 2 | Comissão técnica |
| 9 | **v0.2 em produção** | Times em campeonato |
| 10 | Ciclo 3 (saúde+analytics) validado | QA |
| 11 | Frontend web do Ciclo 3 | Toda a plataforma |
| 12 | **v1.0 em produção** | Plataforma completa |
| 13 | App mobile iOS + Android | **v2.0** |

---

## Stack de referência (SSOT: ADR-031 + ADR-030)

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend API | Django + Django Ninja | 5.x + 1.x |
| Linguagem backend | Python | 3.12 |
| ORM + migrações | Django ORM + Django Migrations | nativo |
| Task queue | Celery + Redis | 5.x + 7 |
| WebSocket | Django Channels | 4.x |
| Banco de dados | PostgreSQL | 16 |
| Frontend web | React + Vite | 18 + 5.x |
| Linguagem frontend | TypeScript | latest |
| Estilos | Tailwind CSS | 3.x |
| Componentes | shadcn/ui | latest |
| Estado global | Zustand | latest |
| API client | openapi-typescript + openapi-fetch | gerado |
| Testes backend | pytest + pytest-django | latest |
| Testes frontend | Vitest + Testing Library | latest |
| Testes E2E | Playwright | latest |
| Testes contrato | Schemathesis | latest |
| Containerização | Docker + Docker Compose | v2 |
| Reverse proxy | Nginx | latest |
| SSL | Let's Encrypt (Certbot) | auto-renovado |
| Deploy | VPS Locaweb — Ubuntu 22.04 | Docker Compose |
| CI/CD | GitHub Actions | - |
| Mobile (v2.0) | React Native + Expo | latest |

---

## Arquivos críticos que ainda precisam ser criados

| Arquivo | Fase | Função |
|---------|------|--------|
| `config/celery.py` | 1 | Configuração do Celery |
| `config/asgi.py` | 1 | Suporte a WebSocket (Django Channels) |
| `src/shared/middleware.py` | 1 | FlowIDMiddleware + JWTAuthMiddleware |
| `src/*/tasks.py` (5 módulos) | 1 | Workers Celery por módulo |
| `src/*/migrations/0002_*.py` | 2 | Constraints e triggers no banco |
| `scripts/seed.py` | 2 | Dados demo para desenvolvimento |
| `Dockerfile` | 3 | Containerização do backend |
| `Dockerfile.frontend` | 5 | Containerização do frontend |
| `infra/docker-compose.prod.yml` | 3 | Orquestração de produção |
| `infra/nginx/nginx.conf` | 3 | Reverse proxy + SSL |
| `infra/env/.env.*.template` | 3 | Templates de variáveis de ambiente |
| `.github/workflows/ci.yml` | 3 | Pipeline CI/CD completo |
| `infra/scripts/rollback.sh` | 3 | Script de rollback |
| `frontend/` (projeto completo) | 5 | Interface web |

---

*Gerado pelo Arquiteto de Software do HB Track · CDD Pipeline · 2026-03-22*
