# AR_203 — Fix INV-008: schema_path tem 3 .parent ao invés de 4

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Em test_inv_train_008_soft_delete_reason_pair.py, a variável schema_path é definida como Path(__file__).parent.parent.parent / 'docs' / 'ssot' / 'schema.sql'. O arquivo __file__ está em tests/training/invariants/, então 3 .parent resolve para tests/ e o path final é tests/docs/ssot/schema.sql (não existe). O fix é adicionar um .parent extra: Path(__file__).parent.parent.parent.parent / 'docs' / 'ssot' / 'schema.sql' — aponta para 'Hb Track - Backend/docs/ssot/schema.sql' (existe).

## Critérios de Aceite
pytest tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py passa (0 FAILs, 0 ERRORs); path resultante aponta para 'Hb Track - Backend/docs/ssot/schema.sql'; Evidência de execução gerada em _reports/training/TEST-TRAIN-INV-008.md

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py -v --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_203/executor_main.log`

## Riscos
- Se o arquivo schema.sql ainda não existir em docs/ssot/, o teste vai falhar com FileNotFoundError — verificar via 'python scripts/ssot/gen_docs_ssot.py' antes.

## Análise de Impacto
**Causa raiz**: `Path(__file__)` = `tests/training/invariants/test_inv_train_008_*.py`. Com `.parent.parent.parent` o caminho resolve para `tests/` (3 subidas: invariants→training→tests). O `schema.sql` está em `Hb Track - Backend/docs/ssot/schema.sql`, que exige subir mais 1 nível até `Hb Track - Backend/` raiz. Portanto se faz necessário `.parent.parent.parent.parent`.

**Fix aplicado**: Substituir todas as 6 ocorrências de `Path(__file__).parent.parent.parent / "docs"` por `Path(__file__).parent.parent.parent.parent / "docs"` em `test_inv_train_008_soft_delete_reason_pair.py`.

**Impacto colateral**: Zero — apenas corrige o path de resolução do schema.sql.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_008_soft_delete_reason_pair.py -v --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T02:57:51.678258+00:00
**Behavior Hash**: df475c246af10a2fb828c131f18df7c492c48ce919cde5ee9f52adc93835f165
**Evidence File**: `docs/hbtrack/evidence/AR_203/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_203_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T04:25:37.637211+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_203_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_203/executor_main.log`
