content = """# TESTADOR.md — Handoff para Humano / Executor

**RUN_ID**: TESTADOR-AR193-20260301
**AR_ID**: AR_193
**Branch**: dev-changes-2
**HEAD**: b123a58
**Data**: 2026-03-01
**Protocolo**: v1.3.0

---

## RESULT: ⏸️ BLOQUEADO_INFRA

**Motivo**: `DIRTY_WORKSPACE` — arquivos tracked com mudanças não-staged (MM)

O Testador **NÃO executou** `hb verify`. Pré-condição "workspace limpo (tracked-unstaged vazio)" **FALHOU**.

---

## Pré-condições — Checklist AR_193

| Pré-condição | Status | Detalhe |
|---|:---:|---|
| AR existe (`docs/hbtrack/ars/**/AR_193_*.md`) | ✅ | `docs/hbtrack/ars/features/AR_193_test_matrix_sync_batch4_5_-_ar-train-015..021_veri.md` |
| Validation Command não vazio | ✅ | Confirmado no EXECUTOR.md (exit code 0) |
| Evidence existe (`docs/hbtrack/evidence/AR_193/executor_main.log`) | ✅ | Presente |
| Evidence STAGED | ✅ | `A  docs/hbtrack/evidence/AR_193/executor_main.log` |
| **Workspace limpo (tracked-unstaged vazio)** | ❌ | **6 arquivos MM** — ver seção abaixo |
| Kanban em fase compatível | — | Não verificado (bloqueado antes) |

---

## Arquivos tracked-unstaged (MM) — workspace sujo

```
MM .github/agents/Arquiteto.agent.md
MM docs/hbtrack/Hb Track Kanban.md
MM docs/hbtrack/_INDEX.md
MM docs/ssot/alembic_state.txt
MM Hb Track - Backend/docs/ssot/alembic_state.txt
MM Hb Track - Backend/docs/ssot/schema.sql
```

**Total**: 6 arquivos com staged + unstaged (MM = dirty working tree)

---

## CONSISTENCY: N/A

`hb verify` não executado — workspace sujo bloqueou antes.

## TRIPLE_CONSISTENCY: N/A

## EVIDENCES

Testador **não gerou** `context.json` / `result.json` — nenhum `hb verify` foi executado.

---

## NEXT_ACTION

**→ Executor**: Stagear os arquivos MM para zerar tracked-unstaged, depois re-entregar ao Testador.

Comandos para limpar o workspace:
```
git add ".github/agents/Arquiteto.agent.md"
git add "docs/hbtrack/Hb Track Kanban.md"
git add "docs/hbtrack/_INDEX.md"
git add "docs/ssot/alembic_state.txt"
git add "Hb Track - Backend/docs/ssot/alembic_state.txt"
git add "Hb Track - Backend/docs/ssot/schema.sql"
```

Após stagear: confirmar `git diff --name-only` retorna **vazio**, depois re-entregar ao Testador.

---

## Histórico de Resultados Anteriores (preservado)

| AR | Resultado | HEAD |
|---|---|---|
| AR_189 | ✅ SUCESSO (sealed) | b123a58 |
| AR_190 | ✅ SUCESSO (sealed) | b123a58 |
| AR_191 | ✅ SUCESSO (sealed) | b123a58 |
| AR_192 | ✅ SUCESSO (sealed) | b123a58 |
| **AR_193** | ⏸️ BLOQUEADO_INFRA | b123a58 |

---

## Testador Contract Fields

```yaml
testador_report_id: TESTADOR-AR193-20260301
protocol_version: v1.3.0
ar_id: AR_193
git_head: b123a58
result: BLOQUEADO_INFRA
block_reason: DIRTY_WORKSPACE
dirty_files_mm:
  - .github/agents/Arquiteto.agent.md
  - docs/hbtrack/Hb Track Kanban.md
  - docs/hbtrack/_INDEX.md
  - docs/ssot/alembic_state.txt
  - Hb Track - Backend/docs/ssot/alembic_state.txt
  - Hb Track - Backend/docs/ssot/schema.sql
triple_run: N/A
consistency: N/A
staged_testador_files: []
next_agent: Executor (limpar workspace MM) -> Testador
```

---

*Gerado automaticamente pelo Testador — sem ✅ VERIFICADO (exclusivo do humano via `hb seal`)*
"""

import os
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_reports", "TESTADOR.md")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print(f"OK: {path}")
