# ROADMAP — HB Track
> Versão: 1.0.0 | Data: 2026-03-22 | Decisões: D1-A · D2-C · D3-A
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

## Estado atual (snapshot 2026-03-22)

### O que já existe e está validado
| Camada | Status | Detalhe |
|--------|--------|---------|
| Contratos OpenAPI | ✅ 17/17 módulos `implementation_ready` | SSOT para toda a API |
| Código backend (Clean Architecture) | ✅ 17/17 módulos | domain / application / infrastructure / api / schemas |
| Migrações Django | ✅ 17/17 módulos | `0001_initial.py` criado e válido |
| Testes unitários | ✅ 720 PASS | Lógica de domínio e use cases |
| Testes de integração | ⏭ 33 SKIPPED | Aguardam PostgreSQL rodando |
| Infra local (Docker Compose) | ✅ Definida | PostgreSQL 12 + Redis 7 |
| Pipeline CDD | ✅ PASS | validate_contracts, hb verify, hb artifact |
| Feature Registry | ✅ 31 features | 10 validated + 21 implemented (código gerado) |
| Frontend | ❌ Não iniciado | Projeto React/Vite não existe |
| Dockerfile | ❌ Não existe | Containerização do backend pendente |
| CI/CD | ❌ Não existe | GitHub Actions não configurado |
| Deploy VPS | ❌ Não existe | Staging e produção não configurados |
| Celery workers | ❌ Não configurado | `config/celery.py` não existe |
| Django Channels | ❌ Não configurado | WebSocket para notificações pendente |
| Endpoint `/health` | ❌ Não existe | Obrigatório para deploy + rollback automático |
| Constraints de banco (Classe A/B) | ❌ Não adicionados | CHECK constraints e triggers pendentes |

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
- [ ] Executar `docker compose -f infra/docker-compose.yml up -d postgres redis`
- [ ] Verificar que PostgreSQL está acessível em `localhost:5433`
- [ ] Verificar que Redis está acessível em `localhost:6379`

#### 0.2 — Aplicar todas as migrações
- [ ] Executar `.venv/bin/python manage.py migrate` (todos os 17 módulos)
- [ ] Confirmar que nenhuma migração falha ou gera conflito
- [ ] Validar schema criado no banco com `manage.py showmigrations`

#### 0.3 — Validar servidor Django
- [ ] Executar `.venv/bin/python manage.py check` sem erros
- [ ] Executar `.venv/bin/python manage.py runserver` e confirmar que sobe
- [ ] Acessar `/api/docs` (Django Ninja UI automática) e verificar todos os 17 routers carregados

#### 0.4 — Validar testes de integração
- [ ] Rodar `.venv/bin/pytest` com PostgreSQL ativo
- [ ] Confirmar que os 33 testes antes skipped agora passam
- [ ] Meta: **720 + 33 = ≥ 753 testes PASS, 0 SKIP**

**Critério de Done:** `pytest` roda sem skip, `manage.py runserver` sobe, todos os 17 routers aparecem no `/api/docs`.

---

## FASE 1 — Backend completo

**Objetivo:** Adicionar as peças de infraestrutura Django que faltam para o sistema funcionar como produto real: autenticação JWT funcional, workers Celery, notificações em tempo real, middleware de rastreabilidade e endpoint de health check.

**Entrada:** Fase 0 concluída

### Tarefas

#### 1.1 — Celery (workers assíncronos)
- [ ] Criar `config/celery.py` com configuração Celery 5.x + Redis broker
- [ ] Adicionar `CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND` em `config/settings.py`
- [ ] Criar `src/notifications/tasks.py` (envio de notificações assíncronas)
- [ ] Criar `src/ai_ingestion/tasks.py` (processamento de ingestion jobs)
- [ ] Criar `src/analytics/tasks.py` (cálculo de métricas periódicas)
- [ ] Criar `src/reports/tasks.py` (geração de relatórios em background)
- [ ] Criar `src/audit/tasks.py` (retenção e exportação de auditoria)
- [ ] Testar: `celery -A config worker --loglevel=info` sobe sem erros

#### 1.2 — Django Channels (WebSocket)
- [ ] Adicionar `channels` e `channels_redis` em `pyproject.toml`
- [ ] Criar `config/asgi.py` com `ProtocolTypeRouter` (HTTP + WebSocket)
- [ ] Configurar `CHANNEL_LAYERS` com Redis em `config/settings.py`
- [ ] Criar consumer WebSocket em `src/notifications/consumers.py`
- [ ] Registrar rota WebSocket em `config/urls.py` (via `ProtocolTypeRouter`)
- [ ] Testar conexão WebSocket local

