# AR_101 — Resgate de ARs de Governança (v1.2.0 Core)

**Status**: ⚠️ PENDENTE
**Versão do Protocolo**: 1.2.0

## Descrição
Mover AR_017, AR_023, AR_024, AR_026 e AR_034 de _legacy/ars/governance para docs/hbtrack/ars/governance/. Atualizar status 'EM TESTE' para 'EM_EXECUCAO'.

## Critérios de Aceite
1. Arquivos movidos com sucesso; 2. Token 'EM TESTE' removido; 3. doc_gates.py reporta PASS.

## Validation Command (Contrato)
```
python scripts/run/doc_gates.py --ar-id 101
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_101/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- docs/_legacy/ars/governance/
git clean -fd docs/hbtrack/ars/governance/
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Notas do Arquiteto
Essas ARs são o núcleo do protocolo atual.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


> 📋 Kanban routing: Executor: Evidence Pack missing or incomplete

### Verificacao Testador em a29d573
**Status Testador**: ⚠️ PENDENTE
**Consistency**: UNKNOWN
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 2 | **Exit Executor**: None
**TESTADOR_REPORT**: `_reports/testador/AR_101_a29d573/result.json`
