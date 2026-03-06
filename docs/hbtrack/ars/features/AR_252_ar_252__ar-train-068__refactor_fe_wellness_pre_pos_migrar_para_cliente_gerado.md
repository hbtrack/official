# AR_252 — AR_252 | AR-TRAIN-068 | Refactor FE Wellness Pre/Pos: migrar para cliente gerado (src/api/generated)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Refactor funcional (Categoria B): migrar WellnessPreForm.tsx e WellnessPostForm.tsx de src/lib/api/wellness (camada manual com tipos próprios) para src/api/generated (WellnessPreApi, WellnessPostApi do cliente gerado). Sem mudança de comportamento, sem contrato BE alterado, sem regeneração de openapi.json.

Organizado em 4 zonas:
- Zona 1: Expandir api-instance.ts com export wellnessPostApi (WellnessPostApi)
- Zona 2: Migrar WellnessPreForm.tsx — remover imports HTTP de lib/api/wellness, usar wellnessApi do cliente gerado
- Zona 3: Migrar WellnessPostForm.tsx — remover todos imports de lib/api/wellness, usar wellnessPostApi + wellnessApi do cliente gerado
- Zona 4A: Compilação TypeScript gate (npx tsc --noEmit)
- Zona 4B: Sync documental (Backlog + TEST_MATRIX + Kanban)

## Critérios de Aceite
- AC-Z1: api-instance.ts exporta wellnessPostApi tipado como WellnessPostApi.
- AC-Z2: WellnessPreForm.tsx usa addWellnessPreToSessionApiV1... e listWellnessPreBySessionApiV1... do cliente gerado. Sem imports HTTP de lib/api/wellness.
- AC-Z3: WellnessPostForm.tsx usa addWellnessPostToSessionApiV1... e listWellnessPostBySessionApiV1... do cliente gerado. Sem imports de lib/api/wellness.
- AC-Z4A: npx tsc --noEmit exit 0 (ou zero novos erros nos 3 arquivos modificados).
- AC-Z4B: grep 'AR-TRAIN-068' em AR_BACKLOG_TRAINING.md e TEST_MATRIX_TRAINING.md retorna pelo menos 1 resultado cada.

## Write Scope
- Hb Track - Frontend/src/api/generated/api-instance.ts
- Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx
- Hb Track - Frontend/src/components/training/wellness/WellnessPostForm.tsx
- docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md
- docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md
- docs/hbtrack/Hb Track Kanban.md

## Validation Command (Contrato)
```
python -c "import sys, os, subprocess; base='Hb Track - Frontend/src/'; f1=open(base+'api/generated/api-instance.ts',encoding='utf-8').read(); f2=open(base+'components/training/wellness/WellnessPreForm.tsx',encoding='utf-8').read(); f3=open(base+'components/training/wellness/WellnessPostForm.tsx',encoding='utf-8').read(); b1=open('docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md',encoding='utf-8').read(); m1=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); checks=[('wellnessPostApi',f1,'AC-Z1 wellnessPostApi em api-instance.ts'),('addWellnessPreToSessionApiV1',f2,'AC-Z2 generated client em WellnessPreForm'),('addWellnessPostToSessionApiV1',f3,'AC-Z3 generated client em WellnessPostForm'),('AR-TRAIN-068',b1,'AC-Z4B AR-TRAIN-068 em BACKLOG'),('AR-TRAIN-068',m1,'AC-Z4B AR-TRAIN-068 em TEST_MATRIX')]; failed=[l for t,c,l in checks if t not in c]; print('FAIL:',failed) or sys.exit(1) if failed else print('AC-Z1/Z2/Z3/Z4B PASS')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_252/executor_main.log`

## Notas do Arquiteto
Classe: M (migração FE) + G (sync documental). Não toca em Backend, schema SQL, alembic, ou openapi.json. CONTRACT_SYNC_FE não acionado (cliente gerado já existe de AR_236). DEC-TRAIN-001: athleteId no prop de WellnessPreForm é apenas para WellnessHistoricalChart UI — nunca vai no payload API.

## Riscos
- api-instance.ts: não duplicar interceptors — já existem 2 idênticos. Adicionar apenas o export wellnessPostApi.
- WellnessPreCreate gerado tem campos `fatigue` e `stress` (não `fatigue_pre` e `stress_level`) — mapeamento necessário no handleSubmit.
- WellnessPreCreate e WellnessPostCreate têm athlete_id/organization_id/created_by_membership_id como REQUIRED — backend infere do JWT (DEC-TRAIN-001), usar cast `as WellnessPreCreate`.
- WELLNESS_PRE_PRESETS usa `fatigue_pre`/`stress_level` — manter estado local com esses nomes e mapear para API no handleSubmit.
- readiness_score não existe em WellnessPreCreate — manter como campo local no form state.
- muscle_soreness_after não existe em WellnessPostCreate — manter como campo local no form state.

