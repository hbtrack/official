"""Escreve _reports/EXECUTOR.yaml com EXECUTOR_REPORT para AR_201."""
import os, datetime
os.chdir(r"c:\HB TRACK")

now = datetime.date.today().isoformat()

content = f"""# EXECUTOR.yaml — EXECUTOR_REPORT

| Campo | Valor |
|---|---|
| **AR** | AR_201 |
| **Título** | Fix validation_command AR_200 - janela 450 para split-por-linha |
| **Data** | {now} |
| **Branch** | dev-changes-2 |
| **Status** | ✅ CONCLUÍDO — Exit Code: 0 |
| **Evidence** | docs/hbtrack/evidence/AR_201/executor_main.log |

---

## Ações Executadas

### E1 — Leitura da AR
- AR_201 lida integralmente: `docs/hbtrack/ars/features/AR_201_fix_validation_command_ar_200_-_janela_450_para_sp.md`
- Write scope: `docs/hbtrack/ars/features/` + `docs/hbtrack/evidence/AR_200/`
- validation_command canônica confirmada

### E2 — Análise de Impacto (preenchida antes do código)
- Causa raiz documentada: janela +450 captura INV-006 (NOT_RUN legítimo)
- Fix: substituição line-by-line via `t.split('\\n')` com `ln.startswith('| '+lbl+' ')`
- Zero impacto em Backend/Frontend/código de produto

### E3 — Patch mínimo atômico

**Arquivo 1 editado**: `docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md`
- Seção `## Validation Command (Contrato)`: substituição total do bloco Python
  - OLD: `t.find(lbl)!=-1 and 'NOT_RUN' in t[t.find('| '+lbl):t.find('| '+lbl)+450]`
  - NEW: `any('NOT_RUN' in ln for ln in t.split('\\n') if ln.startswith('| '+lbl+' '))`
  - Idem para ct_ids (CONTRACT-TRAIN)
- Carimbo histórico (Exit Code: 1): anotado como "(contrato corrigido por AR_201)"

**Arquivo 2 editado**: `docs/hbtrack/ars/features/AR_201_fix_validation_command_ar_200_-_janela_450_para_sp.md`
- Seção `## Análise de Impacto` preenchida com diagnóstico técnico completo

### E4 — Re-execução hb report 200
- Comando: `python temp/_run_ar200_report_v2.py`
- Resultado: Exit Code: 0 (`PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido`)
- Evidence atualizada: `docs/hbtrack/evidence/AR_200/executor_main.log`

### E5 — Execução hb report 201
- Comando: `python temp/_run_ar201_report.py`
- Resultado: Exit Code: 0 (`PASS: AR_200 validation_command corrigida + executor_main.log Exit Code: 0`)
- Evidence gerada: `docs/hbtrack/evidence/AR_201/executor_main.log`

---

## Critérios de Aceite — Verificação

| AC | Descrição | Status |
|---|---|---|
| AC-001 | AR_200 não contém `+450` na validation_command | ✅ PASS |
| AC-002 | AR_200 contém `split` na validation_command | ✅ PASS |
| AC-003 | executor_main.log AR_200 contém `Exit Code: 0` | ✅ PASS |
| AC-004 | executor_main.log AR_200 contém `PASS: 10 evidencias` | ✅ PASS |

---

## Stage Exato

```
git add docs/hbtrack/evidence/AR_201/executor_main.log
git add docs/hbtrack/evidence/AR_200/executor_main.log
git add docs/hbtrack/ars/features/AR_200_executar_top-10_testes_coberto+not_run_e_salvar_ev.md
git add docs/hbtrack/ars/features/AR_201_fix_validation_command_ar_200_-_janela_450_para_sp.md
git add docs/_canon/planos/ar_201_fix_validation_command_ar200_window.json
git add docs/hbtrack/_INDEX.md
```

---

## Nota para o Testador

- Executar `hb verify 201` (triple-run, exit_code=0, hashes idênticos)
- Executar `hb verify 200` (triple-run, Exit Code: 0 esperado)
- `hb seal 201` → `hb seal 200` (nesta ordem)
- Workspace contém arquivos unstaged de outras ARs (Backend/Frontend) — são pré-existentes, fora do write_scope desta AR.
"""

with open("_reports/EXECUTOR.yaml", "w", encoding="utf-8") as f:
    f.write(content)
print("EXECUTOR.yaml written OK")
