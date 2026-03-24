---
doc_type: canon
version: "1.1.0"
status: active
created: "2026-03-17"
last_reviewed: "2026-03-23"
decision_ref: D5, D6
state_semantics: target-state
---

# DEPLOY_PIPELINE.md
> Documento normativo — SSOT para estratégia de deploy do HB Track.
> Versão: 1.1.0 | Status: active | Criado: 2026-03-17 | Revisado: 2026-03-23
> Decisões: D5 = VPS Locaweb (Docker Compose) | D6 = Staging → aprovação → produção

## 0. Status Operacional Atual

O design de deploy está **aprovado**, mas a automação do repositório ainda está **parcial**.

Artefatos presentes no repo:
- `docs/_canon/DEPLOY_PIPELINE.md`
- `docs/_canon/decisions/ADR-027-deploy-pipeline.md`
- `.github/workflows/deploy.yml`

Assets ainda ausentes no workspace:
- `Dockerfile`
- `infra/docker-compose.prod.yml`
- `infra/nginx/nginx.conf`

Regra normativa:
- enquanto esses assets não existirem e não houver health endpoint operacional em runtime, nenhum módulo pode ser promovido para `staging_validated` ou `released` apenas com base no workflow versionado;
- o workflow representa o **target-state** de CI/CD, não evidência suficiente de operação.

## 1. Plataforma de Deploy (D5)

**Escolha:** VPS Locaweb — mesmo servidor que hospeda o Pact Broker.

- Sistema operacional: Ubuntu 22.04 LTS
- Orquestração: Docker Compose v2
- Reverse proxy: Nginx (SSL via Let's Encrypt / Certbot)
- Banco de dados: PostgreSQL 16
- Rede Docker: `hbtrack-net` por ambiente

## 2. Ambientes Alvo

| Ambiente | Branch | Estratégia alvo | Status atual |
|---|---|---|---|
| `development` | qualquer | manual/local | disponível via setup local |
| `staging` | `main` | automático via workflow + SSH | bloqueado até assets de deploy existirem |
| `production` | `main` após aprovação | manual com approval gate | bloqueado até staging estar validado |

## 3. Pipeline Alvo de Entrega

```
[push main]
  → validate_contracts.py
  → pytest
  → docker build + tag SHA
  → deploy staging
  → GET /health = 200
  → aprovação humana
  → deploy produção
  → GET /health = 200
  → rollback para SHA anterior se falhar
```

Este fluxo só pode ser tratado como ativo de ponta a ponta quando os assets ausentes da seção 0 existirem no repo e o runtime expuser `GET /health`.

## 4. Aprovação, Health e Rollback

- quem fez merge na `main` não deve aprovar o próprio deploy, salvo hotfix justificado
- health check canônico: `GET /health` com HTTP 200 e payload `{\"status\":\"ok\"}` em até 120s
- rollback canônico: re-deploy da imagem SHA anterior em até 5 minutos

## 5. Variáveis por Ambiente

| Variável | Staging | Production |
|---|---|---|
| `DATABASE_URL` | `postgres://...staging` | `postgres://...prod` |
| `PACT_BROKER_BASE_URL` | `http://<VPS_IP>:9292` | `http://<VPS_IP>:9292` |
| `ENV` | `staging` | `production` |
| `SECRET_KEY` | secret de staging | secret de produção |

Segredos vivem em GitHub Secrets. Nunca em código ou `.env` versionado.

## 6. Referências

- ADR: `docs/_canon/decisions/ADR-027-deploy-pipeline.md`
- Workflow alvo: `.github/workflows/deploy.yml`
- Arquitetura de código: `docs/_canon/CODE_ARCHITECTURE.md`
- Pact Broker: `docs/_canon/decisions/ADR-025-cdct-pact-strategy.md`
