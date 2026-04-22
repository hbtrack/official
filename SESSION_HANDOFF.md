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
proxima_acao_permitida: "aguardar CI verde no PR #83; aprovar merge; verificar deploy-edge no VPS"
bloqueios_ativos: []
evidence_paths:
  - "infra/docker-compose.edge.yml"
  - "infra/docker-compose.prod.yml"
  - ".github/workflows/deploy.yml"
---
# SESSION HANDOFF — HB TRACK

## O que foi feito

Fase 6 — Edge Proxy (resolve BLOCKED_SHARED_EDGE_HOST):
- `infra/docker-compose.edge.yml` — nginx:1.27-alpine + certbot, portas 80/443
- `infra/nginx/nginx.edge.conf` — 3 vhosts SSL; `nginx.edge.bootstrap.conf` — bootstrap HTTP
- `infra/docker-compose.staging.yml` — staging sem nginx, rede `hbtrack-staging-net`
- `infra/docker-compose.prod.yml` — nginx/certbot removidos, rede → `hbtrack-prod-net`
- `deploy.yml` — health check interno (docker exec), certbot --webroot, job deploy-edge

CI fixes (branch `docs/codegen-canonization`, HEAD `c47b05e5`):
- `scripts/hbtrack_lint/` (25 arquivos) restaurados — deletados por acidente em merge
- `src/shared/middleware.py` — `_UUID4_RE` sanitiza X-Flow-ID, previne log injection (F10)
- `tests/test_fase1_validation.py` — `test_flow_id_propagated` usa UUID v4 válido

## Estado Geral

| Item | Status |
|---|---|
| Artefatos edge + deploy.yml | ✅ commitados |
| CI failures resolvidas (3 → 2) | ✅ `c47b05e5` |
| PR #83 mergeable | ✅ |
| Merge PR #83 | ⏳ aprovação humana |
| Deploy-edge VPS | ⏳ após merge |

## Próxima ação permitida

1. CI verde → aprovar merge do PR #83
2. Verificar deploy-staging → deploy-production → deploy-edge no VPS
3. Migrar imports em `src/training/api/` para paths canônicos (33 DeprecationWarnings)

## Bloqueios ativos

Nenhum.

## Evidências

- `infra/docker-compose.edge.yml`, `nginx.edge.conf`, `nginx.edge.bootstrap.conf`
- `infra/docker-compose.staging.yml`, `infra/docker-compose.prod.yml`
- `.github/workflows/deploy.yml` — health check interno + certbot --webroot + deploy-edge
- `scripts/hbtrack_lint/` (25 arquivos restaurados)
- `src/shared/middleware.py` — _UUID4_RE sanitização F10

## Falhas pré-existentes (não bloquear merge)

- `test_session_handoff_md_under_budget` — resolvido por este handoff
- `test_all_budgets_combined` — resolvido por este handoff
- `test_list_training_sessions_response_time` — `TRAINING_CURSOR_SECRET` ausente no CI

## Próxima sessão

1. CI verde → aprovar merge do PR #83
2. Verificar deploy automático após merge (staging → production → edge)
