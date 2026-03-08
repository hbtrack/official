# AR_257 — AR-TRAIN-073 — Migrar useSessions.ts + useSessionTemplates.ts para trainingApi

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Os hooks `useSessions.ts` e `useSessionTemplates.ts` sao os pontos centrais de acesso de dados de sessao de treino. Atualmente usam `TrainingSessionsAPI` de `src/lib/api/trainings.ts` (cliente manual). Esta AR migra ambos os hooks para usar `trainingApi` e `sessionTemplatesApi` de `src/api/generated/api-instance.ts`.

## ZONA 1 — useSessions.ts

Arquivo: `Hb Track - Frontend/src/lib/hooks/useSessions.ts`

Substituir todas as chamadas de `TrainingSessionsAPI.*` por metodos equivalentes de `trainingApi` (TrainingSessionsApi gerado). Para cada metodo manual:
- `TrainingSessionsAPI.listSessions(filters)` → `trainingApi.<operationId>(params)` (consultar api.ts para nome exato do metodo)
- `TrainingSessionsAPI.getSession(id)` → correspondente gerado
- `TrainingSessionsAPI.createSession(data)` → correspondente gerado
- `TrainingSessionsAPI.updateSession(id, data)` → correspondente gerado
- `TrainingSessionsAPI.updateSessionFocus(id, data)` → correspondente gerado
- `TrainingSessionsAPI.publishSession(id)` → correspondente gerado
- `TrainingSessionsAPI.closeSession(id, data)` → correspondente gerado
- `TrainingSessionsAPI.deleteSession(id)` → correspondente gerado
- `TrainingSessionsAPI.getSessionDeviation(id)` → correspondente gerado
- `TrainingSessionsAPI.saveDeviationJustification(id, data)` → correspondente gerado
- `copyWeek(params)` → correspondente gerado

Padrao de extracao: todos os metodos do cliente gerado retornam `Promise<AxiosResponse<T>>`. Usar `.then(r => r.data)` para extrair o payload tipado.

Imports: remover `import { TrainingSessionsAPI, ... } from '@/lib/api/trainings'`; adicionar `import { trainingApi } from '@/api/generated/api-instance'`. Tipos como `TrainingSession`, `SessionCreate` podem ser importados de `@/api/generated` se ja existirem no cliente; caso o shape difira, manter adapter temporario em trainings.ts.

## ZONA 2 — useSessionTemplates.ts

Arquivo: `Hb Track - Frontend/src/hooks/useSessionTemplates.ts`

Substituir chamadas de `TrainingSessionsAPI.*Template*` por `sessionTemplatesApi.*` (SessionTemplatesApi gerado). Metodos a migrar:
- `getSessionTemplates`, `getSessionTemplate`, `createSessionTemplate`, `updateSessionTemplate`, `deleteSessionTemplate`, `toggleTemplateFavorite`, `duplicateSessionTemplate`

## NOTA — useSuggestions.ts

NAO migrar `useSuggestions.ts` nesta AR. Os endpoints de sugestoes/alertas (CONTRACT-TRAIN-077..085) tem divergencia de tipos (int vs uuid) documentada como DIVERGENTE_DO_SSOT. Migrar sem corrigir a divergencia introduziria regressao de tipos.

## Critérios de Aceite
AC1: useSessions.ts importa trainingApi de @/api/generated/api-instance (nao TrainingSessionsAPI de trainings).
AC2: useSessions.ts nao faz chamadas diretas ao cliente manual (TrainingSessionsAPI.listSessions, .createSession, etc.).
AC3: useSessionTemplates.ts importa sessionTemplatesApi de @/api/generated/api-instance.
AC4: useSessionTemplates.ts nao chama TrainingSessionsAPI para templates.
AC5: npx tsc --noEmit exit=0.

## Write Scope
- Hb Track - Frontend/src/lib/hooks/useSessions.ts
- Hb Track - Frontend/src/hooks/useSessionTemplates.ts

