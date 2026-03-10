content = """# TESTADOR.yaml — Handoff para Humano

**RUN_ID**: TESTADOR-AR194-20260301-FINAL
**AR_ID**: AR_194
**Branch**: dev-changes-2
**HEAD**: b123a58
**Data**: 2026-03-01
**Protocolo**: v1.3.0

---

## RESULT: ✅ SUCESSO

| AR_ID | Titulo | RESULT | CONSISTENCY | TRIPLE_CONSISTENCY | Hash (3x) |
|---|---|---|---|---|---|
| **AR_194** | TRAINING_BATCH_PLAN_v1 — adicionar Batch 6 (AR-TRAIN-010B) | ✅ SUCESSO | OK | PASS | 9d82efdb0df57431 |

---

## Pre-condicoes (checklist — todas OK)

| Pre-condicao | Status | Detalhe |
|---|:---:|---|
| AR existe (docs/hbtrack/ars/**/AR_194_*.md) | ✅ | docs/hbtrack/ars/features/AR_194_training_batch_plan_v1_-_adicionar_batch_6_com_ar-.md |
| Validation Command nao vazio | ✅ | Confirmado na AR_194 |
| Evidence existe (executor_main.log) | ✅ | docs/hbtrack/evidence/AR_194/executor_main.log |
| Evidence STAGED | ✅ | A docs/hbtrack/evidence/AR_194/executor_main.log |
| Workspace limpo (tracked-unstaged vazio) | ✅ | git diff --name-only vazio |
| Kanban em fase compativel | ✅ | AR_194 em estado executavel |

---

## CONSISTENCY: OK

## TRIPLE_CONSISTENCY: PASS

- Run 1/3: exit=0, hash=9d82efdb0df57431
- Run 2/3: exit=0, hash=9d82efdb0df57431
- Run 3/3: exit=0, hash=9d82efdb0df57431
- Hashes: IDENTICOS

---

## EVIDENCES

- docs/hbtrack/evidence/AR_194/executor_main.log
- _reports/testador/AR_194_b123a58/context.json  [STAGED]
- _reports/testador/AR_194_b123a58/result.json   [STAGED]

---

## NEXT_ACTION

**Responsavel**: Humano
**Acao**: `hb seal 194` para registrar VERIFICADO na AR_194.
(O Testador NAO executa hb seal — exclusivo do humano.)

---

## Testador Contract Fields

```yaml
testador_report_id: TESTADOR-AR194-20260301-FINAL
protocol_version: v1.3.0
ar_id: AR_194
git_head: b123a58
result: SUCESSO
triple_run: PASS
consistency: OK
hash: 9d82efdb0df57431 (3x identico)
staged_testador_files:
  - _reports/testador/AR_194_b123a58/context.json
  - _reports/testador/AR_194_b123a58/result.json
next_agent: Humano (hb seal 194)
```

---

*Gerado automaticamente pelo Testador — sem VERIFICADO (exclusivo do humano via `hb seal`)*
"""

with open("_reports/TESTADOR.yaml", "w", encoding="utf-8") as f:
    f.write(content)
print("OK")
