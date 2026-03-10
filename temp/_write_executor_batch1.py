content = """

---

## EXECUTOR REPORT — Batch 1 TRAINING (AR_175 / AR_176)

RUN_ID: BATCH1-TRAINING-AR175-AR176-20260228
DATA: 2026-02-28
PROTOCOLO: 1.3.0

=== AR_175 — EXECUTADO ===

**AR**: AR_175_fix_step18_services_training_alerts_service.py_+_t.md
**Status**: EXECUTADO (exit_code=0)
**Objetivo**: Fix training_alerts_service.py + training_suggestion_service.py para UUID
**validation_command**: cd "Hb Track - Backend" && python -m pytest -q tests/training/invariants/test_inv_train_023_wellness_post_overload_alert_trigger.py 2>&1
**Exit Code**: 0
**Behavior Hash**: 9264c23511d2ba5038edcb6b7c9091480db4e70e7d8ee38be481449d1b3dc23c
**Evidence**: docs/hbtrack/evidence/AR_175/executor_main.log

**Patch aplicado** (write_scope: training_suggestion_service.py):
- generate_compensation_suggestion: session_id: int -> UUID (tipo correto)
- TrainingSession.session_date -> session_at (campo correto do modelo)
- origin_session.session_date -> origin_session.session_at
- TrainingSession.is_locked == False -> status != "readonly" (campo correto)
- generate_reduction_suggestion: mesmas correcoes session_date -> session_at e is_locked -> status

**training_alerts_service.py**: sem alteracao (ja usava UUID corretamente em todos os metodos)

**Staged**:
- A docs/hbtrack/evidence/AR_175/executor_main.log
- M docs/hbtrack/ars/features/AR_175_fix_step18_services_training_alerts_service.py_+_t.md
- M Hb Track - Backend/app/services/training_suggestion_service.py

=== AR_176 — BLOQUEADO (exit 4) ===

**AR**: AR_176_fix_wellness_be_self-only_athlete_id_do_jwt_+_payl.md
**Status**: BLOQUEADO (BLOCKED_INPUT)
**motivo**: BUG NO ARQUIVO DE TESTE fora do write_scope

**Diagnostico**:
test_inv_train_026_lgpd_access_logging.py usa caminho incorreto:
  Path(__file__).parent.parent.parent / "app" / "services"
  => resolve para: tests/app/services/ (ERRADO)
  => deveria ser: Path(__file__).parent.parent.parent.parent / "app" / "services"
  => resultado correto: Hb Track - Backend/app/services/

Os 6 testes de INV-TRAIN-026 falham com AssertionError/FileNotFoundError porque
buscam arquivos em tests/app/services/ e tests/app/models/ que nao existem.

Nenhuma alteracao em wellness_pre_service.py ou wellness_post_service.py consegue
fazer esses testes passarem enquanto o path estiver errado.

test_inv_train_002 e test_inv_train_003 (8 testes): PASSAM sem alteracoes.

**Alternissima necessaria (Arquiteto)**:
1. Corrigir test_inv_train_026_lgpd_access_logging.py — substituir TODAS as 6
   ocorrencias de .parent.parent.parent por .parent.parent.parent.parent.
2. Verificar se outros arquivos de invariante tem o mesmo bug.
3. Retornar AR_176 para Executor com write_scope atualizado (incluir test file OU
   criar nova AR de fix-test separada).

**Staged AR_176**: Analise de Impacto escrita na AR (nao staged, aguardando decisao Arquiteto)

=== STAGING FINAL ===
git diff --name-only = VAZIO (tracked-unstaged limpo)
Restantes staged (from Batch 1 Arquiteto):
  A  docs/_canon/planos/ar_train_002_step18_services.json
  A  docs/_canon/planos/ar_train_004_wellness_backend.json
  M  docs/hbtrack/Hb Track Kanban.md
  M  docs/hbtrack/_INDEX.md
  A  docs/hbtrack/ars/features/AR_175_fix_step18_services_training_alerts_service.py_+_t.md
  A  docs/hbtrack/ars/features/AR_176_fix_wellness_be_self-only_athlete_id_do_jwt_+_payl.md

Staged por AR_175 execution:
  M  docs/hbtrack/ars/features/AR_175_fix_step18_services_training_alerts_service.py_+_t.md (UPDATED - Analise Impacto + Carimbo)
  A  docs/hbtrack/evidence/AR_175/executor_main.log
  M  Hb Track - Backend/app/services/training_suggestion_service.py

=== PROXIMOS PASSOS ===
1. Testador: executar hb verify para AR_175 (exit_code=0, evidence exists)
2. Arquiteto: corrigir bug de path em test_inv_train_026, liberar AR_176
"""

with open('_reports/EXECUTOR.yaml', 'a', encoding='utf-8') as f:
    f.write(content)

print('EXECUTOR.yaml updated')
