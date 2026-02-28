# AR_174 — Migrar _generated para ssot nos test files TRAINING (lote 2/2)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Substituir '"_generated"' por '"ssot"' em 5 arquivos de testes TRAINING (Lote 2 de 2).
Task 173 cobriu os primeiros 6 arquivos.

ARQUIVOS DESTE LOTE:
1. tests/training/invariants/test_inv_train_035_session_templates_unique_name.py
2. tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py
3. tests/training/invariants/test_inv_train_037_cycle_dates.py
4. tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py
5. tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py

PADRAO DE SUBSTITUICAO:
  DE:   / "docs" / "_generated" / "schema.sql"
  PARA: / "docs" / "ssot" / "schema.sql"

NAO modificar arquivos fora da lista. Executor deve completar Task 173 primeiro.

## Critérios de Aceite
1) Nenhum dos 5 arquivos deste lote contem '"_generated"' apos a migracao.
2) docs/ssot/schema.sql existe no repositorio.
3) Combinado com Task 173: ZERO arquivos TRAINING contem refs a _generated.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_035_session_templates_unique_name.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_037_cycle_dates.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "import sys; from pathlib import Path; files=['tests/training/invariants/test_inv_train_035_session_templates_unique_name.py','tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py','tests/training/invariants/test_inv_train_037_cycle_dates.py','tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py','tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py']; errs=[f for f in files if chr(34)+'_generated'+chr(34) in Path(f).read_text(encoding='utf-8')]; sys.exit('FAIL _generated still found: '+str(errs)) if errs else print('PASS lote 2: 5 files migrated')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_174/executor_main.log`

## Notas do Arquiteto
ANCORA: docs/ssot/schema.sql EXISTS. Continuacao Task 173. Apos ambas: zero refs _generated em testes TRAINING.

## Riscos
- Se arquivos tiverem refs a openapi.json ou manifest.json em _generated, migrar no mesmo pass
- Executor deve rodar Task 173 primeiro

## Análise de Impacto
- Escopo: 5 arquivos de testes TRAINING (lote 2/2) em `Hb Track - Backend/tests/training/invariants/`.
- Mudança: substituição mecânica de `"_generated"` → `"ssot"` (aspas duplas) nos paths de fixtures.
- Risco DB: zero.
- Risco produto: zero.
- Validation command corrigido: usa `chr(34)+'_generated'+chr(34)` para evitar falso positivo em campo `is_ai_generated`.
- Estado verificado: todos os 5 arquivos já têm a substituição aplicada (OK pré-validado).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 07760d4
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -c "import sys; from pathlib import Path; files=['tests/training/invariants/test_inv_train_035_session_templates_unique_name.py','tests/training/invariants/test_inv_train_036_wellness_rankings_unique.py','tests/training/invariants/test_inv_train_037_cycle_dates.py','tests/training/invariants/test_inv_train_072_ai_suggestion_not_order.py','tests/training/invariants/test_inv_train_077_immediate_virtual_coach_feedback.py']; errs=[f for f in files if chr(34)+'_generated'+chr(34) in Path(f).read_text(encoding='utf-8')]; sys.exit('FAIL _generated still found: '+str(errs)) if errs else print('PASS lote 2: 5 files migrated')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T10:05:14.915105+00:00
**Behavior Hash**: 58341b511dfb92e42bd5a09804ad4d2e446574a93741856bb391809f86f0c651
**Evidence File**: `docs/hbtrack/evidence/AR_174/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T10:31:09.936501+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_174_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_174/executor_main.log`

### Verificacao Testador em 07760d4
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_174_07760d4/result.json`

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T17:32:54.464983+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_174_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_174/executor_main.log`
