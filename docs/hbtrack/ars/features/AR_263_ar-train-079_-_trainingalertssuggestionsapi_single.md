# AR_263 — AR-TRAIN-079 — trainingAlertsSuggestionsApi singleton + CONTRACT 5.10 fix

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Esta AR tem duas zonas de atuação complementares.

## ZONA 1 — api-instance.ts: adicionar trainingAlertsSuggestionsApi singleton

Arquivo: `Hb Track - Frontend/src/api/generated/api-instance.ts`

Adicionar import de `TrainingAlertsSuggestionsApi` ao bloco de imports existente, seguindo o mesmo padrao das demais classes. Adicionar singleton `trainingAlertsSuggestionsApi` apos os singletons existentes (`attendanceApi` e linha do default export):

```typescript
import {
  ...,
  TrainingAlertsSuggestionsApi
} from '.';

// ... singletons existentes ...
export const trainingAlertsSuggestionsApi = new TrainingAlertsSuggestionsApi(apiConfig, apiConfig.basePath, axiosInstance);
```

Este singleton expõe CONTRACT-TRAIN-077..085 (alertas e sugestões de monitoramento Step18). Padrão de uso: `trainingAlertsSuggestionsApi.getActiveAlertsApi....(teamId).then(r => r.data)`.

NAO alterar os singletons existentes. NAO editar api.ts, base.ts, common.ts, configuration.ts — sao artefatos gerados.

Nota sobre useSuggestions.ts: O hook `useSuggestions.ts` usa `TrainingSuggestionsAPI` de `trainings.ts` que chama `/training-suggestions` — endpoint de recomendacoes de planejamento do ROTEADOR INATIVO `training_suggestions.py`. NAO existe classe gerada correspondente (o roteador nao esta no openapi.json). Porta de saida: CAP-001 (autorizacao PO necessaria). NAO migrar useSuggestions.ts nesta AR.

## ZONA 2 — TRAINING_FRONT_BACK_CONTRACT.md: sync secao 5.10

Arquivo: `docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md`

A secao 5.10 (Alertas e Sugestoes Step 18) ainda esta marcada como DIVERGENTE_DO_SSOT com a nota que `alert_id:int` e `suggestion_id:int`. Isso e STALE — AR-TRAIN-001 (AR_126, VERIFICADO) ja corrigiu o openapi.json para usar uuid (string). O cliente gerado `TrainingAlertsSuggestionsApi` usa `string` para todos os IDs. A secao 5.10 deve ser sincronizada.

Mudancas na secao 5.10:
1. Alterar header de status: `Status: **DIVERGENTE_DO_SSOT**` → `Status: **IMPLEMENTADO**`
2. Atualizar o bloco SSOT DB: substituir nota de divergencia por nota de resolucao:
   - `alert_id: uuid (string) — corrigido por AR-TRAIN-001 (AR_126, VERIFICADO).`
   - `suggestion_id: uuid (string) — corrigido por AR-TRAIN-001 (AR_126, VERIFICADO).`
   - `team_id: uuid (string) — corrigido por AR-TRAIN-001.`
3. Atualizar tabela de contratos: mudar coluna Status de `DIVERGENTE_DO_SSOT` para `IMPLEMENTADO` em todos os 9 contratos (CONTRACT-077..085).
4. Adicionar nota de cliente gerado: `Cliente FE gerado: trainingAlertsSuggestionsApi (TrainingAlertsSuggestionsApi) adicionado em AR-TRAIN-079 (Batch 34).`
5. Adicionar nota sobre useSuggestions.ts: `useSuggestions.ts — DIVERGENTE_DO_SSOT: chama /training-suggestions (roteador inativo, nao-canonico). Deferred a CAP-001. NAO usa CONTRACT-077..085.`

## Critérios de Aceite
AC1: api-instance.ts exporta trainingAlertsSuggestionsApi (instancia de TrainingAlertsSuggestionsApi).
AC2: api-instance.ts importa TrainingAlertsSuggestionsApi de '.'.
AC3: TRAINING_FRONT_BACK_CONTRACT.md secao 5.10 nao contem mais 'DIVERGENTE_DO_SSOT' nos status das linhas de contratos.
AC4: TRAINING_FRONT_BACK_CONTRACT.md secao 5.10 contem 'IMPLEMENTADO' para os contratos 077..085.
AC5: npx tsc --noEmit exit=0 no projeto FE.

## Write Scope
- Hb Track - Frontend/src/api/generated/api-instance.ts
- docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md

