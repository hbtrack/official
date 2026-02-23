# AR_103 — Resgate de Drafts e Invariantes Wellness

**Status**: ⚠️ PENDENTE
**Versão do Protocolo**: 1.2.0

## Descrição
Mover AR_002.5 (A, B, C, D) para docs/hbtrack/ars/drafts/ para suportar gates de escala wellness.

## Critérios de Aceite
1. Invariantes wellness documentadas e em pasta ativa; 2. WELLNESS_SCALE_DOCS_ALIGNED gate funcional.

## Validation Command (Contrato)
```
python scripts/run/doc_gates.py --ar-id 103
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_103/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/_legacy/ars/drafts/
git clean -fd docs/hbtrack/ars/drafts/
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Essencial para o gate de triangulação de verdade §13.3.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


> 📋 Kanban routing: Executor: Evidence Pack missing or incomplete

### Verificacao Testador em 7e59167
**Status Testador**: ⚠️ PENDENTE
**Consistency**: UNKNOWN
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 2 | **Exit Executor**: None
**TESTADOR_REPORT**: `_reports/testador/AR_103_7e59167/result.json`
