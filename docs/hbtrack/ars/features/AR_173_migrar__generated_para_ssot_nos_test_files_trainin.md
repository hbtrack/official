# AR_173 — Migrar _generated para ssot nos test files TRAINING (lote 1/2)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Substituir '"_generated"' por '"ssot"' em 6 arquivos de testes TRAINING (Lote 1 de 2).
Task 174 cobre os outros 5 arquivos.

ARQUIVOS DESTE LOTE (executar a partir de Hb Track - Backend/):
1. tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py
2. tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py
3. tests/training/invariants/test_inv_train_021_internal_load_trigger.py
4. tests/training/invariants/test_inv_train_028_focus_sum_constraint.py
5. tests/training/invariants/test_inv_train_030_attendance_correction_fields.py
6. tests/training/invariants/test_inv_train_031_derive_phase_focus.py

PADRAO DE SUBSTITUICAO:
  DE:   / "docs" / "_generated" / "schema.sql"
  PARA: / "docs" / "ssot" / "schema.sql"
Idem para openapi.json e manifest.json se presentes nos arquivos.

METODO RECOMENDADO (Python, from Hb Track - Backend/):
>>> from pathlib import Path
>>> files = [<lista acima>]
>>> for f in files:
...     p = Path(f); t = p.read_text('utf-8')
...     p.write_text(t.replace('"_generated"', '"ssot"'), 'utf-8')

NAO modificar arquivos fora da lista.

## Critérios de Aceite
1) Nenhum dos 6 arquivos deste lote contem a string '"_generated"' apos a migracao.
2) Os arquivos referenciam docs/ssot/schema.sql.
3) docs/ssot/schema.sql existe no repositorio.

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_021_internal_load_trigger.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_028_focus_sum_constraint.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_030_attendance_correction_fields.py
- Hb Track - Backend/tests/training/invariants/test_inv_train_031_derive_phase_focus.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && python -c "import sys; from pathlib import Path; files=['tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py','tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py','tests/training/invariants/test_inv_train_021_internal_load_trigger.py','tests/training/invariants/test_inv_train_028_focus_sum_constraint.py','tests/training/invariants/test_inv_train_030_attendance_correction_fields.py','tests/training/invariants/test_inv_train_031_derive_phase_focus.py']; errs=[f for f in files if '_generated' in Path(f).read_text(encoding='utf-8')]; sys.exit('FAIL _generated still found: '+str(errs)) if errs else print('PASS lote 1: 6 files migrated')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_173/executor_main.log`

## Notas do Arquiteto
ANCORA: docs/ssot/schema.sql EXISTS. Task 174 cobre os outros 5 arquivos.

## Riscos
- Se arquivos tiverem refs a openapi.json ou manifest.json em _generated, migrar no mesmo pass
- NAO remover docs/_generated/ -- escopo fora desta AR

## Análise de Impacto
- Escopo: 6 arquivos de testes TRAINING (lote 1/2) em `Hb Track - Backend/tests/training/invariants/`.
- Mudança: substituição mecânica de `"_generated"` → `"ssot"` nos paths de fixtures (schema.sql, openapi.json, manifest.json).
- Risco DB: zero (sem alterações de schema ou dados).
- Risco produto: zero (apenas caminhos de artefatos de documentação nos testes).
- Estado verificado: todos os 6 arquivos já têm a substituição aplicada (OK pré-validado).

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 07760d4
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && python -c "import sys; from pathlib import Path; files=['tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py','tests/training/invariants/test_inv_train_020_cache_invalidation_trigger.py','tests/training/invariants/test_inv_train_021_internal_load_trigger.py','tests/training/invariants/test_inv_train_028_focus_sum_constraint.py','tests/training/invariants/test_inv_train_030_attendance_correction_fields.py','tests/training/invariants/test_inv_train_031_derive_phase_focus.py']; errs=[f for f in files if '_generated' in Path(f).read_text(encoding='utf-8')]; sys.exit('FAIL _generated still found: '+str(errs)) if errs else print('PASS lote 1: 6 files migrated')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T10:04:58.986349+00:00
**Behavior Hash**: 9fcd68c977f322a97bf17d44693ef0e5be22f0ca11d37f0d86c306e696c86d5c
**Evidence File**: `docs/hbtrack/evidence/AR_173/executor_main.log`
**Python Version**: 3.11.9

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T10:31:00.889549+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_173_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_173/executor_main.log`

### Verificacao Testador em 07760d4
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_173_07760d4/result.json`

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T17:32:48.071917+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_173_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_173/executor_main.log`