## Análise de Impacto

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `Hb Track - Frontend/src/api/generated/api-instance.ts` | Zona 1: adiciona `WellnessPostApi` ao import e exporta `wellnessPostApi = new WellnessPostApi(...)` |
| `Hb Track - Frontend/src/components/training/wellness/WellnessPreForm.tsx` | Zona 2: remove imports HTTP de lib/api/wellness (submitWellnessPre, getMyWellnessPre, WellnessPreInput, WellnessPre); adiciona imports do cliente gerado; define tipo local WellnessPreFormState; usa wellnessApi.addWellnessPreToSessionApiV1...Post() e wellnessApi.listWellnessPreBySessionApiV1...Get(); mapeia fatigue_pre→fatigue e stress_level→stress no payload |
| `Hb Track - Frontend/src/components/training/wellness/WellnessPostForm.tsx` | Zona 3: remove todos imports de lib/api/wellness; adiciona wellnessApi e wellnessPostApi do cliente gerado; define tipo local WellnessPostFormState; usa wellnessPostApi.addWellnessPostToSession...Post() e wellnessPostApi.listWellnessPostBySession...Get(); usa wellnessApi.listWellnessPreBySession...Get() para checkWellnessPre |
| `docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md` | Zona 4B: adiciona AR-TRAIN-068 na tabela e seção de detalhe |
| `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` | Zona 4B: adiciona entrada §9 AR-TRAIN-068 |
| `docs/hbtrack/Hb Track Kanban.md` | Zona 4B: adiciona card Batch 30 com AR_252 em EXECUTING |

### Impacto funcional
Mínimo — apenas troca o adapter HTTP interno dos 2 componentes. O comportamento da UI (sliders, presets, validações) permanece idêntico. Os endpoints chamados são os mesmos. A única diferença semântica é que `fatigue_pre` passa a ser enviado para a API como `fatigue` (nome correto no schema backend) e `stress_level` como `stress`.

### Invariantes avaliadas
- INV-TRAIN-022 (wellness_post_cache_invalidation): não impactada — mudança é apenas FE adapter.
- INV-TRAIN-003 (wellness_post_deadline): não impactada — deadline enforcement continua no backend.
- INV-TRAIN-071 (content_gate): não impactada — endpoint não está nesta AR.
- DEC-TRAIN-001: CONFIRMADO — athlete_id/org_id/created_by_membership_id são REQUIRED no generated schema mas backend infere do JWT; usar cast `as WellnessPreCreate`.

### ACs a satisfazer
- AC-Z1: api-instance.ts exporta wellnessPostApi ✓ (pendente implementação)
- AC-Z2: WellnessPreForm.tsx sem imports HTTP de lib/api/wellness + método generated ✓ (pendente)
- AC-Z3: WellnessPostForm.tsx sem imports de lib/api/wellness + método generated ✓ (pendente)
- AC-Z4A: npx tsc --noEmit exit 0 ✓ (pendente)
- AC-Z4B: AR-TRAIN-068 em BACKLOG e TEST_MATRIX ✓ (pendente)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys, os, subprocess; base='Hb Track - Frontend/src/'; f1=open(base+'api/generated/api-instance.ts',encoding='utf-8').read(); f2=open(base+'components/training/wellness/WellnessPreForm.tsx',encoding='utf-8').read(); f3=open(base+'components/training/wellness/WellnessPostForm.tsx',encoding='utf-8').read(); b1=open('docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md',encoding='utf-8').read(); m1=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); checks=[('wellnessPostApi',f1,'AC-Z1 wellnessPostApi em api-instance.ts'),('addWellnessPreToSessionApiV1',f2,'AC-Z2 generated client em WellnessPreForm'),('addWellnessPostToSessionApiV1',f3,'AC-Z3 generated client em WellnessPostForm'),('AR-TRAIN-068',b1,'AC-Z4B AR-TRAIN-068 em BACKLOG'),('AR-TRAIN-068',m1,'AC-Z4B AR-TRAIN-068 em TEST_MATRIX')]; failed=[l for t,c,l in checks if t not in c]; print('FAIL:',failed) or sys.exit(1) if failed else print('AC-Z1/Z2/Z3/Z4B PASS')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T08:18:07.059938+00:00
**Behavior Hash**: fa438c466d1698f826550dc8ec9576af1604cfb51123fa981c9239d165fe881d
**Evidence File**: `docs/hbtrack/evidence/AR_252/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys, os, subprocess; base='Hb Track - Frontend/src/'; f1=open(base+'api/generated/api-instance.ts',encoding='utf-8').read(); f2=open(base+'components/training/wellness/WellnessPreForm.tsx',encoding='utf-8').read(); f3=open(base+'components/training/wellness/WellnessPostForm.tsx',encoding='utf-8').read(); b1=open('docs/hbtrack/modulos/treinos/AR_BACKLOG_TRAINING.md',encoding='utf-8').read(); m1=open('docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md',encoding='utf-8').read(); checks=[('wellnessPostApi',f1,'AC-Z1 wellnessPostApi em api-instance.ts'),('addWellnessPreToSessionApiV1',f2,'AC-Z2 generated client em WellnessPreForm'),('addWellnessPostToSessionApiV1',f3,'AC-Z3 generated client em WellnessPostForm'),('AR-TRAIN-068',b1,'AC-Z4B AR-TRAIN-068 em BACKLOG'),('AR-TRAIN-068',m1,'AC-Z4B AR-TRAIN-068 em TEST_MATRIX')]; failed=[l for t,c,l in checks if t not in c]; print('FAIL:',failed) or sys.exit(1) if failed else print('AC-Z1/Z2/Z3/Z4B PASS')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-06T08:21:33.697176+00:00
**Behavior Hash**: fa438c466d1698f826550dc8ec9576af1604cfb51123fa981c9239d165fe881d
**Evidence File**: `docs/hbtrack/evidence/AR_252/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_252_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-06T08:52:19.020434+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_252_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_252/executor_main.log`
