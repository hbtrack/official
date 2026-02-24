# AR_999 — Exemplo: Adicionar campo birthdate em Person

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.2.0

## Descrição
Implementar campo opcional birthdate no model Person e migração Alembic. Este é um exemplo de task que toca código e portanto MUST ter write_scope explícito (GATE P3.6).

## Critérios de Aceite
1. Migration criada com ALTER TABLE persons ADD COLUMN birthdate DATE
2. Model Person atualizado com campo birthdate: Mapped[Optional[date]]
3. pytest tests/test_person.py passa
4. Alembic upgrade/downgrade funciona

## Write Scope
- Hb Track - Backend/app/models/person.py
- Hb Track - Backend/alembic/versions/*.py

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/alembic_state.txt

## Validation Command (Contrato)
```
python temp/validate_ar999.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_999/executor_main.log`

## Rollback Plan (Contrato)
```
python scripts/run/hb_cli.py rollback 999
git checkout -- 'Hb Track - Backend/app/models/person.py'
git clean -fd 'Hb Track - Backend/alembic/versions/'
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Task exemplo para demonstrar write_scope estruturado. Não é uma AR real — serve apenas como template.

## Riscos
- Pode quebrar dependências de Person se não houver testes de integração
- Migration irreversível se houver dados em produção (usar default NULL)

## Análise de Impacto
**Objetivo**: Adicionar campo opcional `birthdate` (DATE) ao model Person com migration Alembic.

**Impacto**:
- Migration: ALTER TABLE persons ADD COLUMN birthdate DATE NULL (reversível)
- Model: Adicionar `birthdate: Mapped[Optional[date]]` ao Person
- Teste: Implementar `test_birthdate_field` para validar campo opcional

**Risco**: BAIXO (campo opcional, não quebra dados existentes, migration reversível)

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução Executor em f638687
**Status Executor**: ❌ FALHA
**Comando**: `cd 'Hb Track - Backend'; pytest tests/models/test_person.py::test_birthdate_field -v`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T05:50:08.916706+00:00
**Behavior Hash**: e165e4d04e7fd3de25f792d8bf0d03e338d2aa497c62e3eaa3ad206af39d04f0
**Evidence File**: `docs/hbtrack/evidence/AR_999/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em f638687
**Status Executor**: ❌ FALHA
**Comando**: `python temp/validate_ar999.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T05:51:00.080443+00:00
**Behavior Hash**: cef4e164455368bb214b753546144787f43c605a5e94739f5a1711e7efc6716e
**Evidence File**: `docs/hbtrack/evidence/AR_999/executor_main.log`
**Python Version**: 3.11.9


### Execução Executor em f638687
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar999.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T05:51:32.084425+00:00
**Behavior Hash**: af41cedb65cd8ab5b7e7c698b0c4f2c3d12a1354e575895678aec8b08f5ae48b
**Evidence File**: `docs/hbtrack/evidence/AR_999/executor_main.log`
**Python Version**: 3.11.9


> 📋 Kanban routing: Arquiteto: Output não-determinístico: behavior_hash diverge nos 3 runs (exit 0 em todos, mas hash diferente)

### Verificacao Testador em f638687
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: FLAKY_OUTPUT (3x)
**Exit Testador**: 2 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_999_f638687/result.json`

### Execução Executor em f638687
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar999.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T05:53:41.738282+00:00
**Behavior Hash**: 2e3deec616a431952db7faef6631582eba1eba0a36f1d061e22e4025aad8dcde
**Evidence File**: `docs/hbtrack/evidence/AR_999/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 6998f74
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_999_6998f74/result.json`

### Verificacao Testador em 680f239
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_999_680f239/result.json`

### Selo Humano em b507dc6
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T16:31:22.747026+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_999_680f239/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_999/executor_main.log`
