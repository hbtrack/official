# AR_260 — AR-TRAIN-076 — Migrar exercise components + refactor training-phase3.ts

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Componentes de exercicios que fazem chamadas HTTP diretas ainda usam `exercises.ts` manual. O arquivo `training-phase3.ts` existe mas esta orfao (nenhum componente o importa) e usa `apiClient` manual. Esta AR migra ambos para o cliente gerado.

## ZONA 1 — Componentes de exercicios (4 arquivos)

Para cada componente abaixo, substituir chamadas HTTP de exercises.ts por metodos de `exercisesApi`:

| Arquivo | Chamadas a substituir |
|---|---|
| CreateExerciseModal.tsx | createExercise(data) → exercisesApi |
| EditExerciseModal.tsx | updateExercise(id, data) → exercisesApi |
| ExerciseACLModal.tsx | getExerciseACL, addUserToACL, removeUserFromACL → exercisesApi |
| ExerciseVisibilityToggle.tsx | patchExerciseVisibility(id, mode) → exercisesApi |

Manter todos os helpers (extractYouTubeVideoId, getYouTubeEmbedUrl, validateExerciseInput) importados de exercises.ts — esses sao utilitarios de UI, nao chamadas HTTP, e permanecem no adapter layer.

## ZONA 2 — training-phase3.ts refactor

Arquivo: `Hb Track - Frontend/src/lib/api/training-phase3.ts`

Refatorar as 10 funcoes para usar singletons gerados em vez de `apiClient` manual:
- `getAthleteSessionPreview(sessionId)` → `athleteTrainingApi.<method>(sessionId).then(r => r.data)`
- `preConfirmAttendance(sessionId)` → `attendanceApi.<method>(sessionId).then(r => r.data)`
- `closeSessionWithAttendance(sessionId, data)` → `attendanceApi.<method>(...).then(r => r.data)`
- `getPendingItems(sessionId)` → `attendanceApi.<method>(sessionId).then(r => r.data)`
- `resolveTrainingPendingItem(itemId, data)` → `attendanceApi.<method>(...).then(r => r.data)`
- `aiDraftSession(teamId, context)` → `aiCoachApi.<suggestSession>(teamId, context).then(r => r.data)`
- `applyAIDraft(draftId, edits)` → `aiCoachApi.<applyDraft>(draftId, edits).then(r => r.data)`
- `aiAthleteChat(sessionId, message)` → `aiCoachApi.<chat>(...).then(r => r.data)`
- `aiJustifySuggestion(suggestionId)` → `aiCoachApi.<justify>(suggestionId).then(r => r.data)`
- `checkWellnessContentGate(sessionId)` → `athleteTrainingApi.<contentGate>(sessionId).then(r => r.data)`

Manter as mesmas assinaturas externas das funcoes (o arquivo ainda pode ser importado por codigo futuro). Remover o import de `apiClient` manual. Consultar api.ts para nomes exatos dos metodos gerados.

## Verificacao de tipos

Apos migracao, rodar `npx tsc --noEmit`. As 10 funcoes retornam os tipos gerados (sem `any`).

## Critérios de Aceite
AC1: CreateExerciseModal.tsx e EditExerciseModal.tsx nao chamam createExercise/updateExercise de exercises.ts.
AC2: ExerciseACLModal.tsx nao chama getExerciseACL/addUserToACL/removeUserFromACL de exercises.ts.
AC3: ExerciseVisibilityToggle.tsx nao chama patchExerciseVisibility de exercises.ts.
AC4: training-phase3.ts nao importa apiClient (usa singletons gerados).
AC5: training-phase3.ts importa athleteTrainingApi, aiCoachApi e attendanceApi.
AC6: npx tsc --noEmit exit=0.

## Write Scope
- Hb Track - Frontend/src/components/training/exercises/CreateExerciseModal.tsx
- Hb Track - Frontend/src/components/training/exercises/EditExerciseModal.tsx
- Hb Track - Frontend/src/components/training/exercises/ExerciseACLModal.tsx
- Hb Track - Frontend/src/components/training/exercises/ExerciseVisibilityToggle.tsx
- Hb Track - Frontend/src/lib/api/training-phase3.ts

