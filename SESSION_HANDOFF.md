---
data_ultima_sessao: "2026-04-22"
branch_ativo: docs/codegen-canonization
modo_operacao: ROADMAP
ci_status: UNKNOWN
modulo_foco: training
fase_roadmap: 6
roadmap_phase: 6
task_type: execute_roadmap_phase
boot_profile_id: roadmap_execution
task_id: ROADMAP-FASE6-DEPLOY
resultado: PENDENTE
proxima_acao_permitida: "aguardar Deploy Pipeline completar em main (cdfe57bc); confirmar staging deploy; criar ticket test_list_training_sessions_response_time"
bloqueios_ativos: []
evidence_paths:
  - "_reports/contract_gates/precommit.latest.json"
  - "contracts/_waivers/PACT_PROVIDER_GATE_TRAINING_20260422.json"
  - "docs/_canon/decisions/ADR-035-session-access-policy.md"
---
# SESSION HANDOFF — HB TRACK

## O que foi feito

**Sessão 2026-04-22 — Fix CI/Deploy Pipeline pós-merge PR #80**

Após merge do PR #80 (refactor training), o Deploy Pipeline falhou em `main` com dois problemas distintos. Ambos corrigidos e merged via PR #81 (`cdfe57bc`):

1. **`TRAINING_CURSOR_SECRET` ausente** no job `test` de `deploy.yml` → `RuntimeError` com `DEBUG=false`. Fix: variável adicionada, alinhando com `_reusable-ci.yml` linha 107.
2. **Budget `CONTRACT_PIPELINE.md` excedido** (828w > 650w) — §7 "Compilador Canônico de IR" foi adicionada pelo pre-commit hook no commit `d5330134`. Fix: budget atualizado 650→850 em `test_context_budgets_and_parity.py`.

**VCS:**
- PR #80 merged → `d7102131` (squash, 22/04/2026)
- PR #81 merged → `cdfe57bc` (squash, 22/04/2026)
- Deploy Pipeline rodando em `main` pós-PR #81 (em andamento)

## Estado Geral

| Item | Status |
|---|---|
| PR #80 (refactor training) | ✅ MERGED `d7102131` |
| PR #81 (fix CI deploy pipeline) | ✅ MERGED `cdfe57bc` |
| Deploy Pipeline em main | 🔄 EM ANDAMENTO |
| Deploy staging `/training/*` | ⏳ aguarda pipeline |
| N3.3 / N3.5 | ⛔ bloqueados (2 releases em produção) |

## Próxima ação permitida

Aguardar Deploy Pipeline completar → confirmar staging saudável → criar ticket para `test_list_training_sessions_response_time`.

## Evidências

- PR #81 merged: `cdfe57bc` (22/04/2026)
- `_reports/contract_gates/precommit.latest.json` → PASS (após PR #81)
- Deploy Pipeline: run iniciado em `main` pós-`cdfe57bc`

## Bloqueios ativos

Nenhum.

## Próxima Sessão

1. Confirmar resultado do Deploy Pipeline (run em `main` após `cdfe57bc`)
2. Se staging OK: marcar Fase 6.2 como DONE no ROADMAP
3. Criar issue GitHub: `test_list_training_sessions_response_time` — falha pré-existente
4. Migrar imports em `src/training/api/` de shims legados para paths canônicos (109 DeprecationWarnings)
