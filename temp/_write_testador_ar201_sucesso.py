"""Escreve _reports/TESTADOR.yaml com resultado SUCESSO para AR_201 e AR_200."""
import os
os.chdir(r"c:\HB TRACK")

content = """# TESTADOR.yaml — SUCESSO

| Campo | Valor |
|---|---|
| **RUN_ID** | TESTADOR-AR_201+AR_200-b123a58 |
| **AR_IDs** | AR_201, AR_200 |
| **Data** | 2026-03-02 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **RESULT** | ✅ SUCESSO |
| **CONSISTENCY** | OK |
| **TRIPLE_CONSISTENCY** | 3/3 hashes idênticos (ambas ARs) |

---

## Pré-condições avaliadas

| Pré-condição | Status |
|---|---|
| AR_201 existe | ✅ OK |
| AR_201 tem Validation Command não vazio | ✅ OK |
| Evidence `docs/hbtrack/evidence/AR_201/executor_main.log` existe | ✅ OK |
| Evidence AR_201 STAGED | ✅ OK |
| Evidence AR_200 STAGED | ✅ OK |
| Workspace limpo (tracked-unstaged vazio) | ✅ OK |
| Kanban em fase compatível | ✅ OK |

---

## Resultado Triple-run

### AR_201

| Run | Exit Code | Hash |
|---|---|---|
| 1/3 | 0 | `29fff797fd5a052f` |
| 2/3 | 0 | `29fff797fd5a052f` |
| 3/3 | 0 | `29fff797fd5a052f` |

**Consistency**: ✅ OK — hashes idênticos  
**Validation output**: `PASS: AR_200 validation_command corrigida + executor_main.log Exit Code: 0`

### AR_200

| Run | Exit Code | Hash |
|---|---|---|
| 1/3 | 0 | `1395a5b2bd65d917` |
| 2/3 | 0 | `1395a5b2bd65d917` |
| 3/3 | 0 | `1395a5b2bd65d917` |

**Consistency**: ✅ OK — hashes idênticos  
**Validation output**: `PASS: 10 evidencias criadas com AR_200 + TEST_MATRIX v1.7.0 + NOT_RUN removido`

---

## Evidências Testador Staged

```
_reports/testador/AR_201_b123a58/context.json  ✅ staged
_reports/testador/AR_201_b123a58/result.json   ✅ staged
_reports/testador/AR_200_b123a58/context.json  ✅ staged
_reports/testador/AR_200_b123a58/result.json   ✅ staged
```

---

## NEXT_ACTION

**→ Humano**: `hb seal 201` → `hb seal 200` (nesta ordem)
"""

with open("_reports/TESTADOR.yaml", "w", encoding="utf-8") as f:
    f.write(content)
print("TESTADOR.yaml written OK")