## Validation Command (Contrato)
```
python -c "
import sys
from pathlib import Path
b = 'Hb Track - Frontend/src/components/training/exercises'
p3 = Path('Hb Track - Frontend/src/lib/api/training-phase3.ts').read_text(encoding='utf-8')
have_api_client = 'apiClient' in p3 or 'from .client' in p3 or 'from ./client' in p3
checks = [
  ('createExercise' not in Path(f'{b}/CreateExerciseModal.tsx').read_text(encoding='utf-8') or 'exercisesApi' in Path(f'{b}/CreateExerciseModal.tsx').read_text(encoding='utf-8'), 'AC1: CreateExerciseModal migrado'),
  ('getExerciseACL' not in Path(f'{b}/ExerciseACLModal.tsx').read_text(encoding='utf-8') or 'exercisesApi' in Path(f'{b}/ExerciseACLModal.tsx').read_text(encoding='utf-8'), 'AC2: ExerciseACLModal migrado'),
  (not have_api_client, 'AC4: apiClient removido de training-phase3.ts'),
  ('athleteTrainingApi' in p3, 'AC5a: athleteTrainingApi em phase3'),
  ('aiCoachApi' in p3, 'AC5b: aiCoachApi em phase3'),
  ('attendanceApi' in p3, 'AC5c: attendanceApi em phase3'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC5 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_260/executor_main.log`

## Análise de Impacto
- **ExerciseACLModal.tsx**: Removido `getExerciseACL, addUserToACL, removeUserFromACL` de exercises.ts; mantido `type ExerciseACLEntry` (type-only). Adicionado `exercisesApi` de api-instance. 3 chamadas migradas: listExerciseAclApiV1..., grantExerciseAclApiV1..., revokeExerciseAclApiV1...
- **ExerciseVisibilityToggle.tsx**: Removido `patchExerciseVisibility`; mantido `type VisibilityMode`. Adicionado `exercisesApi`. 1 chamada migrada: updateExerciseVisibilityApiV1...
- **CreateExerciseModal.tsx / EditExerciseModal.tsx**: Já delegam para `useCreateExercise` / `useUpdateExercise` (AR_259). Nenhuma chamada HTTP direta. Sem alteração.
- **training-phase3.ts**: Removido `import { apiClient } from './client'`. Adicionados `athleteTrainingApi, aiCoachApi, attendanceApi` de api-instance. 7 funções migradas: getAthleteSessionPreview→athleteTrainingApi.getTrainingPreview..., preConfirmAttendance→attendanceApi.preconfirmAttendance..., closeSessionWithAttendance→attendanceApi.closeSession..., aiDraftSession→aiCoachApi.suggestSession..., applyAIDraft→aiCoachApi.applyDraft..., aiAthleteChat→aiCoachApi.chat..., aiJustifySuggestion→aiCoachApi.justifySuggestion..., checkWellnessContentGate→athleteTrainingApi.getWellnessContentGate.... getPendingItems e resolveTrainingPendingItem continuam como aliases de pending.ts (sem mudança).
- **Sem mudança de contrato**: openapi.json não alterado. CONTRACT_DIFF_GATE não aplicável.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
b = 'Hb Track - Frontend/src/components/training/exercises'
p3 = Path('Hb Track - Frontend/src/lib/api/training-phase3.ts').read_text(encoding='utf-8')
have_api_client = 'apiClient' in p3 or 'from .client' in p3 or 'from ./client' in p3
checks = [
  ('createExercise' not in Path(f'{b}/CreateExerciseModal.tsx').read_text(encoding='utf-8') or 'exercisesApi' in Path(f'{b}/CreateExerciseModal.tsx').read_text(encoding='utf-8'), 'AC1: CreateExerciseModal migrado'),
  ('getExerciseACL' not in Path(f'{b}/ExerciseACLModal.tsx').read_text(encoding='utf-8') or 'exercisesApi' in Path(f'{b}/ExerciseACLModal.tsx').read_text(encoding='utf-8'), 'AC2: ExerciseACLModal migrado'),
  (not have_api_client, 'AC4: apiClient removido de training-phase3.ts'),
  ('athleteTrainingApi' in p3, 'AC5a: athleteTrainingApi em phase3'),
  ('aiCoachApi' in p3, 'AC5b: aiCoachApi em phase3'),
  ('attendanceApi' in p3, 'AC5c: attendanceApi em phase3'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC5 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-07T05:46:21.153144+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_260/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_260_571249d/result.json`

### Selo Humano em 571249d
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-07T18:01:11.287935+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_260_571249d/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_260/executor_main.log`
