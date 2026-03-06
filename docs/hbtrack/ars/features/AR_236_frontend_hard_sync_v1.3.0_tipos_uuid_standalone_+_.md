# AR_236 — Frontend Hard Sync v1.3.0: tipos UUID/standalone + stubs CONTRACT-096..105 (AR-TRAIN-052)

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
Sincronizar a camada Frontend com o contrato v1.3.0 e invariantes v1.5.0 do Backend estável. Organizado em 5 zonas:

## Zona 1 — Tipagem canônica (3 arquivos existentes)

### Z1-A: src/types/athlete-canonical.ts
Linha ~40: `person_id: string` está presente mas o Backend retorna `athlete.id` (UUID) como campo primário (TRAINING_CLOSSARY.yaml: `athlete_id = uuid`).
- Adicionar `id: string` ao interface `Athlete` (campo obrigatório, UUID canônico).
- Manter `person_id?: string` como deprecated (opcional) para não quebrar componentes existentes.
- AC-001: arquivo contém `id: string` no bloco `Athlete`.

### Z1-B: src/lib/api/exercises.ts
- `VisibilityMode` (linha 33): atualizar para incluir `'public'` SE o openapi.json/ExerciseVisibilityMode enum incluir esse valor (verificar `python -c "import json; api=json.load(open('Hb Track - Backend/docs/ssot/openapi.json')); print(api['components']['schemas'].get('VisibilityMode', api['components']['schemas'].get('ExerciseVisibilityMode', {})))"`).
- `ExerciseInput` (linha 81): adicionar campos:
  ```typescript
  scope?: ExerciseScope;          // 'SYSTEM' | 'ORG'
  visibility_mode?: VisibilityMode; // default: 'restricted' (Backend aplica server_default)
  organization_id?: string;       // uuid — injetar da org do usuário logado
  ```
- `ExerciseFilters` (linha 72): adicionar `organization_id?: string` para filtragem por organização.
- AC-002: `scope?: ExerciseScope` presente em `ExerciseInput`.

### Z1-C: src/lib/api/trainings.ts
- `TrainingSession` interface (linha ~94): adicionar campo `standalone: boolean` (INV-TRAIN-057: sessão pode existir fora de microciclo).
- AC-003: `standalone` presente em `TrainingSession`.

## Zona 2 — Stubs de API para FASE_3 (1 arquivo novo)

### Z2: src/lib/api/training-phase3.ts (CRIAR NOVO)
Criar arquivo com stubs tipados para todos os endpoints FASE_3:

```typescript
// CONTRACT-TRAIN-096
export async function getAthleteSessionPreview(sessionId: string): Promise<AthleteSessionPreview>
// GET /api/v1/athlete/training-sessions/{session_id}/preview

// CONTRACT-TRAIN-097
export async function preConfirmAttendance(sessionId: string, athleteId?: string): Promise<{status: string, is_official: boolean}>
// POST /api/v1/training-sessions/{session_id}/pre-confirm

// CONTRACT-TRAIN-098
export async function closeSessionWithAttendance(sessionId: string, data: CloseSessionInput): Promise<{closed: boolean, pending_items: PendingItem[]}>
// POST /api/v1/training-sessions/{session_id}/close

// CONTRACT-TRAIN-099/100 — verificar se pending.ts já cobre (endpoints: GET /training/pending-items, PATCH /training/pending-items/{item_id}/resolve)
// Se pending.ts usa URLs diferentes → corrigir pending.ts + re-exportar aqui como alias

// CONTRACT-TRAIN-101
export async function aiDraftSession(teamId: string, context: object): Promise<{draft_id: string, suggested_session: object, justification: string}>
// POST /api/v1/ai-coach/draft-session

// CONTRACT-TRAIN-102
export async function applyAIDraft(draftId: string, edits?: object): Promise<{training_session_id: string, applied: boolean}>
// PATCH /api/v1/ai-coach/draft-session/{draft_id}/apply

// CONTRACT-TRAIN-103
export async function aiAthleteChat(sessionId: string, message: string): Promise<{response: string, type: string}>
// POST /api/v1/ai-coach/athlete-chat

// CONTRACT-TRAIN-104
export async function aiJustifySuggestion(suggestionId: string): Promise<{justification: string, references: string[]}>
// POST /api/v1/ai-coach/justify-suggestion

// CONTRACT-TRAIN-105
export async function checkWellnessContentGate(sessionId: string): Promise<{has_wellness: boolean, can_see_full_content: boolean, blocked_reason?: string}>
// GET /api/v1/athlete/wellness-content-gate/{session_id}
```

