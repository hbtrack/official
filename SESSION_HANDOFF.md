---
data_ultima_sessao: "2026-03-24"
branch_ativo: hb-track-contratos-driven
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: infra
fase_roadmap: 3
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: roadmap-fase3-vps-provisioning
resultado: DONE
proxima_acao_permitida: "Iniciar FASE 4 do ROADMAP.md (Ciclo 1 integrado em staging — E2E, RBAC, performance)."
bloqueios_ativos: []
evidence_paths:
  - Dockerfile
  - requirements.txt
  - infra/docker-compose.prod.yml
  - infra/nginx/nginx.conf
  - infra/nginx/nginx.staging.conf
  - infra/env/.env.staging.template
  - infra/env/.env.production.template
  - infra/scripts/rollback.sh
  - .github/workflows/deploy.yml
  - docs/_canon/VPS_SETUP.md
---
# SESSION HANDOFF — HB TRACK
> Delta-only. Histórico em `_archive/SESSION_HANDOFF_PRE_FASE0_20260323.md`

## Estado Geral
**Data:** 2026-03-24 | **Branch:** hb-track-contratos-driven | **CI:** UNKNOWN
**Modo:** ROADMAP | **task_type:** execute_roadmap_phase | **boot_profile:** roadmap_execution
**Módulo foco:** infra | **Fase ROADMAP:** 3 | **Resultado:** DONE

## O que foi feito

### FASE 3 — Infraestrutura Docker + CI/CD + VPS Provisioning [COMPLETO]

#### Tarefa 3.1 — Dockerfile multi-stage ✅
- `Dockerfile` — builder (`python:3.12-slim`) + runtime minimal, non-root user `hbtrack`
- Venv criado em `/app/.venv` (shebang correto após cópia entre stages)
- ENTRYPOINT: gunicorn config.asgi:application + UvicornWorker

#### Tarefa 3.2 — requirements.txt ✅
- Criado com dependências de produção
- `django-ninja>=1.3.0` (fix `ForwardRef._evaluate()` no Python 3.12)

#### Tarefa 3.3 — docker-compose.prod.yml ✅
- 7 serviços: api, celery_worker, celery_beat, postgres:16, redis:7, nginx, certbot
- `entrypoint:` (não `command:`) para sobrescrever ENTRYPOINT do Dockerfile
- `env_file: ../.env` (relativo ao arquivo compose em `infra/`)

#### Tarefa 3.4 — config/settings.py + config/urls.py ✅
- `django.contrib.staticfiles` adicionado ao INSTALLED_APPS
- `STATIC_URL`, `STATIC_ROOT` configurados
- `GET /health` verifica PostgreSQL + Redis, retorna 200/503

#### Tarefa 3.5 — Nginx ✅
- `infra/nginx/nginx.conf` — reverse proxy + SSL (handballtrack.app)
- `infra/nginx/nginx.staging.conf` — idem para staging.handballtrack.app
- HTTP→HTTPS redirect, TLS 1.2/1.3, rate limiting, WebSocket upgrade, headers de segurança

#### Tarefa 3.6 — Templates .env ✅
- `infra/env/.env.staging.template` — todas as variáveis com placeholder CHANGE_ME_*
- `infra/env/.env.production.template` — idem para produção

#### Tarefa 3.7 — GitHub Actions deploy.yml ✅
- Corrigido: `VPS_HOST` → `VPS_HOST_STAGING` / `VPS_HOST_PRODUCTION`
- Corrigido: `docker compose` → `docker compose -f infra/docker-compose.prod.yml`
- Corrigido: rollback lê `PREV_SHA` de `.last_sha` (não `.env.deploy`)
- Build context corrigido: `./Hb Track - Backend` → `.`

#### Tarefa 3.8 — VPS Provisioning (Locaweb 191.252.185.34) ✅
- Docker Engine + Compose instalados, usuário `hbtrack` criado com grupo docker
- UFW: portas 22, 80, 443 abertas
- `/opt/hbtrack/staging/.env` preenchido com credenciais reais
- Imagem construída localmente no VPS, stack iniciada
- SSL gerado via certbot standalone para `staging.handballtrack.app`
- GitHub Actions secrets adicionados: VPS_SSH_KEY, VPS_HOST_STAGING, VPS_USER, STAGING_URL

#### Tarefa 3.9 — rollback.sh ✅
- `infra/scripts/rollback.sh` — rollback seguro por SHA

#### Tarefa 3.10 — VPS Setup Docs ✅
- `docs/_canon/VPS_SETUP.md` — runbook de provisionamento

## Evidências
- `https://staging.handballtrack.app/health` → HTTP 200 `{"status":"ok","db":"ok","redis":"ok"}`
- Stack docker: api (healthy), postgres (healthy), redis (healthy), nginx (up), certbot (up)
- GitHub Actions secrets configurados no repositório `hbtrack/official`

## Bloqueios ativos
Nenhum.

## Próxima ação permitida
Iniciar **FASE 4 do ROADMAP.md** (Ciclo 1 integrado em staging — E2E, RBAC, performance).
