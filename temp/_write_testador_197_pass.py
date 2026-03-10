import pathlib

content = """# TESTADOR_REPORT — AR_197

| Campo | Valor |
|---|---|
| **RUN_ID** | TESTADOR-AR197-b123a58 |
| **AR_ID** | AR_197 |
| **Protocolo** | v1.3.0 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **Data** | 2026-03-02 |
| **RESULT** | ✅ SUCESSO |
| **CONSISTENCY** | OK |
| **TRIPLE_CONSISTENCY** | PASS (3/3 hashes idênticos) |

---

## Resultado do Triple-Run

| Run | Exit Code | Hash |
|---|---|---|
| Run 1/3 | 0 | `024a3407e37d128b` |
| Run 2/3 | 0 | `024a3407e37d128b` |
| Run 3/3 | 0 | `024a3407e37d128b` |

**Veredito:** ✅ SUCESSO — exit=0 × 3, hashes idênticos × 3.

**STDOUT:**
```
PASS: all invariants IMPLEMENTADO
PASS: version v1.5.0 ok
PASS: traceability note present
```

**result.json:** `workspace_clean: True` · `evidence_pack_complete: True` · `status: SUCESSO`

---

## Pré-condições (todas ✅)

| Pré-condição | Status | Detalhe |
|---|---|---|
| AR existe | ✅ | `docs/hbtrack/ars/features/AR_197_invariants_training.md_v1.5.0_31_itens_gap_parcial.md` |
| AR tem Validation Command | ✅ | 3 checks: GAP/PARCIAL/DIVERGENTE count=0 · version v1.5.0 · traceability |
| Evidence existe | ✅ | `docs/hbtrack/evidence/AR_197/executor_main.log` |
| Evidence staged | ✅ | `git diff --cached` contém `evidence/AR_197/executor_main.log` |
| Workspace limpo | ✅ | `git diff --name-only` = vazio (UNSTAGED_COUNT: 0) no momento do verify |
| Fase Kanban compatível | ✅ | Section 21 — AR_197 READY |

**Nota pós-verify:** `hb verify` atualizou automaticamente `docs/hbtrack/Hb Track Kanban.md` (remoção de 1 linha em branco — side-effect do CLI). `workspace_clean: True` no result.json registrado antes do efeito. Kanban não staged pelo Testador (proibido pelo skill). O humano deve stagear ao executar `hb seal 197`.

---

## EVIDENCES (staged — Testador)

```
_reports/testador/AR_197_b123a58/context.json
_reports/testador/AR_197_b123a58/result.json
```

---

## NEXT_ACTION

**→ Humano: `hb seal 197`**
"""

out = pathlib.Path(r"_reports/TESTADOR.yaml")
out.write_text(content, encoding="utf-8")
print("TESTADOR.yaml escrito — SUCESSO AR_197")
