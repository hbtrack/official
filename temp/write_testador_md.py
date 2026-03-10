"""Rewrite _reports/TESTADOR.yaml with final triple-run results."""
from pathlib import Path

content = """# TESTADOR REPORT — BATCH0-TRAINING-FULL-20260228

---

## CABECALHO

| Campo | Valor |
|---|---|
| **RUN_ID** | BATCH0-TRAINING-FULL-20260228 |
| **GIT_SHA** | 07760d4 |
| **Data** | 2026-02-28 |
| **Protocol** | v1.3.0 |
| **Metodo Triple-Run** | 3x deterministico — hashes identicos em todas |

---

## RESULTADOS

| AR | Resultado | TRIPLE_CONSISTENCY | Hash (16) | Runs |
|---|---|---|---|---|
| **AR_169** | ✅ SUCESSO | OK | 3b7525c5cb81a853 | 3/3 exit=0 |
| **AR_170** | ✅ SUCESSO | OK | 98ff43e0d607dc3c | 3/3 exit=0 |
| **AR_171** | ✅ SUCESSO | OK | 5257c66fb8175f85 | 3/3 exit=0 |
| **AR_172** | ✅ SUCESSO | OK | 2e4fa785242e7f91 | 3/3 exit=0 |
| **AR_173** | ✅ SUCESSO | OK | 9fcd68c977f322a9 | 3/3 exit=0 |
| **AR_174** | ✅ SUCESSO | OK | 58341b511dfb92e4 | 3/3 exit=0 |

**PASS: 6/6 | FAIL: 0/6 | BLOQUEADO: 0/6**

---

## EVIDENCIAS STAGED

- _reports/testador/AR_169_07760d4/context.json  ← staged ✅
- _reports/testador/AR_169_07760d4/result.json   ← staged ✅
- _reports/testador/AR_170_07760d4/context.json  ← staged ✅
- _reports/testador/AR_170_07760d4/result.json   ← staged ✅
- _reports/testador/AR_171_07760d4/context.json  ← staged ✅
- _reports/testador/AR_171_07760d4/result.json   ← staged ✅
- _reports/testador/AR_172_07760d4/context.json  ← staged ✅
- _reports/testador/AR_172_07760d4/result.json   ← staged ✅
- _reports/testador/AR_173_07760d4/context.json  ← staged ✅
- _reports/testador/AR_173_07760d4/result.json   ← staged ✅
- _reports/testador/AR_174_07760d4/context.json  ← staged ✅
- _reports/testador/AR_174_07760d4/result.json   ← staged ✅

---

## WORKSPACE AO FINAL

- git diff --name-only = vazio (OK) ✅
- Testador NAO modificou codigo de produto.
- Testador NAO executou hb report, hb seal, git reset, git restore.

---

## NOTAS

- AR_169/170: run anterior BLOQUEADO_INFRA (workspace sujo). Re-executados com sucesso apos workspace limpo.
- hb verify sobrescreve context/result staged — re-staged apos cada verify (comportamento normal do pipeline).
- Validation commands fixados (ESC-001/ESC-002) pelo Arquiteto em sessao anterior.

---

## NEXT_ACTION

**Humano: hb seal para cada AR e depois commit.**

```
python scripts/run/hb_cli.py seal 169
python scripts/run/hb_cli.py seal 170
python scripts/run/hb_cli.py seal 171
python scripts/run/hb_cli.py seal 172
python scripts/run/hb_cli.py seal 173
python scripts/run/hb_cli.py seal 174
```
"""
Path("_reports/TESTADOR.yaml").write_text(content, encoding="utf-8")
print("OK")