## Validation Command (Contrato)
```
python -c "
import sys
from pathlib import Path
inst = Path('Hb Track - Frontend/src/api/generated/api-instance.ts').read_text(encoding='utf-8')
c510_start = 'Alertas e Sugest'
c = Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text(encoding='utf-8')
sec = c[c.find(c510_start):c.find('5.11')]
checks = [
  ('trainingAlertsSuggestionsApi' in inst, 'AC1: singleton presente'),
  ('TrainingAlertsSuggestionsApi' in inst, 'AC2: import presente'),
  ('DIVERGENTE_DO_SSOT' not in sec, 'AC3: DIVERGENTE removido de 5.10'),
  ('IMPLEMENTADO' in sec, 'AC4: IMPLEMENTADO em 5.10'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC4 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_263/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- "Hb Track - Frontend/src/api/generated/api-instance.ts"
git checkout -- docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- TrainingAlertsSuggestionsApi pode ter nome diferente em api.ts — confirmar antes via grep 'export class Training' em api.ts.
- Secao 5.10 do CONTRACT.md pode ter texto ligeiramente diferente do esperado — ler arquivo antes de editar.
- Manter todos os outros imports e exports existentes em api-instance.ts sem alteracao.

## Análise de Impacto

**ZONA 1 — api-instance.ts:**
- Arquivo: `Hb Track - Frontend/src/api/generated/api-instance.ts`
- Impacto: adicionar `TrainingAlertsSuggestionsApi` no bloco import existente + novo singleton `trainingAlertsSuggestionsApi` após `attendanceApi`
- Classe confirmada em `api.ts` linha 56969: `export class TrainingAlertsSuggestionsApi extends BaseAPI`
- Zero risco de quebra: nenhum export existente será alterado; somente adição
- tsc: tipagem compatível (classe gerada pelo OpenAPI Generator)

**ZONA 2 — TRAINING_FRONT_BACK_CONTRACT.md §5.10:**
- Arquivo puramente documental — zero impacto de runtime
- Seção 5.10 atual: `Status: DIVERGENTE_DO_SSOT` (stale pós AR-TRAIN-001 AR_126)
- Mudanças: header status → IMPLEMENTADO; SSOT DB → notas de resolução; 9 contratos (077..085) → IMPLEMENTADO
- Adicionar nota de singleton gerado + nota useSuggestions.ts deferred CAP-001

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
inst = Path('Hb Track - Frontend/src/api/generated/api-instance.ts').read_text(encoding='utf-8')
c510_start = 'Alertas e Sugest'
c = Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text(encoding='utf-8')
sec = c[c.find(c510_start):c.find('5.11')]
checks = [
  ('trainingAlertsSuggestionsApi' in inst, 'AC1: singleton presente'),
  ('TrainingAlertsSuggestionsApi' in inst, 'AC2: import presente'),
  ('DIVERGENTE_DO_SSOT' not in sec, 'AC3: DIVERGENTE removido de 5.10'),
  ('IMPLEMENTADO' in sec, 'AC4: IMPLEMENTADO em 5.10'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC4 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-07T20:09:08.939516+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_263/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
inst = Path('Hb Track - Frontend/src/api/generated/api-instance.ts').read_text(encoding='utf-8')
c510_start = 'Alertas e Sugest'
c = Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text(encoding='utf-8')
sec = c[c.find(c510_start):c.find('5.11')]
checks = [
  ('trainingAlertsSuggestionsApi' in inst, 'AC1: singleton presente'),
  ('TrainingAlertsSuggestionsApi' in inst, 'AC2: import presente'),
  ('DIVERGENTE_DO_SSOT' not in sec, 'AC3: DIVERGENTE removido de 5.10'),
  ('IMPLEMENTADO' in sec, 'AC4: IMPLEMENTADO em 5.10'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC4 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-07T20:10:20.461369+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_263/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 571249d
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "
import sys
from pathlib import Path
inst = Path('Hb Track - Frontend/src/api/generated/api-instance.ts').read_text(encoding='utf-8')
c510_start = 'Alertas e Sugest'
c = Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text(encoding='utf-8')
sec = c[c.find(c510_start):c.find('5.11')]
checks = [
  ('trainingAlertsSuggestionsApi' in inst, 'AC1: singleton presente'),
  ('TrainingAlertsSuggestionsApi' in inst, 'AC2: import presente'),
  ('DIVERGENTE_DO_SSOT' not in sec, 'AC3: DIVERGENTE removido de 5.10'),
  ('IMPLEMENTADO' in sec, 'AC4: IMPLEMENTADO em 5.10'),
]
bad=[m for ok,m in checks if not ok]
print('FAIL:',bad) or sys.exit(1) if bad else print('AC1..AC4 PASS')
" && cd "Hb Track - Frontend" && npx tsc --noEmit 2>&1 | tail -3`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-07T20:12:13.985111+00:00
**Behavior Hash**: c7950ee5238ba6845dd89c9bc183f2c44810fc6427b78bfd5cd97290aaad941f
**Evidence File**: `docs/hbtrack/evidence/AR_263/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 571249d
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_263_571249d/result.json`

### Selo Humano em 571249d
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-08T04:58:39.171674+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_263_571249d/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_263/executor_main.log`
