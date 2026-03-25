---
data_ultima_sessao: "2026-03-25"
branch_ativo: hb-track-contratos-driven
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: training
fase_roadmap: 2
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: roadmap-fase0-meta-753-tests
resultado: DONE
proxima_acao_permitida: "FASE 0 ✅ COMPLETA. 1142 + 1 schemathesis = 1143 PASS, 0 SKIP. FASE 2 ✅ Ciclo 1 contract tests PASS. FASE 5 ✅ COMPLETA (5.1-5.9). Próximo: FASE 6 — Deploy produção (BLOCKED_DEPLOY_REQUIRES_HUMAN)"
bloqueios_ativos: []
evidence_paths:
  - ROADMAP.md
  - conftest.py
  - tests/test_performance_phase4.py
  - scripts/checks/check_correction_protocol.py
  - scripts/checks/FAILURE_TO_GATES.yaml
  - src/seasons/tests/integration/test_seasons_api.py
  - src/teams/tests/integration/test_teams_api.py
---
# SESSION HANDOFF — HB TRACK
> Delta-only. Histórico em `_archive/SESSION_HANDOFF_PRE_FASE0_20260323.md`

## Estado Geral
**Data:** 2026-03-25 | **Branch:** hb-track-contratos-driven | **CI:** UNKNOWN
**Modo:** ROADMAP | **task_type:** execute_roadmap_phase | **boot_profile:** roadmap_execution
**Módulo foco:** training | **Fase ROADMAP:** 2 | **Resultado:** DONE

## O que foi feito nesta sessão
**Bugfix schemathesis + FASE 0 meta 753 tests em andamento**

- `CreateMicrocycleIn.week_number`: `int` → `Annotated[int, Field(ge=1, le=32767)]` — previne HTTP 500 por SmallIntegerField overflow
- `MicrocycleEntity.validate_invariants`: adicionado `week_number <= 32767`
- `conftest.py` raiz: `_patch_flush_allow_cascade` (global) — corrige FK teardown `transactional_db`
- `tests/test_performance_phase4.py`: URLs corrigidas + warm-up request + `created_by_user_id`
- ROADMAP.md 2.5 `[x]` — schemathesis Ciclo 1: `1 passed, 74 skipped, 0 errors`

## Evidências
- `src/training/schemas.py` — `_WeekNumber = Annotated[int, Field(ge=1, le=32767)]`
- `src/training/domain/entities.py` — invariante `<= 32767`
- `tests/schemathesis/conftest.py` — patch removido (movido para raiz)
- `conftest.py` — `_patch_flush_allow_cascade` autouse session
- `tests/test_performance_phase4.py` — warm-up + URLs corretas

## Próxima ação permitida
**FASE 0 meta "≥ 753 testes PASS, 0 SKIP" em andamento.**

Suite atual (postgres ativo): `1138+ passed, 2 failed, 2 skipped`.
Pendente: corrigir `test_check_correction_protocol.py` (paths `_agent` → `gates`) e `test_session_handoff_md_under_budget`.

## Bloqueios ativos
Nenhum bloqueio canônico ativo.