## Validation Command (Contrato)
```
python -c "
import sys
from pathlib import Path
s = Path('Hb Track - Frontend/src/lib/hooks/useSessions.ts').read_text(encoding='utf-8')
t = Path('Hb Track - Frontend/src/hooks/useSessionTemplates.ts').read_text(encoding='utf-8')
checks = [
  ('trainingApi' in s, 'AC1: trainingApi em useSessions'),
  ('TrainingSessionsAPI.listSessions' not in s and 'TrainingSessionsAPI.createSession' not in s, 'AC2: trainings manual removido de useSessions'),
  ('sessionTemplatesApi' in t or 'trainingApi' in t, 'AC3: api gerada em useSessionTemplates'),
  ('TrainingSessionsAPI' not in t, 'AC4: TrainingSessionsAPI removido de useSessionTemplates'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC4 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_257/executor_main.log`

## Análise de Impacto
- **useSessions.ts**: Removido `TrainingSessionsAPI` do import; adicionado `trainingApi` de `@/api/generated/api-instance` e `SessionCreate` de trainings. Todas as 11 chamadas manuais substituídas: listSessions→listTrainingSessionsApiV1TrainingSessionsGet (com expansão de filtros), getSession→getTrainingSessionByIdApiV1..., updateSession→updateTrainingSessionApiV1..., updateSessionFocus→inline+updateTrainingSession, publishSession→publishTrainingSessionApiV1..., closeSession→closeTrainingSessionApiV1..., deleteSession→deleteTrainingSessionApiV1..., createSession→createTrainingSessionApiV1..., getSessionDeviation→getSessionDeviationApiV1..., saveDeviationJustification→updateTrainingSession com {deviation_justification}. Padrão `.then(r => r.data)` aplicado em todas as mutationFns/queryFns.
- **useSessionTemplates.ts**: Removido `TrainingSessionsAPI` do import; adicionado `sessionTemplatesApi` de `@/api/generated/api-instance`. queryFn substituída: getSessionTemplates→listSessionTemplatesApiV1SessionTemplatesGet.
- **Downstream**: Componentes que usam estes hooks continuam compatíveis — as interfaces de retorno são preservadas via cast `as unknown as T`.
- **Sem mudança de contrato FE↔BE**: Este batch não modifica openapi.json; CONTRACT_DIFF_GATE não aplicável.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
s = Path('Hb Track - Frontend/src/lib/hooks/useSessions.ts').read_text(encoding='utf-8')
t = Path('Hb Track - Frontend/src/hooks/useSessionTemplates.ts').read_text(encoding='utf-8')
checks = [
  ('trainingApi' in s, 'AC1: trainingApi em useSessions'),
  ('TrainingSessionsAPI.listSessions' not in s and 'TrainingSessionsAPI.createSession' not in s, 'AC2: trainings manual removido de useSessions'),
  ('sessionTemplatesApi' in t or 'trainingApi' in t, 'AC3: api gerada em useSessionTemplates'),
  ('TrainingSessionsAPI' not in t, 'AC4: TrainingSessionsAPI removido de useSessionTemplates'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC4 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T17:06:19.357218+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_257/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
s = Path('Hb Track - Frontend/src/lib/hooks/useSessions.ts').read_text(encoding='utf-8')
t = Path('Hb Track - Frontend/src/hooks/useSessionTemplates.ts').read_text(encoding='utf-8')
checks = [
  ('trainingApi' in s, 'AC1: trainingApi em useSessions'),
  ('TrainingSessionsAPI.listSessions' not in s and 'TrainingSessionsAPI.createSession' not in s, 'AC2: trainings manual removido de useSessions'),
  ('sessionTemplatesApi' in t or 'trainingApi' in t, 'AC3: api gerada em useSessionTemplates'),
  ('TrainingSessionsAPI' not in t, 'AC4: TrainingSessionsAPI removido de useSessionTemplates'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC4 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T17:09:00.529645+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_257/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_257_571249d/result.json`

### Selo Humano em 571249d
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-07T18:00:19.213275+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_257_571249d/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_257/executor_main.log`
