---
data_ultima_sessao: "2026-04-22"
branch_ativo: refactor/training-decomposition
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: training
fase_roadmap: 6
roadmap_phase: 6
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: ROADMAP-TIER3-TRAINING-DECOMPOSITION
resultado: DONE
proxima_acao_permitida: "push branch + abrir PR refactor/training-decomposition → main"
bloqueios_ativos: []
evidence_paths:
  - "_reports/contract_gates/precommit.latest.json"
  - "contracts/_waivers/PACT_PROVIDER_GATE_TRAINING_20260422.json"
  - "docs/_canon/decisions/ADR-035-session-access-policy.md"
  - "src/training/migrations/0007_training_session_execution_fields.py"
---
# SESSION HANDOFF — HB TRACK

## O que foi feito

**Sessão 2026-04-22 — Tier 1/2/3 (pós Fase 6)**

Fases 0–6 + Tier 1 Adversarial + Tier 2 + Tier 3 concluídos (ver `.dev/decisões/rafatora_training.md` §6/§7/§8).

**Tier 1 — Adversarial bug fixes (e560168f):**
- Migration `0007` + 12 campos ORM/repo (V1 — perda silenciosa de dados)
- `CursorCodec` dual-key `TRAINING_CURSOR_SECRETS` CSV (V2 — cliff failure em rotação)
- Q filter tie-break `(session_at, id)` + índice (V12 — duplicação com timestamps iguais)
- Guard duplo ENV=production em `get_cursor_codec()` (V9)
- IntegrityError/DataError retornam mensagem genérica (V10 — leak de schema)
- `test_all_training_domain_errors_have_mapping` recursivo (V5)

**Tier 2 — N+1 housekeeping:**
- N2.1: `DeprecationWarning` via `__getattr__` em 5 shims + `warnings.warn` em `use_cases.py`
- N2.2: `TrainingServices` singleton via `__new__`
- N2.3: waiver `PACT_PROVIDER_GATE_TRAINING_20260422.json` + `merge-readiness.json`
- N2.4: `ADR-035-session-access-policy.md` (OWASP API1+API5)

**Tier 3 — N+2 housekeeping:**
- N3.1: `configure_for_testing`/`reset_testing_overrides`/`_resolve` em `TrainingServices` + 6 testes
- N3.2: comentário 4-linhas nos imports `_gen_*` em `api/__init__.py`
- N3.4: `VPS/runbooks/TRAINING_V1_DATA_RECOVERY.md`
- N3.3/N3.5: BLOQUEADOS (aguardam PR merge + 2 releases em produção)

**Testes**: 394 passed, 19 skipped

## Estado Geral

| Fase | Status |
|---|---|
| 0–5 (decomposição completa) | ✅ CONCLUÍDAS |
| 6.1 source graph sync | ✅ CONCLUÍDA |
| 6.2 commit + PR | ⏳ |

## Evidências

- `hb verify --roadmap-phase 5` → PASS
- Source graph: 11/11 testes PASS
- Context bundle: 5/5 testes PASS
- Último commit Fase 5: `fe2e3aa0`

## Bloqueios ativos

Nenhum.

## Próxima ação permitida

Commit Fase 6 + abrir PR com: decomposição de arquivos, surface pública preservada,
shims ativos, TODO remoção shims N+1.

## Próxima Sessão

Aderir aos critérios de done da Fase 6.