#### 1.3 — Autenticação JWT real
- [ ] Validar que `identity_access` emite JWT RS256 válido no login
- [ ] Criar middleware Django `JWTAuthMiddleware` em `src/identity_access/middleware.py`
- [ ] Registrar middleware em `MIDDLEWARE` no `config/settings.py`
- [ ] Adicionar `ALLOWED_HOSTS` para staging e produção nas variáveis de ambiente
- [ ] Testar fluxo completo: login → token → endpoint protegido → 401 sem token

#### 1.4 — Middleware de rastreabilidade (X-Flow-ID)
- [ ] Criar `src/shared/middleware.py` com `FlowIDMiddleware`
  - Gera UUID v4 para requests sem `X-Flow-ID`
  - Propaga `X-Flow-ID` em todos os responses
  - Injeta em contexto Celery via task headers
- [ ] Registrar em `MIDDLEWARE` no `config/settings.py`
- [ ] Verificar que `X-Flow-ID` aparece nos headers de response

#### 1.5 — CORS
- [ ] Adicionar `django-cors-headers` em `pyproject.toml`
- [ ] Configurar `CORS_ALLOWED_ORIGINS` por ambiente (dev: localhost, staging: domínio staging, prod: domínio produção)
- [ ] Testar preflight `OPTIONS` de localhost

#### 1.6 — Endpoint `/health`
- [ ] Criar endpoint `GET /health` em `config/urls.py` (fora do NinjaAPI)
- [ ] Response: `{"status": "ok", "db": "ok", "redis": "ok"}` com status 200
- [ ] Verificar conectividade com PostgreSQL e Redis no handler
- [ ] Retornar 503 se qualquer dependência estiver indisponível
- [ ] Testar: `curl localhost:8000/health` → `200 {"status":"ok"}`

#### 1.7 — Logging estruturado
- [ ] Configurar `LOGGING` em `config/settings.py` (JSON structlog ou logging nativo)
- [ ] Garantir que cada log inclui `flow_id`, `module`, `level`, `timestamp`
- [ ] Configurar log rotation para produção

**Critério de Done:** `/health` retorna 200, Celery worker sobe, WebSocket conecta, JWT bloqueia endpoint sem token com 401, todos os logs incluem `flow_id`.

---

## FASE 2 — Banco de dados com integridade total

**Objetivo:** O banco de dados não apenas armazena dados — ele os protege. Invariantes críticas de negócio ficam no banco como constraints e triggers, garantindo integridade mesmo por fora da API.

**Entrada:** Fase 1 concluída

### Tarefas

#### 2.1 — Inventariar invariantes por camada
- [ ] Listar todas as invariantes Classe A (CHECK constraints) por módulo, baseado nos arquivos `domain/rules.py`
- [ ] Listar todas as invariantes Classe B (triggers) por módulo
- [ ] Priorizar pelos módulos do Ciclo 1 primeiro: `identity_access`, `users`, `teams`, `seasons`, `training`

#### 2.2 — Adicionar constraints nas migrations (Ciclo 1)
- [ ] `identity_access`: constraint de role válido (enum), constraint de sessão única ativa
- [ ] `users`: constraint de email único, constraint de status válido
- [ ] `teams`: constraint de nome único por organização
- [ ] `seasons`: constraint de datas válidas (start ≤ end), constraint de sobreposição de temporadas
- [ ] `training`: constraint de FSM (status válido), constraint de datas de bloco dentro da sessão
- [ ] Criar migration `0002_add_constraints.py` para cada módulo afetado
- [ ] Testar que violations de constraint retornam erro antes de chegar na camada de aplicação

#### 2.3 — Adicionar constraints nas migrations (Ciclos 2 e 3)
- [ ] Repetir processo para os 12 módulos restantes (após Ciclo 1 validado)

#### 2.4 — Dados de seed / fixtures
- [ ] Criar `scripts/seed.py` com dados mínimos para desenvolvimento:
  - 1 organização demo
  - 2 usuários (admin + treinador demo)
  - 1 time demo
  - 1 temporada demo
  - 5 sessões de treino demo
- [ ] Criar management command Django: `manage.py seed_demo`
- [ ] Documentar como resetar e re-seedar o banco em desenvolvimento

#### 2.5 — Testes de contrato HTTP (Schemathesis)
- [ ] Configurar `schemathesis` para rodar contra cada módulo do Ciclo 1
- [ ] Integrar no pipeline de testes: `pytest --schemathesis`
- [ ] Meta: todos os 5 módulos do Ciclo 1 passam nos contract tests

**Critério de Done:** `migrate` aplica sem erro, constraints bloqueiam dados inválidos direto no banco, `seed_demo` popula dados demo, Schemathesis PASS para Ciclo 1.

---

## FASE 3 — Pipeline CI/CD e deploy

