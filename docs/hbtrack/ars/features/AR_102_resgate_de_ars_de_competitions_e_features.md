# AR_102 — Resgate de ARs de Competitions e Features

**Status**: ⚠️ PENDENTE
**Versão do Protocolo**: 1.2.0

## Descrição
Mover AR_002, AR_036 (competitions) e AR_014, AR_015 (features) para as pastas ativas. Restaurar DEPRECATED_PATTERNS.md para a raiz de specs.

## Critérios de Aceite
1. Paths restaurados conforme PRD; 2. DEPRECATED_PATTERNS.md acessível pelo DOC-GATE-017.

## Validation Command (Contrato)
```
python scripts/run/doc_gates.py --ar-id 102
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_102/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/_legacy/ars/
git clean -fd docs/hbtrack/ars/competitions/
git clean -fd docs/hbtrack/ars/features/
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Restaura o histórico de migração do frontend.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


> 📋 Kanban routing: Executor: Evidence Pack missing or incomplete

### Verificacao Testador em 6577c49
**Status Testador**: ⚠️ PENDENTE
**Consistency**: UNKNOWN
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 2 | **Exit Executor**: None
**TESTADOR_REPORT**: `_reports/testador/AR_102_6577c49/result.json`
