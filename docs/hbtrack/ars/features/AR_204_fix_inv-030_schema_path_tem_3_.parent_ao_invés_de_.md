# AR_204 — Fix INV-030: schema_path tem 3 .parent ao invés de 4 (mesma causa do INV-008)

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Em test_inv_train_030_attendance_correction_fields.py, a mesma causa raiz do INV-008: Path(__file__).parent.parent.parent resolve para tests/ e o schema.sql path fica errado. Fix idêntico: adicionar .parent extra.

## Critérios de Aceite
pytest tests/training/invariants/test_inv_train_030_attendance_correction_fields.py passa (0 FAILs, 0 ERRORs); Evidência de execução gerada em _reports/training/TEST-TRAIN-INV-030.md

## Write Scope
- Hb Track - Backend/tests/training/invariants/test_inv_train_030_attendance_correction_fields.py

## Validation Command (Contrato)
```
cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_030_attendance_correction_fields.py -v --tb=short 2>&1
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_204/executor_main.log`

## Análise de Impacto
**Causa raiz**: Mesma causa do INV-008. `Path(__file__).parent.parent.parent` resolve para `tests/`, mas o `schema.sql` está em `Hb Track - Backend/docs/ssot/schema.sql`, exigindo `.parent.parent.parent.parent` para subir até o root do backend.

**Fix aplicado**: Substituir todas as 6 ocorrências de `Path(__file__).parent.parent.parent / "docs"` por `Path(__file__).parent.parent.parent.parent / "docs"` em `test_inv_train_030_attendance_correction_fields.py`.

**Impacto colateral**: Zero — apenas corrige o path de resolução do schema.sql.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Backend" && pytest tests/training/invariants/test_inv_train_030_attendance_correction_fields.py -v --tb=short 2>&1`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T02:58:26.519454+00:00
**Behavior Hash**: 8093af667a4c5f49f33f20f1ba46088d59b541781e6469b9bb8abef3d4b722de
**Evidence File**: `docs/hbtrack/evidence/AR_204/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_204_b123a58/result.json`
