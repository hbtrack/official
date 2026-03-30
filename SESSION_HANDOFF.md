---
data_ultima_sessao: "2026-03-27"
branch_ativo: docs/infra-deploy-checklist
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: training
fase_roadmap: 4
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: roadmap-fase4-staging-validation
resultado: PENDENTE
proxima_acao_permitida: "Abrir PR com fixes de auth + HTTP_RUNTIME_CONTRACT_GATE → CI verde → merge → staging valida contratos automaticamente."
bloqueios_ativos: []
evidence_paths:
  - ROADMAP.md
  - .github/workflows/deploy.yml
  - scripts/contracts/validate/validate_contracts.py
---
# SESSION HANDOFF — HB TRACK
> Delta-only. Histórico em `_archive/SESSION_HANDOFF_PRE_FASE0_20260323.md`

## Estado Geral
**Data:** 2026-03-27 | **Branch:** fix/seed-training-session-created-by | **CI:** UNKNOWN
**Modo:** ROADMAP | **Fase ROADMAP:** 4 | **Resultado:** PENDENTE

## O que foi feito
HTTP_RUNTIME_CONTRACT_GATE ativado: `validate_contracts.py` agora executa Schemathesis CLI contra staging quando `HB_STAGING_URL` está definida. Job `contract-conformance` adicionado ao `deploy.yml` (ETAPA 5) após `deploy-staging`, antes da aprovação humana. Bugs de auth corrigidos por drift código-contrato: `training/api.py` (`_get_actor_id` retornava `uuid4()` → agora lança 401), `teams/api.py` e `seasons/api.py` (`_get_actor_role` defaultava para `"admin"` → agora lança 401). Contratos já declaravam `HTTPBearer` corretamente — problema era código sem enforcement.

## Evidências
- `scripts/contracts/validate/validate_contracts.py`: `_g11_http_runtime_contract` ativado
- `.github/workflows/deploy.yml`: job `contract-conformance` (ETAPA 5) adicionado
- `src/training/api.py`: `_get_actor_id` corrigido
- `src/teams/api.py`: `_get_actor_role` corrigido
- `src/seasons/api.py`: `_get_actor_role` corrigido

## Próxima ação permitida
Abrir PR → CI verde → merge → deploy staging → `contract-conformance` gate valida que API responde 401 sem token.

## Bloqueios ativos
- `BLOCKED_DEPLOY_REQUIRES_HUMAN` — VPS Locaweb (FASE 4 validação staging)
