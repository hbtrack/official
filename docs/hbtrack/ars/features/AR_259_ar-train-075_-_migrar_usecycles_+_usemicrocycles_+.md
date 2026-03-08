# AR_259 — AR-TRAIN-075 — Migrar useCycles + useMicrocycles + useExercises para gerado

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Os hooks de ciclos, microciclos e exercicios usam clientes manuais (`trainings.ts` e `exercises.ts`). Esta AR migra os tres hooks centrais para os singletons gerados.

## ZONA 1 — useCycles.ts

Arquivo: `Hb Track - Frontend/src/lib/hooks/useCycles.ts`

Substituir chamadas de `trainingsService.getCycles*`, `.createCycle`, `.updateCycle`, `.deleteCycle`, `.getActiveCycles` por metodos de `cyclesApi` (TrainingCyclesApi gerado). Importar `cyclesApi` de `@/api/generated/api-instance`.

## ZONA 2 — useMicrocycles.ts

Arquivo: `Hb Track - Frontend/src/lib/hooks/useMicrocycles.ts`

Substituir chamadas de `trainingsService.getMicrocycles*`, `.createMicrocycle`, `.updateMicrocycle`, `.deleteMicrocycle`, `.getCurrentMicrocycle`, `.getMicrocycleSummary` por metodos de `microcyclesApi` (TrainingMicrocyclesApi gerado). Importar `microcyclesApi` de `@/api/generated/api-instance`.

## ZONA 3 — useExercises.ts

Arquivo: `Hb Track - Frontend/src/hooks/useExercises.ts`

Substituir chamadas de `getExercises`, `getExerciseById` (e outras de exercises.ts) por metodos de `exercisesApi`, `exerciseTagsApi` e `exerciseFavoritesApi`. Importar os tres singletons de `@/api/generated/api-instance`.

## Padrao geral

Para cada chamada manual:
1. Identificar o metodo correspondente no cliente gerado (consultar api.ts pelo nome da classe + operacoes CRUD da entidade)
2. Substituir a chamada, extraindo `.data` do AxiosResponse
3. Remover imports do cliente manual (manter apenas type-only se necessario)
4. Verificar que React Query keys e callbacks continuam funcionando com o novo formato de resposta

## Critérios de Aceite
AC1: useCycles.ts importa cyclesApi e nao chama trainingsService.getCycles*.
AC2: useMicrocycles.ts importa microcyclesApi e nao chama trainingsService.getMicrocycles*.
AC3: useExercises.ts importa exercisesApi/exerciseTagsApi/exerciseFavoritesApi e nao chama getExercises de exercises.ts.
AC4: npx tsc --noEmit exit=0.

## Write Scope
- Hb Track - Frontend/src/lib/hooks/useCycles.ts
- Hb Track - Frontend/src/lib/hooks/useMicrocycles.ts
- Hb Track - Frontend/src/hooks/useExercises.ts

## Validation Command (Contrato)
```
python -c "
import sys
from pathlib import Path
cy = Path('Hb Track - Frontend/src/lib/hooks/useCycles.ts').read_text(encoding='utf-8')
mi = Path('Hb Track - Frontend/src/lib/hooks/useMicrocycles.ts').read_text(encoding='utf-8')
ex = Path('Hb Track - Frontend/src/hooks/useExercises.ts').read_text(encoding='utf-8')
checks = [
  ('cyclesApi' in cy, 'AC1a: cyclesApi em useCycles'),
  ('trainingsService.getCycle' not in cy, 'AC1b: trainingsService removido de useCycles'),
  ('microcyclesApi' in mi, 'AC2a: microcyclesApi em useMicrocycles'),
  ('trainingsService.getMicrocycle' not in mi, 'AC2b: trainingsService removido de useMicrocycles'),
  ('exercisesApi' in ex, 'AC3a: exercisesApi em useExercises'),
  ('getExercises(' not in ex, 'AC3b: getExercises manual removido de useExercises'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC3 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_259/executor_main.log`

## Análise de Impacto
- **useCycles.ts**: Removido `trainingsService` do import; adicionado `cyclesApi` de `@/api/generated/api-instance`. 8 chamadas migradas: getCycles→listTrainingCyclesApiV1, createCycle→createTrainingCycleApiV1, updateCycle (×2)→updateTrainingCycleApiV1, deleteCycle (×2)→deleteTrainingCycleApiV1, getCycle→getTrainingCycleApiV1, getActiveCycles→getActiveCyclesApiV1.
- **useMicrocycles.ts**: Removido `trainingsService`; adicionado `microcyclesApi`. 9 chamadas migradas: getMicrocycles→listTrainingMicrocyclesApiV1, createMicrocycle→createTrainingMicrocycleApiV1, updateMicrocycle (×2), deleteMicrocycle (×2), getMicrocycle, getCurrentMicrocycle, getMicrocycleSummary.
- **useExercises.ts**: Removidos imports `getExercises, getExerciseById, getExerciseTags, addFavorite, removeFavorite, getFavorites, createExercise, updateExercise`; mantido `deleteExercise` (sem equivalente gerado); adicionados `exercisesApi, exerciseTagsApi, exerciseFavoritesApi`. 9 chamadas migradas.
- Sem alteração de contratos OpenAPI. Sem impacto em rotas BE. Sem alteração em React Query keys.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
cy = Path('Hb Track - Frontend/src/lib/hooks/useCycles.ts').read_text(encoding='utf-8')
mi = Path('Hb Track - Frontend/src/lib/hooks/useMicrocycles.ts').read_text(encoding='utf-8')
ex = Path('Hb Track - Frontend/src/hooks/useExercises.ts').read_text(encoding='utf-8')
checks = [
  ('cyclesApi' in cy, 'AC1a: cyclesApi em useCycles'),
  ('trainingsService.getCycle' not in cy, 'AC1b: trainingsService removido de useCycles'),
  ('microcyclesApi' in mi, 'AC2a: microcyclesApi em useMicrocycles'),
  ('trainingsService.getMicrocycle' not in mi, 'AC2b: trainingsService removido de useMicrocycles'),
  ('exercisesApi' in ex, 'AC3a: exercisesApi em useExercises'),
  ('getExercises(' not in ex, 'AC3b: getExercises manual removido de useExercises'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC3 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T21:16:13.057262+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_259/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
cy = Path('Hb Track - Frontend/src/lib/hooks/useCycles.ts').read_text(encoding='utf-8')
mi = Path('Hb Track - Frontend/src/lib/hooks/useMicrocycles.ts').read_text(encoding='utf-8')
ex = Path('Hb Track - Frontend/src/hooks/useExercises.ts').read_text(encoding='utf-8')
checks = [
  ('cyclesApi' in cy, 'AC1a: cyclesApi em useCycles'),
  ('trainingsService.getCycle' not in cy, 'AC1b: trainingsService removido de useCycles'),
  ('microcyclesApi' in mi, 'AC2a: microcyclesApi em useMicrocycles'),
  ('trainingsService.getMicrocycle' not in mi, 'AC2b: trainingsService removido de useMicrocycles'),
  ('exercisesApi' in ex, 'AC3a: exercisesApi em useExercises'),
  ('getExercises(' not in ex, 'AC3b: getExercises manual removido de useExercises'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC3 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-07T05:42:59.789772+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_259/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_259_571249d/result.json`

### Selo Humano em 571249d
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-07T18:00:37.731971+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_259_571249d/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_259/executor_main.log`