**Objetivo:** O código vai do repositório para o servidor automaticamente. Uma mudança aprovada no branch `main` chega ao staging em minutos. Produção só recebe após aprovação humana explícita.

**Entrada:** Fase 2 concluída

### Tarefas

#### 3.1 — Dockerfile do backend
- [ ] Criar `Dockerfile` multi-stage na raiz:
  - Stage `builder`: instala dependências Python em `.venv`
  - Stage `runtime`: Python 3.12-slim, copia apenas `.venv` e `src/`, `config/`, `manage.py`
  - `ENTRYPOINT`: `gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker`
  - `EXPOSE 8000`
- [ ] Testar build local: `docker build -t hbtrack-api .`
- [ ] Testar container: `docker run -p 8000:8000 --env-file .env hbtrack-api`
- [ ] Verificar que `/health` responde dentro do container

#### 3.2 — Docker Compose de produção
- [ ] Criar `infra/docker-compose.prod.yml` com os serviços:
  - `api` — imagem do backend (Django Ninja + Gunicorn + Uvicorn)
  - `celery_worker` — mesma imagem, comando `celery -A config worker`
  - `celery_beat` — mesma imagem, comando `celery -A config beat` (tarefas periódicas)
  - `channels` — Django Channels / ASGI (pode ser o mesmo processo `api`)
  - `postgres` — PostgreSQL 16
  - `redis` — Redis 7 Alpine
  - `nginx` — reverse proxy
- [ ] Configurar rede Docker isolada `hbtrack-net` por ambiente
- [ ] Configurar volumes nomeados para dados persistentes (postgres_data, redis_data)

#### 3.3 — Nginx
- [ ] Criar `infra/nginx/nginx.conf`:
  - Upstream para o backend na porta 8000
  - SSL com Let's Encrypt (Certbot)
  - Redirect HTTP → HTTPS
  - Proxy `/api/` → backend
  - Proxy WebSocket `/ws/` → Django Channels
  - Servir arquivos estáticos do frontend (após Fase 5)
  - Rate limiting: 100 req/s por IP
  - Headers de segurança: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`

#### 3.4 — Variáveis de ambiente
- [ ] Criar `infra/env/.env.staging.template` (sem valores reais — apenas chaves)
- [ ] Criar `infra/env/.env.production.template`
- [ ] Variáveis obrigatórias documentadas:
  - `SECRET_KEY` (gerado com `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
  - `DATABASE_URL`
  - `REDIS_URL`
  - `ALLOWED_HOSTS`
  - `CORS_ALLOWED_ORIGINS`
  - `DEBUG=false`
  - `JWT_PRIVATE_KEY` (RS256)
  - `JWT_PUBLIC_KEY` (RS256)
- [ ] Adicionar `infra/env/*.env` no `.gitignore`

#### 3.5 — GitHub Actions: pipeline completo
- [ ] Criar `.github/workflows/ci.yml`:
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
- [ ] Instalar Docker Engine + Docker Compose v2 no servidor Ubuntu 22.04
- [ ] Instalar Certbot para SSL Let's Encrypt
- [ ] Criar usuário `hbtrack` com permissão Docker (sem sudo)
- [ ] Configurar SSH key para deploy automático (GitHub Actions secret)
- [ ] Configurar firewall: apenas 80, 443 e porta SSH abertos
- [ ] Criar diretórios de deploy: `/opt/hbtrack/staging/` e `/opt/hbtrack/production/`
- [ ] Subir Pact Broker (já existe no VPS — verificar porta e integração)

#### 3.7 — Rollback
- [ ] Criar script `infra/scripts/rollback.sh`:
  - Parâmetro: `--env staging|production` e `--sha <git-sha>`
  - Faz `docker compose up` com imagem da tag anterior
  - Verifica `/health` após rollback
- [ ] Documentar procedimento manual de rollback em `docs/_canon/OPERATIONS.md`

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
  5. `POST /api/training-sessions/` → cria sessão de treino
  6. `POST /api/training-sessions/{id}/publish` → publica sessão
  7. `POST /api/training-sessions/{id}/attendance` → registra presença
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
- [ ] Criar projeto em `frontend/` com:
  ```bash
  npm create vite@latest frontend -- --template react-ts
  ```
- [ ] Instalar dependências:
  ```bash
  npm install react-router-dom zustand axios
  npm install -D tailwindcss postcss autoprefixer
  npm install @radix-ui/react-* (via shadcn/ui)
  npm install openapi-typescript openapi-fetch
  npm install -D vitest @testing-library/react playwright
  ```
- [ ] Configurar Tailwind CSS (`tailwind.config.ts`)
- [ ] Configurar shadcn/ui (`npx shadcn@latest init`)
- [ ] Configurar React Router v6 com estrutura de rotas
- [ ] Criar `frontend/vite.config.ts` com proxy para `http://localhost:8000/api`

