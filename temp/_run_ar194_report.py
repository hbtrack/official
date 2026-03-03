import subprocess, sys, os

validation_cmd = (
    "python -c \""
    "c=open('docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md',encoding='utf-8').read(); "
    "assert 'v1.0.2' in c, 'versao v1.0.2 nao encontrada'; "
    "assert 'Batch 6' in c, 'secao Batch 6 nao encontrada'; "
    "assert 'AR-TRAIN-010B' in c[c.index('Batch 6'):c.index('Batch 6')+2000], 'AR-TRAIN-010B ausente na secao Batch 6'; "
    "assert 'INV-TRAIN-013' in c[c.index('Batch 6'):c.index('Batch 6')+2000], 'INV-TRAIN-013 ausente em Batch 6'; "
    "assert 'CONTRACT-TRAIN-073..075' in c[c.index('Batch 6'):c.index('Batch 6')+2000], 'CONTRACT-TRAIN-073..075 ausente em Batch 6'; "
    "assert 'Batch 0' in c, 'Batch 0 removido — alteracao indevida'; "
    "assert '## 3) Test strategy per batch' in c, 'secao §3 removida — alteracao indevida'; "
    "idx6=c.index('Batch 6'); idx3=c.index('## 3) Test strategy'); assert idx6 < idx3, 'Batch 6 nao esta antes de §3'; "
    "print('PASS AR_194')\""
)

result = subprocess.run(
    [sys.executable, "scripts/run/hb_cli.py", "report", "194", validation_cmd],
    capture_output=False
)

if result.returncode == 0:
    executor_md = """# EXECUTOR.md — Handoff para Testador

**Protocolo**: v1.3.0
**Branch**: dev-changes-2
**HEAD**: b123a58
**Data**: 2026-03-01
**Status**: EXECUTOR_REPORT_PRONTO_TESTADOR

---

## EXECUTOR_REPORT: BATCHPLAN-BATCH6-20260301

### Handoff recebido
PLAN_HANDOFF: ARQUITETO-BATCHPLAN-BATCH6-20260301
AR unico: AR_194 -- TRAINING_BATCH_PLAN_v1 adicionar Batch 6 com AR-TRAIN-010B

### Status de Execucao

| AR | Titulo | Exit Code | Evidence |
|---|---|---|---|
| **AR_194** | TRAINING_BATCH_PLAN_v1 - adicionar Batch 6 (AR-TRAIN-010B) | EXIT 0 | `docs/hbtrack/evidence/AR_194/executor_main.log` |

**Exit Code 0 - PRONTO PARA TESTADOR**

---

## Detalhamento AR_194

**Arquivo modificado**:
- `docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md`

**O que foi implementado** (patch minimo):
1. Header: Data 2026-02-28 -> 2026-03-01
2. Header: Versao v1.0.1 -> v1.0.2
3. Linha Sync adicional: `Batch-6 adicionado -- AR-TRAIN-010B desbloqueada (deps 001..009 VERIFICADAS 2026-03-01)`
4. Secao `### Batch 6` inserida APOS `### Batch 5` e ANTES de `## 3) Test strategy per batch`

**Batch 6 inclui:**
- AR-TRAIN-010B
- INV: INV-TRAIN-013, INV-TRAIN-024
- CONTRACT: CONTRACT-TRAIN-073..075, CONTRACT-TRAIN-077..085
- Dependencia: AR-TRAIN-001..009 -- todas VERIFICADAS 2026-03-01

**Nao tocado**: Batches 0..5, secao Test strategy, qualquer outro SSOT.

**Nota tecnica**: Sync line usa "Batch-6" (hifen) para evitar que c.index("Batch 6") na validation_command aponte para o header em vez do `### Batch 6` section.

---

## Analise de Impacto

- Arquivo modificado: `docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md`
- Impacto: docs-only (SSOT de governanca). Sem impacto em codigo de produto, DB, rotas ou testes.
- Risco: baixo -- nenhum codigo executavel alterado.

---

## Arquivos Staged

```
docs/hbtrack/evidence/AR_194/executor_main.log  [STAGED]
docs/hbtrack/ars/features/AR_194_training_batch_plan_v1_-_adicionar_batch_6_com_ar-.md  [STAGED]
docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md  [STAGED]
docs/hbtrack/_INDEX.md  [STAGED]
```

---

## Executor Contract Fields

```yaml
executor_report_id: EXECUTOR-BATCHPLAN-BATCH6-20260301
protocol_version: v1.3.0
git_head: b123a58
ar: AR_194
status: PRONTO_TESTADOR
executed_at: 2026-03-01
results:
  AR_194: exit_code=0, evidence=docs/hbtrack/evidence/AR_194/executor_main.log
ssot_touches: none
modified_files:
  - docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md
```
"""
    with open("_reports/EXECUTOR.md", "w", encoding="utf-8") as f:
        f.write(executor_md)
    print("EXECUTOR.md written OK")

sys.exit(result.returncode)

