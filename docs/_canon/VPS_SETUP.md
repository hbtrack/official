# HB Track — VPS Setup (Staging e Production)

> Documento operacional para provisionamento manual do servidor.
> Requer aprovação humana antes de executar em produção (BLOCKED_DEPLOY_REQUIRES_HUMAN).

## Pré-requisitos

- Ubuntu 22.04 LTS (64-bit)
- Mínimo: 2 vCPU, 4 GB RAM, 40 GB SSD
- Acesso SSH como root na primeira configuração

---

## 1. Usuário e permissões

```bash
# Criar usuário sem sudo para rodar a aplicação
useradd -m -s /bin/bash hbtrack
usermod -aG docker hbtrack

# Diretórios de deploy
mkdir -p /opt/hbtrack/staging /opt/hbtrack/production
chown -R hbtrack:hbtrack /opt/hbtrack
```

---

## 2. Docker Engine + Compose v2

```bash
# Instalar Docker via script oficial
curl -fsSL https://get.docker.com | sh

# Verificar
docker --version          # >= 24.x
docker compose version    # >= 2.x
```

---

## 3. Certbot (Let's Encrypt)

```bash
apt-get install -y certbot
# Gerar certificado (substituir handballtrack.app)
certbot certonly --standalone -d handballtrack.app --non-interactive --agree-tos -m admin@handballtrack.app

# Renovação automática (já incluída na instalação do certbot)
systemctl status certbot.timer
```

---

## 4. Firewall (UFW)

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (redirect para HTTPS)
ufw allow 443/tcp   # HTTPS
ufw enable
ufw status
```

---

## 5. SSH key para GitHub Actions

No servidor (como root):
```bash
# Gerar par de chaves dedicado para CI/CD
ssh-keygen -t ed25519 -C "github-actions-hbtrack" -f /root/.ssh/hbtrack_deploy -N ""
cat /root/.ssh/hbtrack_deploy.pub >> /home/hbtrack/.ssh/authorized_keys
chmod 700 /home/hbtrack/.ssh
chmod 600 /home/hbtrack/.ssh/authorized_keys

# Exibir chave privada para copiar para o secret do GitHub
cat /root/.ssh/hbtrack_deploy
```

No repositório GitHub, adicionar os secrets:
| Secret | Valor |
|--------|-------|
| `VPS_SSH_KEY` | Conteúdo da chave privada acima |
| `VPS_HOST_STAGING` | IP ou hostname do servidor staging |
| `VPS_HOST_PRODUCTION` | IP ou hostname do servidor production |
| `VPS_USER` | `hbtrack` |

---

## 6. Repositório e arquivos no servidor

```bash
# Como usuário hbtrack
su - hbtrack
cd /opt/hbtrack/staging  # ou /production

# Clonar repositório
git clone https://github.com/hbtrack/official.git .

# Criar .env a partir do template
cp infra/env/.env.staging.template .env
# Editar .env e preencher todos os CHANGE_ME_* com valores reais
nano .env
```

---

## 7. Primeiro deploy manual

```bash
cd /opt/hbtrack/staging

# Logar no GitHub Container Registry
echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u GITHUB_USER --password-stdin

# Subir os serviços
docker compose -f infra/docker-compose.prod.yml pull
docker compose -f infra/docker-compose.prod.yml up -d

# Verificar
docker compose -f infra/docker-compose.prod.yml ps
curl http://localhost:8000/health
```

---

## 8. Variáveis de ambiente do GitHub Actions

Adicionar como **Variables** (não secrets — não são sensíveis):
| Variable | Exemplo |
|----------|---------|
| `STAGING_URL` | `https://staging.hbtrack.app` |
| `PRODUCTION_URL` | `https://api.hbtrack.app` |

---

## Checklist de prontidão

- [ ] Docker Engine >= 24 instalado
- [ ] Compose v2 instalado
- [ ] Certbot configurado e certificado gerado
- [ ] Usuário `hbtrack` criado com permissão Docker
- [ ] `/opt/hbtrack/staging/` e `/opt/hbtrack/production/` criados
- [ ] `.env` preenchido em cada ambiente (sem CHANGE_ME_*)
- [ ] SSH key adicionada aos secrets do GitHub
- [ ] Firewall UFW ativo (22, 80, 443)
- [ ] Health check responde: `curl https://handballtrack.app/health`