#### 5.2 — Geração do API client (D3 — Opção A)
- [ ] Gerar tipos TypeScript a partir do contrato:
  ```bash
  npx openapi-typescript contracts/openapi/openapi.yaml -o frontend/src/api/schema.d.ts
  ```
- [ ] Criar `frontend/src/api/client.ts` com `openapi-fetch` configurado
- [ ] Criar script `package.json`: `"api:generate": "openapi-typescript ..."`
- [ ] **Regra:** nunca editar `schema.d.ts` manualmente — apenas regenerar
- [ ] Criar React Query hooks por módulo em `frontend/src/api/hooks/`:
  - `useAuth.ts`
  - `useUsers.ts`
  - `useTeams.ts`
  - `useSeasons.ts`
  - `useTraining.ts`

#### 5.3 — Autenticação e navegação base
- [ ] Criar layout base: `frontend/src/shared/layouts/AppLayout.tsx`
  - Sidebar com navegação por módulo
  - Header com nome do usuário e logout
  - Área de conteúdo com React Router Outlet
- [ ] Criar página de login: `frontend/src/features/auth/pages/LoginPage.tsx`
  - Formulário: email + senha
  - Chama `POST /api/auth/login`
  - Armazena JWT no `localStorage` (ou httpOnly cookie — ver ADR-007)
  - Redireciona para dashboard após login
- [ ] Criar `AuthProvider` (Zustand store):
  - Estado: `user`, `token`, `isAuthenticated`
  - Actions: `login`, `logout`, `refreshToken`
- [ ] Criar `ProtectedRoute` component — redireciona para login se não autenticado
- [ ] Testar: logout expira sessão, rota protegida redireciona sem token

#### 5.4 — Módulo: Users (perfis)
- [ ] Página: lista de membros do time (`/users`)
- [ ] Página: detalhe do perfil (`/users/:id`)
- [ ] Formulário: criar/editar perfil
- [ ] Componente: avatar + nome + role badge

#### 5.5 — Módulo: Teams (elencos)
- [ ] Página: lista de times (`/teams`)
- [ ] Página: detalhe do time (`/teams/:id`) com lista de membros
- [ ] Formulário: criar time
- [ ] Ação: adicionar/remover membro do time

#### 5.6 — Módulo: Seasons (temporadas)
- [ ] Página: lista de temporadas (`/seasons`)
- [ ] Página: detalhe da temporada (`/seasons/:id`)
- [ ] Formulário: criar temporada (nome, datas)
- [ ] Indicador visual de temporada ativa

#### 5.7 — Módulo: Training (treinos)
- [ ] Página: calendário/lista de sessões (`/training`)
- [ ] Página: detalhe da sessão (`/training/:id`)
  - Informações da sessão (status, data, local)
  - Lista de blocos com exercícios
  - Lista de presença dos atletas
  - Registros de bem-estar (pré e pós)
- [ ] Formulário: criar sessão de treino
- [ ] Ações de estado: publicar, iniciar, concluir, cancelar (botões contextuais por status)
- [ ] Componente: gerenciador de blocos (drag & drop via `@dnd-kit`)
- [ ] Componente: registro de presença (check por atleta)

#### 5.8 — Testes de frontend
- [ ] Criar testes unitários (Vitest) para hooks e utils
- [ ] Criar testes E2E (Playwright) para fluxos críticos:
  - Login → ver dashboard → criar treino → registrar presença
  - Logout → tentar acessar rota protegida → redireciona para login

#### 5.9 — Build e integração com CI
- [ ] Adicionar ao `infra/docker-compose.prod.yml` serviço `frontend`:
  - Build via `Dockerfile.frontend` (multi-stage: `npm run build` → Nginx para servir `dist/`)
- [ ] Configurar Nginx para servir `frontend/dist/` em `/` e fazer proxy de `/api/` para o backend
- [ ] Adicionar job `build-frontend` no `.github/workflows/ci.yml`

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
- [ ] Adicionar `0002_add_constraints.py` em `competitions`, `matches`, `scout`, `video`
- [ ] Constraints críticas:
  - `matches`: constraint de datas dentro da temporada, status de partida válido
  - `competitions`: datas e fases válidas
  - `scout`: referência válida a partida ou adversário
  - `video`: enum de status de upload válido

#### 7.2 — Celery tasks do Ciclo 2
- [ ] `src/matches/tasks.py`: cálculo de estatísticas de partida após encerramento
- [ ] `src/video/tasks.py`: processamento de upload de vídeo (transcodificação / thumbnail)
- [ ] `src/scout/tasks.py`: consolidação de relatórios de scouting

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
