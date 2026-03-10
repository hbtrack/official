"""Escreve _reports/TESTADOR.yaml com resultado BLOCKED_PRECONDITION para AR_201."""
import os
os.chdir(r"c:\HB TRACK")

content = """# TESTADOR.yaml — BLOCKED_PRECONDITION

| Campo | Valor |
|---|---|
| **RUN_ID** | TESTADOR-AR_201-b123a58 |
| **AR_ID** | AR_201 |
| **Data** | 2026-03-02 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **RESULT** | ⏸️ BLOQUEADO_INFRA |
| **CONSISTENCY** | N/A — verify não executado |
| **TRIPLE_CONSISTENCY** | N/A |

---

## Motivo do Bloqueio

**DIRTY_WORKSPACE** — `git diff --name-only` retornou arquivos tracked-unstaged:

```
Hb Track - Backend/docs/ssot/alembic_state.txt
Hb Track - Backend/docs/ssot/schema.sql
docs/hbtrack/Hb Track Kanban.md
docs/ssot/alembic_state.txt
```

Regra canônica (Testador.agent.md):
> "Workspace sujo (tracked-unstaged) => bloquear e parar. Você NÃO corrige."

O Testador NÃO executa comandos destrutivos (`git restore`, `git checkout -- .`, etc).

---

## Pré-condições avaliadas

| Pré-condição | Status |
|---|---|
| AR_201 existe (`docs/hbtrack/ars/features/AR_201_*.md`) | ✅ OK |
| AR_201 tem Validation Command não vazio | ✅ OK |
| Evidence `docs/hbtrack/evidence/AR_201/executor_main.log` existe | ✅ OK |
| Evidence AR_201 STAGED (`git diff --cached`) | ✅ OK |
| Evidence AR_200 STAGED | ✅ OK |
| **Workspace limpo (tracked-unstaged vazio)** | ❌ FALHOU |
| Kanban em fase compatível | ✅ OK |

---

## Evidências Testador Staged

Nenhuma — verify não foi executado. Nenhum artefato de testador gerado.

---

## NEXT_ACTION

**→ Executor**: Limpar os arquivos tracked-unstaged listados abaixo (sem usar comandos destrutivos proibidos) e garantir `git diff --name-only` vazio antes de passar ao Testador novamente.

Arquivos tracked-unstaged a resolver:
- `Hb Track - Backend/docs/ssot/alembic_state.txt` — stagear se modificado durante hb report
- `Hb Track - Backend/docs/ssot/schema.sql` — idem
- `docs/hbtrack/Hb Track Kanban.md` — stagear se atualizado pelo Arquiteto/Executor durante este ciclo
- `docs/ssot/alembic_state.txt` — stagear se relevante ao ciclo atual

Após resolver: `git diff --name-only` deve retornar vazio.
"""

with open("_reports/TESTADOR.yaml", "w", encoding="utf-8") as f:
    f.write(content)
print("TESTADOR.yaml written OK")