Todos os tipos devem ser definidos no mesmo arquivo (interfaces `AthleteSessionPreview`, `CloseSessionInput`).
AC-004: arquivo existe e contém `getAthleteSessionPreview`.

## Zona 3 — Default visibility_mode (1 arquivo — busca necessária)

### Z3: Formulários de criação de exercício
Buscar arquivos que chamam `createExercise()` ou que têm state/form com campo `visibility_mode`:
```bash
grep -rn 'createExercise\|visibility_mode\|org_wide' 'Hb Track - Frontend/src/' --include='*.tsx' --include='*.ts'
```
- Em qualquer formulário que passe `visibility_mode: 'org_wide'` explicitamente: alterar para `'restricted'`.
- Em qualquer formulário que omita `visibility_mode`: não é necessário adicionar (Backend já usa server_default='restricted').
- ExerciseVisibilityToggle.tsx: NÃO alterar a lógica de toggle (org_wide ↔ restricted); esse é um toggle pós-criação, não o default de criação.
- AC-005: NENHUM formulário de criação passa `visibility_mode: 'org_wide'` explicitamente.

## Zona 4 — Organization_id injection

### Z4: src/lib/api/exercises.ts — getExercises()
Verificar se `getExercises()` passa `organization_id` como query param. O Backend requer este campo para filtrar exercícios da organização correta (INV-TRAIN-049: scope=ORG requer organization_id).
- Se `organization_id` não está sendo passado: adicionar parâmetro opcional `organization_id?: string` na função e incluí-lo em `params` quando presente.
- Nota: `organization_id` deve ser obtido do contexto de auth (não hardcoded).

## Zona 5 — IA Coach Modal SCREEN-TRAIN-025

### Z5: src/components/training/AICoachDraftModal.tsx
INV-TRAIN-081: justificativa gerada pela IA DEVE ser visível antes do botão 'Aplicar'.
- O modal já existe (`AICoachDraftModal.tsx`) mas pode não exibir `justification`.
- Verificar a interface `AIDraft` e o estado `data`: se não possui `justification: string`, adicionar.
- No render do estado `data`: garantir que o campo `justification` seja exibido (elemento de texto ou bloco citação) ANTES do botão 'Aplicar'.
- AC-006: arquivo contém string `justification` como campo de UI visível.

## PROCESSO DE EXECUÇÃO
1. Zona 1: editar 3 arquivos de tipos (athlete-canonical.ts, exercises.ts, trainings.ts)
2. Zona 2: criar training-phase3.ts com stubs completos
3. Zona 3: buscar e corrigir formulários com org_wide default
4. Zona 4: verificar getExercises() organization_id injection
5. Zona 5: editar AICoachDraftModal.tsx para exibir justification
6. Rodar validation_command
7. Rodar hb report 236

## Critérios de Aceite
AC-001: src/types/athlete-canonical.ts contém `id: string` no interface Athlete.
AC-002: src/lib/api/exercises.ts contém `scope?: ExerciseScope` em ExerciseInput.
AC-003: src/lib/api/trainings.ts contém `standalone` em TrainingSession.
AC-004: src/lib/api/training-phase3.ts existe e contém `getAthleteSessionPreview`.
AC-005: Nenhum formulário de criação de exercício passa `visibility_mode: 'org_wide'` explicitamente.
AC-006: src/components/training/AICoachDraftModal.tsx exibe `justification` no estado data.

## Write Scope
- Hb Track - Frontend/src/types/athlete-canonical.ts
- Hb Track - Frontend/src/lib/api/exercises.ts
- Hb Track - Frontend/src/lib/api/trainings.ts
- Hb Track - Frontend/src/lib/api/training-phase3.ts
- Hb Track - Frontend/src/components/training/AICoachDraftModal.tsx

