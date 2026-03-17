# DEPLOY_PIPELINE.md
> Documento normativo — SSOT para estratégia de deploy do HB Track.
> Versão: 1.0.0 | Status: active | Criado: 2026-03-17
> Decisões: D5 = VPS Locaweb (Docker Compose) | D6 = Staging → aprovação → produção

## 1. Plataforma de Deploy (D5)

**Escolha:** VPS Locaweb — mesmo servidor que hospeda o Pact Broker.

- Sistema operacional: Ubuntu 22.04 LTS
- Orquestração: Docker Compose v2
- Reverse proxy: Nginx (SSL via Let's Encrypt / Certbot)
- Banco de dados: PostgreSQL 16 (container Docker)
- Rede Docker: `hbtrack-net` (isolada por ambiente)

## 2. Ambientes

| Ambiente | Domínio | Branch | Deploy |
|---|---|---|---|
| `development` | localhost | qualquer | manual (`docker compose up`) |
| `staging` | `staging.hbtrack.<domínio>` | `main` | automático via CI/CD |
| `production` | `hbtrack.<domínio>` | `main` (após aprovação) | manual (aprovação humana) |

## 3. Pipeline de Entrega (D6 = Opção C)

```
[push main]
    │
    ▼
[1. VALIDATE]         ← python3 validate_contracts.py (todos os gates)
    │ PASS
    ▼
[2. TEST]             ← pytest (unit + integration)
    │ PASS
    ▼
[3. BUILD]            ← docker build → tag com git SHA
    │ PASS
    ▼
[4. DEPLOY STAGING]   ← automático: docker compose up no servidor VPS (staging)
    │
    ▼
[5. APROVAÇÃO HUMANA] ← notificação enviada ao responsável
    │                    GitHub Actions: environment protection (required reviewer)
    │ APROVADO
    ▼
[6. DEPLOY PRODUÇÃO]  ← docker compose up no servidor VPS (production)
    │
    ▼
[7. HEALTH CHECK]     ← GET /health → 200 OK em até 120s
    │ FALHA
    ▼
[8. ROLLBACK AUTO]    ← docker compose up com imagem anterior (tag SHA-1)
```

## 4. Regra de Aprovação

- Responsável: quem fez merge na `main` **não pode** aprovar o próprio deploy
- Aprovação expira em: 24 horas (se não aprovado, deploy é cancelado)
- Aprovação via: GitHub Actions → Environments → `production` → required reviewers
- Em caso de incidente crítico (hotfix): aprovação pode ser feita pelo mesmo autor com justificativa registrada

## 5. Health Check

- Endpoint: `GET /health`
- Timeout: 120 segundos após container iniciar
- Critério de sucesso: HTTP 200 + `{"status": "ok"}`
- Critério de falha: timeout ou status ≠ 200 → rollback automático

## 6. Rollback

- Estratégia: re-deploy da imagem Docker com tag SHA anterior
- Gatilho automático: health check falhar após deploy
- Gatilho manual: qualquer membro da equipe via GitHub Actions
- Tempo máximo de rollback: 5 minutos

## 7. Variáveis de Ambiente por Ambiente

| Variável | Staging | Production |
|---|---|---|
| `DATABASE_URL` | `postgres://...staging` | `postgres://...prod` |
| `PACT_BROKER_BASE_URL` | `http://<VPS_IP>:9292` | `http://<VPS_IP>:9292` |
| `ENV` | `staging` | `production` |
| `SECRET_KEY` | secret de staging | secret de produção |

Variáveis sensíveis armazenadas em: **GitHub Secrets** (nunca em código ou `.env` commitado).

## 8. Referências

- ADR: `docs/_canon/decisions/ADR-027-deploy-pipeline.md`
- Workflow CI/CD: `.github/workflows/deploy.yml`
- Arquitetura de código: `docs/_canon/CODE_ARCHITECTURE.md`
- Pact Broker: `docs/_canon/decisions/ADR-025-cdct-pact-strategy.md`
