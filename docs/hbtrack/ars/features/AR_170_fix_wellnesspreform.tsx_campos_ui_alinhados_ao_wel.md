# AR_170 — Fix WellnessPreForm.tsx: campos UI alinhados ao WellnessPreInput corrigido

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Atualizar src/components/training/wellness/WellnessPreForm.tsx para usar os campos atualizados pela Task 162.

=== 1. Estado inicial do formulario ===
Atual (usando campos antigos):
```typescript
// Linha ~69 (aproximado)
sleep_quality: 7,
fatigue_level: 5,  // OBSOLETO
stress_level: 4,
muscle_soreness: 4,
mood: 7,           // OBSOLETO
readiness: 7,      // OBSOLETO
```

Corrigir para (campos SSOT-aligned):
```typescript
sleep_hours: 7.0,        // NOVO campo obrigatorio
sleep_quality: 3,        // range 1-5 (ajustar para valor medio do range)
fatigue_pre: 5,          // renomeado
stress_level: 4,
muscle_soreness: 4,
readiness_score: 7,      // renomeado, agora opcional
```

=== 2. Existing wellness load (linha ~87) ===
Quando carrega wellness existente:
- `existing.sleep_quality` -> manter OK
- `existing.fatigue_level` -> mudar para `existing.fatigue_pre`
- `existing.mood` -> REMOVER (DB nao tem campo mood no wellness_pre)
- `existing.readiness` -> mudar para `existing.readiness_score`
- `existing.sleep_hours` -> adicionar (carregar se existir)

=== 3. Sliders e handlers ===
Atualizar todos os setValues que usam campos antigos:
- `fatigue_level: v` -> `fatigue_pre: v`
- `mood: v` -> REMOVER este slider/handler
- `readiness: v` -> `readiness_score: v`

=== 4. ADICIONAR campo sleep_hours na UI ===
Adicionar um input numerico ou slider para 'Horas de sono' (sleep_hours):
- Label: 'Horas de sono'
- Range: 0..24, step 0.5 ou 1
- Tipo: input number ou slider com step 0.5
- Required (campo obrigatorio no DB)
- Handler: `(v) => setValues(prev => ({ ...prev, sleep_hours: v }))`

=== 5. sleep_quality slider ===
Atual provavelmente usa range 0-10. Corrigir para range 1-5 (ANCORA: ck_wellness_pre_sleep_quality: sleep_quality >= 1 AND <= 5). Ajustar min/max do slider.

=== 6. Presets (WELLNESS_PRE_PRESETS) ===
Presets ja foram corrigidos na Task 162. WellnessPreForm so precisa aplicar os preset.values no setValues -- verificar que os campos dos presets batem com os do estado local.

=== 7. GARANTIR: athlete_id NAO enviado ===
Nao incluir athlete_id no payload enviado. O submitWellnessPre (corrigido na Task 162) nao aceita athlete_id em WellnessPreInput. Verificar que form state nao tem athlete_id na composicao do payload.

ARQUIVOS A MODIFICAR:
- Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx

## Critérios de Aceite
1) Estado inicial do form inclui sleep_hours e NAO inclui fatigue_level nem mood.
2) Handler para sleep_hours presente na UI (input ou slider).
3) sleep_quality slider usa range 1-5 (min=1, max=5).
4) Nenhum campo athlete_id no form state ou payload enviado.
5) Carga de wellness existente usa fatigue_pre, readiness_score (nao fatigue_level/readiness).
6) TypeScript compila sem erros no arquivo.

## Write Scope
- Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx

## Validation Command (Contrato)
```
cd "Hb Track - Frontend" && python -c "import sys; c=open('src/components/training/wellness/WellnessPreForm.tsx', encoding='utf-8').read(); checks=[('sleep_hours' in c, 'sleep_hours in form'), ('fatigue_pre' in c, 'fatigue_pre in form'), ('fatigue_level' not in c, 'fatigue_level removed from form'), (' mood: ' not in c, 'mood removed from form'), ('readiness_score' in c, 'readiness_score in form'), ('readiness:' not in c or 'readiness_score' in c, 'readiness renamed to readiness_score'), ('athlete_id' not in c.split('handleSubmit')[1].split('submitWellnessPre')[0] if 'handleSubmit' in c and 'submitWellnessPre' in c else True, 'no athlete_id in submit payload')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: WellnessPreForm checks OK') if not failed else sys.exit('FAIL: '+str(failed))" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'WellnessPreForm' in l and 'error TS' in l]; print('PASS: WellnessPreForm tsc ok') if not errs else sys.exit('FAIL WellnessPreForm tsc: '+chr(10).join(errs[:5]))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_170/executor_main.log`

## Notas do Arquiteto
Esta task depende da Task 162 (wellness.ts). Executor deve rodar Task 162 primeiro. ANCORA: ck_wellness_pre_sleep_quality CHECK: sleep_quality >= 1 AND <= 5 (nao 0-10). ANCORA: sleep_hours NOT NULL (obrigatorio no DB).

## Riscos
- Slider de sleep_hours pode precisar de componente adequado (Input numerico vs Slider); Executor escolhe o mais adequado mantendo UX consistente
- sleep_quality range mudando de 0-10 para 1-5 pode quebrar presets que usavam valores > 5
- Se WellnessPreForm usa TypeScript strict mode, remover campo mood pode gerar TS error se usado em algum discriminated union -- verificar

## Análise de Impacto
Arquivo único: `Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx`.
DB changes: nenhum — estado local de formulário e labels UI.
Depende de AR_169 (wellness.ts) já executada. Mudanças: estado inicial reescrito (sleep_hours, fatigue_pre, readiness_score), slider Humor removido, sleep_quality min=1/max=5, useEffect de carga atualizado, hasCriticalValues com novos nomes. Sem alteração de lógica de submit. Risco nulo — FE-only, arquivo isolado.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 07760d4
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Frontend" && python -c "import sys; c=open('src/components/training/wellness/WellnessPreForm.tsx', encoding='utf-8').read(); checks=[('sleep_hours' in c, 'sleep_hours in form'), ('fatigue_pre' in c, 'fatigue_pre in form'), ('fatigue_level' not in c, 'fatigue_level removed from form'), (' mood: ' not in c, 'mood removed from form'), ('readiness_score' in c, 'readiness_score in form'), ('readiness:' not in c or 'readiness_score' in c, 'readiness renamed to readiness_score'), ('athlete_id' not in c.split('handleSubmit')[1].split('submitWellnessPre')[0] if 'handleSubmit' in c and 'submitWellnessPre' in c else True, 'no athlete_id in submit payload')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: WellnessPreForm checks OK') if not failed else sys.exit('FAIL: '+str(failed))" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'WellnessPreForm' in l and 'error TS' in l]; print('PASS: WellnessPreForm tsc ok') if not errs else sys.exit('FAIL WellnessPreForm tsc: '+chr(10).join(errs[:5]))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T10:41:57.710966+00:00
**Behavior Hash**: 98ff43e0d607dc3c16eace9b98f476ed01170e48475d69f0bb49e2134e6187b1
**Evidence File**: `docs/hbtrack/evidence/AR_170/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 07760d4
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_170_07760d4/result.json`

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T17:32:46.991171+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_170_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_170/executor_main.log`
