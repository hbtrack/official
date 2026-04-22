---
data_ultima_sessao: "2026-04-22"
branch_ativo: docs/codegen-canonization
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: infra
fase_roadmap: 6
roadmap_phase: 6
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: ROADMAP-FASE6-EDGE-PROXY
resultado: PENDENTE
proxima_acao_permitida: "fazer commit/push da branch com os novos artefatos de infra; depois executar migração manual no VPS (parar nginx legado, criar redes, rodar deploy-edge)"
bloqueios_ativos: []
evidence_paths:
  - "infra/docker-compose.edge.yml"
  - "infra/docker-compose.staging.yml"
  - "infra/docker-compose.prod.yml"
  - "infra/nginx/nginx.edge.conf"
  - "infra/nginx/nginx.edge.bootstrap.conf"
  - ".github/workflows/deploy.yml"
---
# SESSION HANDOFF — HB TRACK

## O que foi feito

**Sessão 2026-04-23 — Arquitetura Edge Proxy (resolve BLOCKED_SHARED_EDGE_HOST)**

Implementada a arquitetura de proxy único de borda que elimina o conflito staging/produção nas portas 80/443 do mesmo VPS.

### Artefatos criados/modificados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `infra/docker-compose.edge.yml` | NOVO | Stack edge: nginx:1.27-alpine + certbot nas portas 80/443 |
| `infra/nginx/nginx.edge.conf` | NOVO | Config completa: 3 vhosts, upstreams por alias de rede, SSL |
| `infra/nginx/nginx.edge.bootstrap.conf` | NOVO | Config bootstrap (sem SSL) para emissão inicial de certs ACME |
| `infra/docker-compose.staging.yml` | NOVO | Stack staging: sem nginx, sem portas públicas, rede `hbtrack-staging-net` |
| `infra/docker-compose.prod.yml` | MODIFICADO | Removidos nginx/certbot; rede renomeada para `hbtrack-prod-net`; aliases `prod-api`/`prod-frontend` |
| `.github/workflows/deploy.yml` | MODIFICADO | Jobs `deploy-staging` e `deploy-production` simplificados; job `deploy-edge` (etapa 8) adicionado |

### Arquitetura implementada

```
Internet → 80/443
  └── nginx edge (hbtrack-edge stack)
        ├── handballtrack.app / www → prod-frontend:80, prod-api:8000
        └── staging.handballtrack.app → staging-frontend:80, staging-api:8000

Redes internas (sem portas públicas):
  hbtrack-prod-net    → production stack
  hbtrack-staging-net → staging stack
```

### Funcionamento do deploy-edge (CI)

1. Copia `infra/` para `/opt/hbtrack/edge` no VPS
2. Cria redes Docker se ausentes (idempotente)
3. Migra certs do volume legado `hbtrack-production_certbot_conf` → `hbtrack-edge_certbot_conf` (uma vez)
4. Para nginx legado que ocupe 80/443 (se existir)
5. Verifica quais certs existem; emite os ausentes via certbot standalone
6. Sobe edge com `nginx.edge.conf` (SSL completo) ou `nginx.edge.bootstrap.conf` (aguardando DNS)

## Estado Geral

| Item | Status |
|---|---|
| Artefatos de infra criados | ✅ COMPLETO |
| deploy.yml atualizado (8 etapas) | ✅ COMPLETO |
| Commit/push na branch | ⏳ PENDENTE (humano) |
| Migração manual no VPS | ⏳ PENDENTE (humano) |
| Staging cert (staging.handballtrack.app) | ⏳ aguarda DNS + deploy-edge |
| BLOCKED_SHARED_EDGE_HOST | ✅ RESOLVIDO (arquitetura) |

## Próxima ação permitida

1. **Commit e push** dos artefatos criados (todos os arquivos modificados acima)
2. **No VPS** — executar uma vez manualmente ou via primeiro deploy-edge do CI:
   - Os containers de nginx da produção antiga serão parados automaticamente pelo script
   - `docker network create hbtrack-prod-net` (se ainda não existir)
   - `docker network create hbtrack-staging-net` (se ainda não existir)
3. Verificar HTTPS nos 3 hostnames após deploy

## Evidências

- `infra/docker-compose.edge.yml` — stack edge criada (nginx:1.27-alpine + certbot, ports 80/443)
- `infra/nginx/nginx.edge.conf` — roteamento multi-vhost completo com TLS
- `infra/nginx/nginx.edge.bootstrap.conf` — config bootstrap HTTP-only para emissão de certs
- `infra/docker-compose.staging.yml` — stack staging sem nginx, rede hbtrack-staging-net
- `infra/docker-compose.prod.yml` — nginx/certbot removidos, rede → hbtrack-prod-net, aliases adicionados
- `.github/workflows/deploy.yml` — job `deploy-edge` (etapa 8) adicionado na linha 681

## Bloqueios ativos

Nenhum bloqueio técnico. Migração no VPS requer ação humana.

## Próxima Sessão

1. Confirmar resultado do Deploy Pipeline (run em `main` após `cdfe57bc`)
2. Se staging OK: marcar Fase 6.2 como DONE no ROADMAP
3. Criar issue GitHub: `test_list_training_sessions_response_time` — falha pré-existente
4. Migrar imports em `src/training/api/` de shims legados para paths canônicos (109 DeprecationWarnings)