## Validation Command (Contrato)
```
python temp/validate_ar236.py
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_236/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Frontend/src/types/athlete-canonical.ts
git checkout -- Hb Track - Frontend/src/lib/api/exercises.ts
git checkout -- Hb Track - Frontend/src/lib/api/trainings.ts
git checkout -- Hb Track - Frontend/src/components/training/AICoachDraftModal.tsx
git clean -fd Hb Track - Frontend/src/lib/api/training-phase3.ts
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- athlete-canonical.ts: renomear person_id→id pode quebrar componentes que usam athlete.person_id diretamente. Estratégia recomendada: adicionar id: string como novo campo (sem remover person_id) nesta AR; a remoção de person_id é uma AR futura após migração completa.
- training-phase3.ts: os stubs são TypeScript não-implementados (throw new Error('não implementado')). Não devem ser chamados em produção sem BE real. Uso: apenas tipagem e estrutura para compilação.
- pending.ts existente usa URLs /attendance/sessions/{id}/pending-items vs CONTRACT-099 que define /training/pending-items. Executor deve verificar e alinhar — se o Backend mudou, atualizar pending.ts; se o CONTRACT está desatualizado, reportar divergência.
- ExerciseVisibilityToggle.tsx usa org_wide como valor de toggle (não default de criação) — NÃO alterar esse arquivo nesta AR.
- getExercises() organization_id: a fonte do organization_id no Frontend pode ser via JWT context, auth store ou query param. Executor deve verificar o padrão existente no codebase (grep: useOrganization, useAuth, organization_id) antes de injetar.
- TypeScript compilation: após alterações de tipos, executar tsc --noEmit para garantir 0 erros de tipo. Se houver erros de tipo, corrigir antes de hb report.
- AC-005 (visibility_mode org_wide) requer inspeção manual (grep). validation_command indica AC-005 como 'requer inspeção manual' — Executor deve documentar resultado da busca no executor_main.log.

## Análise de Impacto

**Executado em**: 2026-03-04

### AC-001 — athlete-canonical.ts + id: string
- ESTADO ANTES: `id: string` **já presente** na linha 39 do interface `Athlete` (adicionado em AR anterior).
- IMPACTO: Nenhuma alteração necessária. AC-001 já satisfeito.

### AC-002 — exercises.ts: ExerciseInput + scope/visibility_mode/organization_id
- ESTADO ANTES: `ExerciseInput` contém apenas `name, description, tag_ids, category, media_url`. Sem `scope`, `visibility_mode`, `organization_id`.
- IMPACTO: Adicionar 3 campos opcionais em `ExerciseInput`. Sem quebra de compatibilidade (opcional).
- `ExerciseFilters` também recebe `organization_id?: string` (Zona 4).
- `getExercises()` recebe tratamento de `organization_id` como query param.
- `VisibilityMode`: openapi.json **não contém** enum `VisibilityMode`/`ExerciseVisibilityMode` → `'public'` não adicionado.

### AC-003 — trainings.ts: TrainingSession + standalone
- ESTADO ANTES: `TrainingSession` não tem campo `standalone`.
- IMPACTO: Adicionar `standalone: boolean` ao final do interface (INV-TRAIN-057). Sem quebra.

### AC-004 — training-phase3.ts (CRIAR NOVO)
- ESTADO ANTES: arquivo não existe.
- IMPACTO: Criação de novo stub file com 8 funções tipadas + interfaces. Zero impacto em produção (stubs com throw).
- CONTRACT-099/100: `pending.ts` usa `/attendance/sessions/{id}/pending-items` e `/attendance/pending-items/{id}/resolve`. O CONTRACT define `/training/pending-items`. Divergência documentada → re-exportando aliases de pending.ts no training-phase3.ts (sem modificar pending.ts, fora do write_scope).

### AC-005 — Formulários de criação de exercício
- ESTADO ANTES: `CreateExerciseModal.tsx` não passa `visibility_mode` na criação (submete apenas name/description/tag_ids/category/media_url). `ExerciseVisibilityToggle.tsx` usa `org_wide` como toggle pós-criação (não alterado).
- Grep resultado: nenhum formulário de criação passa `visibility_mode: 'org_wide'` explicitamente.
- IMPACTO: AC-005 **já satisfeito**. Nenhuma alteração em formulários.

### AC-006 — AICoachDraftModal.tsx + justification
- ESTADO ANTES: arquivo **já exibe** `justification` proeminentemente (bloco "Justificativa da IA" antes dos botões de ação). Campo `justification: string` presente em `TrainingSessionDraft` e `MicrocycleDraft`.
- IMPACTO: AC-006 **já satisfeito**. Nenhuma alteração necessária.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar236.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T15:51:11.444998+00:00
**Behavior Hash**: c06c2786e6756e4c67d16f900f1f183a2f56e796bf69fa3175fa1b1229fb3f2a
**Evidence File**: `docs/hbtrack/evidence/AR_236/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar236.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T15:52:27.355977+00:00
**Behavior Hash**: c06c2786e6756e4c67d16f900f1f183a2f56e796bf69fa3175fa1b1229fb3f2a
**Evidence File**: `docs/hbtrack/evidence/AR_236/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_236_a7ab568/result.json`
