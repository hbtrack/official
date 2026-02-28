# AR_169 — Fix wellness.ts: paths canonicos + WellnessPreInput SSOT-aligned

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Corrigir src/lib/api/wellness.ts em TODOS os seguintes pontos:

=== 1. WellnessPreInput interface (ANCORAS: schema.sql wellness_pre) ===
Campos atuais INCORRETOS (renomear/remover/adicionar):
- REMOVER: `fatigue_level` (coluna DB e `fatigue_pre`, nao `fatigue_level`)
- REMOVER: `readiness` (coluna DB e `readiness_score`)
- REMOVER: `mood` (coluna inexistente no DB -- NAO EXISTE em wellness_pre)
- ADICIONAR: `sleep_hours: number` (NOT NULL no DB, range 0..24, 1 decimal)
- RENOMEAR: `fatigue_level` -> `fatigue_pre` (alinhar ao DB)
- RENOMEAR: `readiness` -> `readiness_score` (tornar opcional: `readiness_score?: number`)
- MANTER: `sleep_quality`, `stress_level`, `muscle_soreness`, `notes?: string`
- ADICIONAR (opcional): `menstrual_cycle_phase?: string`

Interface final esperada:
```typescript
export interface WellnessPreInput {
  sleep_hours: number;         // 0..24, 1 decimal
  sleep_quality: number;       // 1..5
  fatigue_pre: number;         // 0..10
  stress_level: number;        // 0..10
  muscle_soreness: number;     // 0..10
  readiness_score?: number;    // 0..10 (opcional)
  menstrual_cycle_phase?: string; // enum opcional
  notes?: string;
}
```

=== 2. submitWellnessPre (ANCORA: openapi.json path) ===
Atual: `apiClient.post('/wellness_pre', { training_session_id: sessionId, ...data })`
Corrigir para:
```typescript
apiClient.post(`/wellness-pre/training_sessions/${sessionId}/wellness_pre`, { ...data })
```
REMOVER `training_session_id` do body (esta no path agora).

=== 3. getMyWellnessPre (ANCORA: openapi.json, DEC-TRAIN-001) ===
Atual: GET `/wellness_pre` com params `{ training_session_id, athlete_id: 'me' }`
Corrigir para: GET `/wellness-pre/training_sessions/${sessionId}/wellness_pre`
Sem query params para athlete (backend infere pelo JWT).
Retornar response[0] || null (pode retornar array).

=== 4. submitWellnessPost (ANCORA: openapi.json path) ===
Atual: `apiClient.post('/wellness_post', { training_session_id: sessionId, ...data })`
Corrigir para:
```typescript
apiClient.post(`/wellness-post/training_sessions/${sessionId}/wellness_post`, { ...data })
```
REMOVER `training_session_id` do body.

=== 5. getMyWellnessPost (ANCORA: openapi.json) ===
Atual: GET `/wellness_post` com params `{ training_session_id, athlete_id: 'me' }`
Corrigir para: GET `/wellness-post/training_sessions/${sessionId}/wellness_post`
Sem query params athlete. Retornar response[0] || null.

=== 6. WELLNESS_PRE_PRESETS (dependem de WellnessPreInput) ===
Atualizar todos os 4 presets para usar os novos campo names:
- `fatigue_level` -> `fatigue_pre`
- `readiness` -> `readiness_score`
- REMOVER campo `mood` de cada preset.values
- ADICIONAR `sleep_hours` razoável (ex: 8.0, 7.0, 6.0, 5.0) em cada preset

=== 7. GARANTIR: athlete_id NAO em WellnessPreInput ===
DEC-TRAIN-001: interface nao deve ter campo athlete_id. Backend infer do JWT.

ARQUIVOS A MODIFICAR:
- Hb Track - Frontend/src/lib/api/wellness.ts (UNICO arquivo desta task)

## Critérios de Aceite
1) WellnessPreInput contem sleep_hours (required) e NAO contem fatigue_level nem mood.
2) WellnessPreInput usa fatigue_pre (nao fatigue_level) e readiness_score (nao readiness).
3) submitWellnessPre faz POST para /wellness-pre/training_sessions/${sessionId}/wellness_pre.
4) submitWellnessPost faz POST para /wellness-post/training_sessions/${sessionId}/wellness_post.
5) getMyWellnessPre e getMyWellnessPost nao enviam athlete_id query param.
6) WELLNESS_PRE_PRESETS usa fatigue_pre, readiness_score, sleep_hours (sem mood, sem fatigue_level).
7) TypeScript compila sem erros em wellness.ts.

## Write Scope
- Hb Track - Frontend/src/lib/api/wellness.ts

