---
data_ultima_sessao: "2026-03-27"
branch_ativo: fix/schemathesis-timeout
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: training
fase_roadmap: 4
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: roadmap-fase4-staging-validation
resultado: DONE
proxima_acao_permitida: "Rodar testes de integração com Schemathesis em staging → CI verde → merge → deploy."
bloqueios_ativos: []
evidence_paths:
  - ROADMAP.md
  - .github/workflows/deploy.yml
  - scripts/contracts/validate/validate_contracts.py
---
# SESSION HANDOFF — HB TRACK
> Delta-only. Histórico em `_archive/SESSION_HANDOFF_PRE_FASE0_20260323.md`

## Estado Geral
**Data:** 2026-03-27 | **Branch:** docs/infra-deploy-checklist | **CI:** UNKNOWN
**Modo:** ROADMAP | **Fase ROADMAP:** 4 | **Resultado:** CONCLUÍDO (auth enforcement)

## O que foi feito nesta sessão

### Auditoria de conformidade
Auditoria completa do projeto identificou vulnerabilidade crítica: **13 de 17 módulos** tinham auth stubs que aceitavam requisições anônimas (retornavam `uuid4()`, `RoleLabel.MEMBER`, ou defaults como `"admin"`/`"member"` em vez de lançar 401).

### Correção sistemática de auth — 13 módulos corrigidos
Todos os helpers `_get_role`/`_get_actor_id`/`_role`/`_uid` foram reescritos para seguir o padrão de referência (teams/seasons): verificar `request._actor_role` / `request._actor_id` (populados pelo `JWTClaimsMiddleware`), lançar `HttpError(401, "Unauthenticated")` se ausentes.

**Módulos corrigidos:**
- `src/training/api.py` — `_get_actor_role` (defaultava "admin")
- `src/matches/api.py` — `_role()` e `_actor_id()` (usavam `request.auth`)
- `src/medical/api.py` — `_role()` e `_actor_id()` (usavam `request.auth`, crítico para LGPD)
- `src/wellness/api.py` — `_role()` e `_actor_id()` (usavam `request.auth`)
- `src/scout/api.py` — `_get_role()` e `_get_actor_id()` + import HttpError
- `src/competitions/api.py` — `_role()` + import HttpError
- `src/analytics/api.py` — `_role()` e `_uid()` + import HttpError
- `src/exercises/api.py` — `_get_role()` e `_get_actor_id()` + import HttpError
- `src/reports/api.py` — `_role()` e `_uid()` + import HttpError
- `src/video/api.py` — adicionado `_get_actor_id()` helper, substituídos 3 inline `uuid4()`
- `src/audit/api.py` — `_get_role()` + import HttpError
- `src/notifications/api.py` — `_get_role()` e `_get_user_id()` + import HttpError
- `src/ai_ingestion/api.py` — `_get_role()` + import HttpError

**Módulos já corretos (sem alteração):** teams, seasons, users, identity_access

### Validação
- **393 testes passando**, 0 falhas (excluindo 2 problemas pré-existentes: schemathesis `django_db` marker, `TestStage23ExitCodes` hang)
- Zero stubs de auth restantes: grep por `uuid4()`, `"admin"`, `"member"`, `request.auth` em `src/*/api.py` retorna vazio

## Evidências
- `.CEPRAEA/RELATÓRIO.md` — relatório completo da auditoria
- `src/*/api.py` (13 módulos) — auth enforcement corrigido
- 393 testes passam sem falha

## Próxima ação permitida
1. Commit das alterações de auth
2. Rodar Schemathesis em staging para validar que API rejeita 401 sem token
3. Prosseguir com FASE 4 restante (RBAC testing, contract conformance)

## Bloqueios ativos
- `BLOCKED_DEPLOY_REQUIRES_HUMAN` — VPS Locaweb (FASE 4 validação staging)

## Problemas pré-existentes (não relacionados a esta sessão)
- `tests/schemathesis/test_ciclo1_contracts.py` — falta `django_db` marker
- `tests/pipeline_gates/test_session_state_phase3.py::TestStage23ExitCodes` — trava (subprocesso bloqueante)
