---
doc_type: canon
version: "1.3.0"
status: active
created: "2026-03-17"
last_reviewed: "2026-04-01"
decision_ref: D5, D6
state_semantics: current-state
---

# DEPLOY_PIPELINE.md
> Documento normativo do fluxo de deploy do HB Track.
> SSOT estruturado complementar: `docs/_canon/graph/ops/`.

## 0. Autoridade

Este documento nao e o source master de ambiente, secrets, topologia ou endpoints.
Esses conceitos vivem em:

- `docs/_canon/graph/ops/environment_catalog.yaml`
- `docs/_canon/graph/ops/secrets_catalog.yaml`
- `docs/_canon/graph/ops/service_topology.yaml`
- `docs/_canon/graph/ops/deploy_contract.yaml`
- `docs/_canon/graph/ops/runtime_endpoints.yaml`
- `docs/_canon/graph/ops/github_actions_catalog.yaml`

Este arquivo consolida a politica e o fluxo operacional aprovados por ADRs sobre o estado real do repositorio.

## 1. Baseline operacional atual

Artefatos presentes e ativos no workspace:

- `.github/workflows/deploy.yml`
- `Dockerfile`
- `infra/docker-compose.prod.yml`
- `infra/docker-compose.pact-broker.yml`
- `infra/nginx/nginx.conf`
- `infra/nginx/nginx.staging.conf`
- `infra/scripts/rollback.sh`
- `infra/env/.env.staging.template`
- `infra/env/.env.production.template`
- `config/urls.py`

Regra normativa:

- promocao para `staging_validated` exige health check real em staging
- promocao para `released` exige aprovacao humana e health check real em producao
- rollback canonicamente aceito e o definido em `infra/scripts/rollback.sh`
- o workflow vigente renderiza `.env` via `scripts/deploy/inject_env.sh` e `scripts/deploy/render_env_from_contract.py`, com falha fechada se faltar valor obrigatorio

## 2. Plataforma e ambientes

Plataforma aprovada por `ADR-027`:

- VPS Locaweb
- Docker Compose v2
- Nginx como reverse proxy
- PostgreSQL 16
- Redis 7
- Certbot para TLS

Ambientes:

| Ambiente | Runtime | Diretorio | URL base |
| --- | --- | --- | --- |
| `development` | workspace local | repo local | `http://localhost:8000` |
| `staging` | VPS + Compose | `/opt/hbtrack/staging` | `https://staging.handballtrack.app` |
| `production` | VPS + Compose | `/opt/hbtrack/production` | `https://api.handballtrack.app` |

## 3. Fluxo canonicamente aceito

```
push main
  -> validate
  -> test
  -> build
  -> deploy-staging
  -> GET /health em staging
  -> HTTP_RUNTIME_CONTRACT_GATE (HB_STAGING_URL obrigatoria)
  -> PACT_PROVIDER_GATE (PACT_BROKER_BASE_URL obrigatoria — ADR-025)
  -> aprovacao humana
  -> deploy-production
  -> GET /health em producao
  -> rollback automatico se o health falhar
```

Pact Broker:

- provisionado na VPS via `infra/docker-compose.pact-broker.yml` (porta 9292)
- URL configurada como GitHub variable `PACT_BROKER_BASE_URL` (B8-002)
- estrategia CDCT: ADR-025

## 4. Health, evidencias e rollback

Health endpoints canonicos:

- staging: `https://staging.handballtrack.app/health`
- producao: `https://api.handballtrack.app/health`

Endpoints operacionais complementares:

- OpenAPI local/live: `.../api/openapi.json`
- Docs live: `.../api/docs`
- Pact Broker interno: `http://<VPS_IP>:9292`

Evidencias minimas:

- `_reports/contract_gates/latest.json`
- workflow `.github/workflows/deploy.yml`
- `infra/scripts/rollback.sh`
- resposta HTTP 200 dos health checks do ambiente alvo

Rollback aceito:

- automatico no job de producao quando o health check falha
- manual via `infra/scripts/rollback.sh --env <staging|production> --sha <git-sha>`

## 5. Renderizacao deterministica de `.env`

Fluxo aceito:

- o `target-state` operacional para ambientes remotos passa a ser `.env` renderizado por contrato, nunca bootstrapado manualmente no workflow
- GitHub Environment fornece secrets/vars reais do ambiente alvo
- `scripts/deploy/inject_env.sh` chama `scripts/deploy/render_env_from_contract.py`
- secrets operacionais ativos no runtime atual incluem JWT RS256, DB, Cloudinary, Resend e Gemini; a rotacao/verificacao deles e contratual em `scripts/ops/rotate_keys.sh`
- `JWT_PRIVATE_KEY` e `JWT_PUBLIC_KEY` precisam permanecer sincronizados entre o runtime ativo e os GitHub secrets antes de qualquer redeploy; hotfix no VPS sem esse espelhamento reintroduz drift operacional
- o renderer resolve placeholders do template derivado em `infra/env/` usando os fragments compilados em `compiled_ops/deploy/`
- se faltar valor obrigatorio, o job falha fechado antes do SSH/deploy
- o `.env` resolvido passa a ser artefato efemero do job e e sincronizado para `/opt/hbtrack/<env>/.env`

Consequencia normativa:

- `.github/workflows/deploy.yml` deixa de ser source manual de variaveis operacionais
- qualquer mudanca no workflow, templates de env, compose, nginx, rollback, renderer ou runtime config deve atualizar `docs/_canon/graph/ops/` no mesmo changeset

## 6. Referencias

- `docs/_canon/decisions/ADR-025-cdct-pact-strategy.md`
- `docs/_canon/decisions/ADR-027-deploy-pipeline.md`
- `docs/_canon/graph/ops/deploy_contract.yaml`
- `docs/_canon/graph/ops/runtime_endpoints.yaml`
- `docs/_canon/graph/ops/service_topology.yaml`
- `.github/workflows/deploy.yml`
