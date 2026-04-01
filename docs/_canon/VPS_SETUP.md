# HB Track — VPS Setup (Staging e Production)

> Runbook operacional. SSOT estruturado: `docs/_canon/graph/ops/`.
> Este arquivo nao redefine ambiente, secrets, topologia ou deploy; ele operacionaliza o que ja esta catalogado.

## 0. Fontes obrigatorias

Antes de provisionar a VPS, consulte:

- `docs/_canon/graph/ops/environment_catalog.yaml`
- `docs/_canon/graph/ops/secrets_catalog.yaml`
- `docs/_canon/graph/ops/service_topology.yaml`
- `docs/_canon/graph/ops/deploy_contract.yaml`
- `docs/_canon/graph/ops/runtime_endpoints.yaml`
- `docs/_canon/graph/ops/github_actions_catalog.yaml`

## 1. Pre-requisitos

- Ubuntu 22.04 LTS
- Docker Engine >= 24
- Docker Compose v2
- portas 22, 80, 443 e 9292 liberadas
- tres diretorios de servico: `/opt/hbtrack/staging`, `/opt/hbtrack/production`, `/opt/hbtrack/pact-broker`

## 2. Usuario e diretorios

```bash
useradd -m -s /bin/bash hbtrack
usermod -aG docker hbtrack
mkdir -p /opt/hbtrack/staging /opt/hbtrack/production /opt/hbtrack/pact-broker
chown -R hbtrack:hbtrack /opt/hbtrack
```

## 3. Docker, Compose e Certbot

```bash
curl -fsSL https://get.docker.com | sh
docker --version
docker compose version
apt-get install -y certbot
systemctl status certbot.timer
```

## 4. Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

## 5. GitHub Actions: secrets e variables

Secrets canonicos no GitHub:

| Secret | Finalidade |
| --- | --- |
| `VPS_SSH_KEY` | chave privada para `appleboy/ssh-action` e `scp-action` |
| `VPS_HOST_STAGING` | alvo SSH do staging |
| `VPS_HOST_PRODUCTION` | alvo SSH da producao |
| `VPS_USER` | usuario remoto de deploy |
| `GITHUB_TOKEN` | acesso ao GHCR |

Variables canonicas no GitHub:

| Variable | Exemplo |
| --- | --- |
| `STAGING_URL` | `https://staging.handballtrack.app` |
| `PRODUCTION_URL` | `https://api.handballtrack.app` |

## 6. .env por ambiente

Templates versionados:

- staging: `infra/env/.env.staging.template`
- producao: `infra/env/.env.production.template`

Arquivos de runtime:

- staging: `/opt/hbtrack/staging/.env`
- producao: `/opt/hbtrack/production/.env`

Regra:

- o catalogo de variaveis obrigatorias e o de `docs/_canon/graph/ops/environment_catalog.yaml`
- secrets e rotacao seguem `docs/_canon/graph/ops/secrets_catalog.yaml`
- `.env` de staging/producao deve ser renderizado por `scripts/deploy/inject_env.sh` a partir do source graph operacional
- se faltar valor obrigatorio no environment GitHub alvo, o renderer falha fechado e o deploy nao prossegue

Secrets de environment GitHub obrigatorios para `staging` e `production`:

- `SECRET_KEY`
- `DB_PASSWORD`
- `JWT_PRIVATE_KEY`
- `JWT_PUBLIC_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `RESEND_API_KEY`
- `GEMINI_API_KEY`

Observacoes:

- `POSTGRES_PASSWORD` pode ser omitido e herdara `DB_PASSWORD`
- `CLOUDINARY_URL` pode ser omitido e sera derivado das credenciais Cloudinary
- planejamento de rotacao/verificacao passa por `bash scripts/ops/rotate_keys.sh --secret <NAME> --environment <staging|production> --format json`

## 7. Primeiro deploy manual

```bash
su - hbtrack
cd /opt/hbtrack/staging
git clone https://github.com/hbtrack/official.git .
export HB_ENV_SECRET_KEY='...'
export HB_ENV_DB_PASSWORD='...'
export HB_ENV_JWT_PRIVATE_KEY='...'
export HB_ENV_JWT_PUBLIC_KEY='...'
export HB_ENV_CLOUDINARY_CLOUD_NAME='...'
export HB_ENV_CLOUDINARY_API_KEY='...'
export HB_ENV_CLOUDINARY_API_SECRET='...'
export HB_ENV_RESEND_API_KEY='...'
export HB_ENV_GEMINI_API_KEY='...'
bash scripts/deploy/inject_env.sh staging /opt/hbtrack/staging/.env latest
docker compose -f infra/docker-compose.prod.yml pull
docker compose -f infra/docker-compose.prod.yml up -d
docker compose -f infra/docker-compose.prod.yml ps
curl https://staging.handballtrack.app/health
```

## 8. Pact Broker (CDCT — ADR-025)

Provisionar apos os servicos principais de staging e production:

```bash
mkdir -p /opt/hbtrack/pact-broker
# copiar infra/docker-compose.pact-broker.yml para /opt/hbtrack/pact-broker/docker-compose.yml
# criar /opt/hbtrack/pact-broker/.env com PACT_BROKER_DB_PASSWORD, PACT_BROKER_BASIC_AUTH_PASSWORD
cd /opt/hbtrack/pact-broker
docker compose up -d
curl http://localhost:9292/diagnostic/status/heartbeat
```

Configurar no GitHub Actions (repository variable):
- `PACT_BROKER_BASE_URL` = `http://<VPS_IP>:9292`
- `PACT_BROKER_TOKEN` (secret) = credencial de acesso ao broker

## 9. Checklist de prontidao

- [ ] Docker e Compose instalados
- [ ] Certbot funcional
- [ ] usuario `hbtrack` com acesso ao Docker
- [ ] diretorios `/opt/hbtrack/staging`, `/opt/hbtrack/production` e `/opt/hbtrack/pact-broker` criados
- [ ] secrets e variables do GitHub configurados (incluindo `PACT_BROKER_BASE_URL`)
- [ ] `.env` renderizado por ambiente com os valores do catalogo
- [ ] health endpoint responde conforme `docs/_canon/graph/ops/runtime_endpoints.yaml`
- [ ] Pact Broker acessivel em `http://<VPS_IP>:9292/diagnostic/status/heartbeat`
