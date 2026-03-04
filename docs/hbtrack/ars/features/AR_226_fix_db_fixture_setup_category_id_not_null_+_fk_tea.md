# AR_226 — Fix DB fixture setup: category_id NOT NULL + FK team_registrations (~57+ ERROs)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir fixtures de setup de banco que falham com:
1. `asyncpg.exceptions.NotNullViolationError: null value in column 'category_id'` — a fixture cria exercício sem passar category_id (obrigatório após migração).
2. `asyncpg.exceptions.ForeignKeyViolationError: insert or update on table 'team_registrations' violates foreign key constraint 'fk_team_registrations_athlete_id'` — a fixture cria team_registration antes de criar o athlete.

Arquivos afetados (ERRORs at setup):
- test_inv_train_011_deviation_rules.py
- test_inv_train_013_gamification_badge_rules.py
- test_inv_train_020_cache_invalidation_trigger.py
- test_inv_train_021_internal_load_trigger.py
- test_inv_train_028_focus_sum_constraint.py
- test_inv_train_029_edit_blocked_after_in_progress.py
- test_inv_train_050_exercise_favorites_unique.py
- test_inv_train_052_exercise_media.py
- test_inv_train_058_session_structure_mutable.py
- test_inv_train_059_exercise_order_contiguous.py
- test_inv_train_063_*.py
- test_inv_train_064_*.py
- test_inv_train_065_close_pending_guard.py
- test_inv_train_066_pending_items.py
- test_inv_train_076_*.py
- test_inv_train_148_exercise_bank_services.py
- test_inv_train_exb_acl_006_*.py

FIX TIPO 1 (category_id): nas fixtures que criam exercício via INSERT direto ou factory, adicionar category_id com um valor válido (criar categoria de teste se necessário, ou usar fixture compartilhada de conftest).

FIX TIPO 2 (FK team_registrations): ajustar ordem de criação — athlete DEVE existir antes de team_registration. Se a fixture está usando IDs hardcoded que não existem, criar os registros dependentes ou usar um athlete_id de fixture existente.

Verificar se conftest.py do diretório tests/training/ já expõe fixture de exercício ou categoria — se sim, reaproveitar ao invés de criar novo.

Não alterar nada em app/ nem schema de DB.

## Critérios de Aceite
AC-001: pytest nos arquivos test_inv_train_011/013/020/021/028/029 = 0 FAILs, 0 ERRORs.
AC-002: pytest nos arquivos test_inv_train_050/052/058/059/063/064/065/066/076/148/exb_acl_006 = 0 FAILs, 0 ERRORs.
AC-003: nenhum ERROR 'NotNullViolationError' ou 'ForeignKeyViolationError' nos arquivos listados.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_011_deviation_rules.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_013_gamification_badge_rules.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_021_internal_load_trigger.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_028_focus_sum_constraint.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_029_edit_blocked_after_in_progress.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_052_exercise_media.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_058_session_structure_mutable.py
- Hb Track - Backend/tests/training/invariants/

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_011_deviation_rules.py tests/training/invariants/test_inv_train_013_gamification_badge_rules.py tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py tests/training/invariants/test_inv_train_021_internal_load_trigger.py tests/training/invariants/test_inv_train_028_focus_sum_constraint.py tests/training/invariants/test_inv_train_029_edit_blocked_after_in_progress.py tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py tests/training/invariants/test_inv_train_052_exercise_media.py tests/training/invariants/test_inv_train_148_exercise_bank_services.py -q --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_226/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py plan docs/_canon/planos/ar_batch18_fix_test_layer_044_047.json --dry-run
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- category_id pode ser FK para outra tabela — verificar schema.sql antes de criar a fixture de categoria.
- FK team_registrations pode exigir criação de múltiplas entidades (org → team → athlete) — manter ordem topológica.
- Se conftest.py de nível superior já tem fixture de exercício, extender ao invés de duplicar.

## Análise de Impacto
Root causes reais (descobertos na execução):

1. test_029: path `.parent.parent.parent / "app"` aponta para `tests/app/` (errado). Fix: adicionar mais um `.parent`.

2. test_050, test_052, test_148: `TypeError: function() missing required argument 'globals' (pos 2)` causado por `uuid4.__class__(exercise_id)` nas fixtures. `uuid4.__class__` é `types.FunctionType`, que exige 2 args. Fix: substituir por `exercise_id` (string).

3. test_011/013/020/021/028: já passam — sem mudanças necessárias.

Sem mudanças em app/ nem schema.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_011_deviation_rules.py tests/training/invariants/test_inv_train_013_gamification_badge_rules.py tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py tests/training/invariants/test_inv_train_021_internal_load_trigger.py tests/training/invariants/test_inv_train_028_focus_sum_constraint.py tests/training/invariants/test_inv_train_029_edit_blocked_after_in_progress.py tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py tests/training/invariants/test_inv_train_052_exercise_media.py tests/training/invariants/test_inv_train_148_exercise_bank_services.py -q --tb=short 2>&1 | tail -5`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T21:47:50.025708+00:00
**Behavior Hash**: 5de5ded6f088e22295535f3eec41f257c003010b92dcf3003d9ebc00b774850f
**Evidence File**: `docs/hbtrack/evidence/AR_226/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 142a146
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -m pytest tests/training/invariants/test_inv_train_011_deviation_rules.py tests/training/invariants/test_inv_train_013_gamification_badge_rules.py tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py tests/training/invariants/test_inv_train_021_internal_load_trigger.py tests/training/invariants/test_inv_train_028_focus_sum_constraint.py tests/training/invariants/test_inv_train_029_edit_blocked_after_in_progress.py tests/training/invariants/test_inv_train_050_exercise_favorites_unique.py tests/training/invariants/test_inv_train_052_exercise_media.py tests/training/invariants/test_inv_train_148_exercise_bank_services.py -q --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T23:07:18.167858+00:00
**Behavior Hash**: 2412147326683390a6460f309bad8768392f45339a0219c543fe5e6c6dc9c148
**Evidence File**: `docs/hbtrack/evidence/AR_226/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 142a146
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_226_142a146/result.json`

### Selo Humano em 142a146
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T23:22:26.657973+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_226_142a146/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_226/executor_main.log`
