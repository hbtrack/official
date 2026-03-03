"""Append AR_169/170 report to _reports/EXECUTOR.md"""
from pathlib import Path

NEW_SECTION = """

---

# EXECUTOR REPORT — AR-TRAIN-003 Wellness FE (AR_169/170)

**Data**: 2026-02-28
**Protocol**: v1.3.0
**RUN_ID**: BATCH0-WELLNESS-FE-SEAL-20260228

## ANÁLISE DE IMPACTO

### AR_169 — Fix wellness.ts
- Arquivo único: `Hb Track - Frontend/src/lib/api/wellness.ts`
- DB changes: nenhum — apenas tipos TS e paths de chamada de API
- Cascata: WellnessPreForm.tsx usa WellnessPreInput (coberto por AR_170). WellnessHistoricalChart usa metric como string prop — não afetado.
- WELLNESS_PRE_PRESETS atualizado com novos nomes (fatigue_pre, readiness_score, sleep_hours)
- Risco nulo — FE-only, sem alteração de lógica de negócio

### AR_170 — Fix WellnessPreForm.tsx
- Arquivo único: `Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx`
- DB changes: nenhum — estado local de formulário e labels UI
- Depende de AR_169 (já executada). Mudanças: estado inicial reescrito, slider Humor removido, sleep_quality min=1/max=5, useEffect de carga atualizado, hasCriticalValues com novos nomes
- Risco nulo — FE-only, arquivo isolado

## RESULTADOS

### AR_169 — ✅ PASS

```
EXECUTOR_REPORT:
- ar_id: 169
- validation_exit_code: 0
- behavior_hash: 3b7525c5cb81a853948f49f26064c0e5f6cb9940dde7bf70e0a3545ef0257d00
- timestamp_utc: 2026-02-28T10:41:44.903714+00:00
- evidence_path: docs/hbtrack/evidence/AR_169/executor_main.log
- stdout: |
    PASS: wellness.ts no tsc errors
    PASS: all checks OK - 9 checks
- method: smart runner (temp/_hb_report_helper.py)
- note: validation_command limpo (Windows-compatível); hb_cli.py report requer
        parâmetro explícito — smart runner lê AR file diretamente.
```

### AR_170 — ✅ PASS

```
EXECUTOR_REPORT:
- ar_id: 170
- validation_exit_code: 0
- behavior_hash: 98ff43e0d607dc3c16eace9b98f476ed01170e48475d69f0bb49e2134e6187b1
- timestamp_utc: 2026-02-28T10:41:57.710966+00:00
- evidence_path: docs/hbtrack/evidence/AR_170/executor_main.log
- stdout: |
    PASS: WellnessPreForm checks OK
    PASS: WellnessPreForm tsc ok
- method: smart runner (temp/_hb_report_helper.py)
- note: ESC-002-WELLNESS corrigido (embedded double-quote "'mood'" removido do
        validation_command). Hash idêntico à sessão anterior — código correto.
```

## RESUMO

| AR | Resultado | Hash (8) | Evidence |
|---|---|---|---|
| AR_169 | ✅ PASS (exit=0) | `3b7525c5` | `docs/hbtrack/evidence/AR_169/executor_main.log` |
| AR_170 | ✅ PASS (exit=0) | `98ff43e0` | `docs/hbtrack/evidence/AR_170/executor_main.log` |

**PASS: 2/2**

## STAGED (isolamento de domínio)

```
docs/hbtrack/evidence/AR_169/executor_main.log
docs/hbtrack/evidence/AR_170/executor_main.log
docs/hbtrack/ars/features/AR_169_fix_wellness.ts_paths_canonicos_+_wellnesspreinput.md
docs/hbtrack/ars/features/AR_170_fix_wellnesspreform.tsx_campos_ui_alinhados_ao_wel.md
```

## WORKSPACE CLEAN

- tracked-unstaged (do domínio AR_169/170): zero ✅
- Staged: apenas 4 artefatos acima (evidence + AR files)
- Código de produto (wellness.ts, WellnessPreForm.tsx): staged do ciclo anterior, não reescrito neste ciclo

## ESCALAÇÕES

Nenhuma. AR_169 e AR_170 passaram com exit=0. Prontos para Testador.

"""

p = Path("_reports/EXECUTOR.md")
content = p.read_text(encoding="utf-8")
p.write_text(content + NEW_SECTION, encoding="utf-8")
print(f"OK --- {len(content + NEW_SECTION)} chars total")
