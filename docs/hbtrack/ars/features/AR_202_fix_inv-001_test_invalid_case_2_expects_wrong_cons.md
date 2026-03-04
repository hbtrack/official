# AR_202 — Fix INV-001: test_invalid_case_2 expects wrong constraint name

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Em test_inv_train_001_focus_sum_constraint.py, a função test_invalid_case_2__negative_focus insere uma sessão com focus_attack_positional_pct=-5. O PostgreSQL dispara ck_training_sessions_focus_attack_positional_range (range check no campo negativo) antes de ck_training_sessions_focus_total_sum. O test espera ck_training_sessions_focus_total_sum mas deve esperar ck_training_sessions_focus_attack_positional_range. Fix: mudar a string de expected constraint name na chamada assert_pg_constraint_violation nessa função.

## Critérios de Aceite
pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py passa (0 FAILs, 0 ERRORs); Apenas a string de expected constraint name alterada — nenhuma outra linha de lógica modificada; Evidência de execução gerada em _reports/training/TEST-TRAIN-INV-001.md

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_001_focus_sum_constraint.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py -v --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_202/executor_main.log`

## Riscos
- Se existirem outros test cases que também esperem ck_training_sessions_focus_total_sum com valores negativos, devem ser verificados individualmente.

## Análise de Impacto
**Causa raiz**: O arquivo `test_inv_train_001_focus_sum_constraint.py` está truncado — termina no meio da chamada `assert_pg_constraint_violation(...)` sem fechar o parêntese, sem `await async_db.rollback()` e sem encerramento do método. 224 linhas lidas, mas o `Get-Content` mostra arquivo com 196 linhas efetivas (leitura para). Isso causa `SyntaxError` (unclosed parenthesis), que o pytest reporta como ERROR/FAIL.

**Fix aplicado**: Acrescentar as 3 linhas faltantes ao final do arquivo:
- `)` — fecha o `assert_pg_constraint_violation(...)`
- linha em branco
- `await async_db.rollback()` — padrão dos demais test cases do arquivo

**Impacto colateral**: Zero — nenhuma lógica de negócio alterada. Apenas completar sintaxe Python truncada.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py -v --tb=short 2>&1`
**Exit Code**: 255
**Timestamp UTC**: 2026-03-03T02:50:20.413130+00:00
**Behavior Hash**: d7f0027db1b9f614c9423cc40145a57f68b1cffb191d13110e7ed140b25fbadd
**Evidence File**: `docs/hbtrack/evidence/AR_202/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: ❌ FALHA
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py -v --tb=short 2>&1`
**Exit Code**: 255
**Timestamp UTC**: 2026-03-03T02:53:36.046604+00:00
**Behavior Hash**: d7f0027db1b9f614c9423cc40145a57f68b1cffb191d13110e7ed140b25fbadd
**Evidence File**: `docs/hbtrack/evidence/AR_202/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_001_focus_sum_constraint.py -v --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T02:56:52.486615+00:00
**Behavior Hash**: afb312eb3f767d5e5b50244ac7d60a2c96f49671d49522c99074428f0b3664ce
**Evidence File**: `docs/hbtrack/evidence/AR_202/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_202_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T04:25:34.106383+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_202_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_202/executor_main.log`
