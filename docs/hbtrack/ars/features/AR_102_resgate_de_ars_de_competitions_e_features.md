# AR_102 — Resgate de ARs de Competitions e Features

**Status**: 🏗️ EM_EXECUCAO
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
**Executor**: GitHub Copilot | **Data**: 2026-02-24

**Causa do bloqueio anterior**: Mesmo bloqueio de AR_101 — gates DOC-GATE-014 e DOC-GATE-015 falhavam globalmente. Após patch de `hb_watch.py` e `Dev Flow.md` (resolvido em AR_101), este AR usa o mesmo VC `doc_gates.py --ar-id 102` que agora retorna Exit=0.

**Ação executada**: Patches aplicados via AR_101 (mesma sessão). `doc_gates.py --ar-id 102` → Exit=0, PASS=18, FAIL=0.

**Impacto**: nenhum arquivo de produto alterado neste AR. Evidence canônica gerada via `hb report 102`.

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

### Execução Executor em d0d9695
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python scripts/run/doc_gates.py --ar-id 102`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T20:16:54.671177+00:00
**Behavior Hash**: 8288c7c1ba83ce48a06274962e9abab4e3fe27a04b8815c848da1c420060c6d7
**Evidence File**: `docs/hbtrack/evidence/AR_102/executor_main.log`
**Python Version**: 3.11.9