## Validation Command (Contrato)
```
cd "Hb Track - Frontend" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'wellness.ts' in l and 'error TS' in l]; print('FAIL: tsc errors:\n'+chr(10).join(errs)) if errs else print('PASS: wellness.ts no tsc errors')" && python -c "import sys; c=open('src/lib/api/wellness.ts', encoding='utf-8').read(); checks=[('sleep_hours' in c, 'sleep_hours present in WellnessPreInput'), ('fatigue_pre' in c, 'fatigue_pre present'), ('fatigue_level' not in c, 'fatigue_level removed'), ('mood: number' not in c, 'mood removed'), ('readiness_score' in c, 'readiness_score present'), ('readiness: number' not in c, 'readiness renamed'), ('/wellness-pre/training_sessions/' in c, 'wellness-pre path corrected'), ('/wellness-post/training_sessions/' in c, 'wellness-post path corrected'), ('athlete_id' not in c.split('WellnessPreInput')[1].split('}')[0] if 'WellnessPreInput' in c else True, 'no athlete_id in WellnessPreInput')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: all checks OK - '+str(len(checks))+' checks') if not failed else sys.exit('FAIL: '+str(failed))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_169/executor_main.log`

## Notas do Arquiteto
ANCORAS: openapi.json paths /wellness-pre/training_sessions/{training_session_id}/wellness_pre e /wellness-post/training_sessions/{training_session_id}/wellness_post. schema.sql wellness_pre: sleep_hours numeric(4,1) NOT NULL, fatigue_pre (0-10), sleep_quality (1-5), readiness_score nullable. DEC-TRAIN-001 RESOLVIDA: sem athlete_id no payload atleta.

## Riscos
- WellnessPreForm.tsx e WellnessPostForm.tsx dependem de WellnessPreInput/WellnessPostInput -- Task 163 cobre WellnessPreForm; WellnessPostForm usa WellnessPostInput que nao muda nomes de campos
- WELLNESS_PRE_PRESETS tipos devem ser Partial<WellnessPreInput> -- verificar que sleep_hours esta presente nos presets apos renaming
- getMyWellnessPre retorna WellnessPre[] do endpoint -- response[0] pode ser undefined se atleta ainda nao preencheu; manter null return
- Outros arquivos que importam WellnessPreInput podem quebrar com renaming (fatigue_level -> fatigue_pre): Executor deve grep por usos e corrigir em cascata nesta mesma task

## Análise de Impacto
Arquivo único: `Hb Track - Frontend/src/lib/api/wellness.ts`.
DB changes: nenhum — apenas tipos TS e paths de chamada de API.
Cascata: WellnessPreForm.tsx usa WellnessPreInput (coberto por AR_170). WellnessHistoricalChart recebe metric como string prop — não afetado. AthleteWellnessSummary: campos renomeados (avg_fatigue_pre/avg_readiness_score). WELLNESS_PRE_PRESETS atualizado com novos nomes. Risco nulo — FE-only, sem alteração de lógica de negócio.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 07760d4
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `cd "Hb Track - Frontend" && npx tsc --noEmit --skipLibCheck 2>&1 | python -c "import sys; lines=sys.stdin.read(); errs=[l for l in lines.splitlines() if 'wellness.ts' in l and 'error TS' in l]; print('FAIL: tsc errors:\n'+chr(10).join(errs)) if errs else print('PASS: wellness.ts no tsc errors')" && python -c "import sys; c=open('src/lib/api/wellness.ts', encoding='utf-8').read(); checks=[('sleep_hours' in c, 'sleep_hours present in WellnessPreInput'), ('fatigue_pre' in c, 'fatigue_pre present'), ('fatigue_level' not in c, 'fatigue_level removed'), ('mood: number' not in c, 'mood removed'), ('readiness_score' in c, 'readiness_score present'), ('readiness: number' not in c, 'readiness renamed'), ('/wellness-pre/training_sessions/' in c, 'wellness-pre path corrected'), ('/wellness-post/training_sessions/' in c, 'wellness-post path corrected'), ('athlete_id' not in c.split('WellnessPreInput')[1].split('}')[0] if 'WellnessPreInput' in c else True, 'no athlete_id in WellnessPreInput')]; failed=[msg for ok,msg in checks if not ok]; print('PASS: all checks OK - '+str(len(checks))+' checks') if not failed else sys.exit('FAIL: '+str(failed))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-28T10:41:44.903714+00:00
**Behavior Hash**: 3b7525c5cb81a853948f49f26064c0e5f6cb9940dde7bf70e0a3545ef0257d00
**Evidence File**: `docs/hbtrack/evidence/AR_169/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 07760d4
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_169_07760d4/result.json`

### Selo Humano em 07760d4
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-28T17:32:44.861520+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_169_07760d4/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_169/executor_main.log`
