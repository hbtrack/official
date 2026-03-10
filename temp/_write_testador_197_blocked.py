import pathlib

content = """# TESTADOR_REPORT — AR_197

| Campo | Valor |
|---|---|
| **RUN_ID** | TESTADOR-AR197-20260302 |
| **AR_ID** | AR_197 |
| **Protocolo** | v1.3.0 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **Data** | 2026-03-02 |
| **RESULT** | ⏸️ BLOQUEADO_INFRA |
| **CONSISTENCY** | N/A (verify não executado) |
| **TRIPLE_CONSISTENCY** | N/A |

---

## Motivo do Bloqueio

**DIRTY_WORKSPACE** — `git diff --name-only` retornou 7 arquivos tracked-unstaged.

Conforme as regras do Testador: workspace sujo → bloquear e parar. `hb verify` NÃO foi executado.

### Arquivos tracked-unstaged (dirty):

```
Hb Track - Backend/app/core/db.py
Hb Track - Backend/docs/ssot/alembic_state.txt
Hb Track - Backend/docs/ssot/schema.sql
docs/hbtrack/ars/features/AR_196_promover_status_ssot_training_ar_backlog_+_invaria.md
docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md
docs/hbtrack/modulos/treinos/TRAINING_BATCH_PLAN_v1.md
docs/ssot/alembic_state.txt
```

### Pré-condições verificadas:

| Pré-condição | Status | Detalhe |
|---|---|---|
| AR existe | ✅ | `docs/hbtrack/ars/features/AR_197_invariants_training.md_v1.5.0_31_itens_gap_parcial.md` |
| AR tem Validation Command | ✅ | Confirmado via EXECUTOR.yaml (3 checks, Exit 0) |
| Evidence existe | ✅ | `docs/hbtrack/evidence/AR_197/executor_main.log` |
| Evidence staged | ✅ | Presente em `git diff --cached` |
| Workspace limpo | ❌ | **7 tracked-unstaged — BLOQUEADO** |
| Fase Kanban compatível | ✅ | AR_197 em READY (Section 21) |

---

## EVIDENCES

Não aplicável — `hb verify` não executado. Nenhum `context.json` / `result.json` gerado.

---

## NEXT_ACTION

**→ Executor: limpar workspace (staged os arquivos pendentes ou revertê-los de forma segura, SEM git restore / git reset --hard).**

Após workspace limpo (`git diff --name-only` vazio), Testador retoma:
```
python scripts/run/hb_cli.py verify 197
```
"""

out = pathlib.Path(r"_reports/TESTADOR.yaml")
out.write_text(content, encoding="utf-8")
print("TESTADOR.yaml escrito — BLOCKED DIRTY_WORKSPACE AR_197")
