# AR_276 — Sunset final: remover stubs /publish + /close do router, openapi e FE

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.3.0

## Descrição
ARQUIVO 1: Hb Track - Backend/app/api/v1/routers/training_sessions.py
(a) Buscar com grep: @router.post(...publish...) e @router.post(...close...) — se existirem como stubs deprecated, REMOVER completamente.
(b) Remover qualquer import nao mais utilizado associado (TrainingSessionCloseRequest se ainda importada mas nao usada).
(c) Confirmar: apenas /schedule e /finalize existem como endpoints de transicao humana.

PIPELINE FINAL spec-driven (OBRIGATORIO):
1. Iniciar uvicorn: cd 'Hb Track - Backend' && uvicorn app.main:app --reload.
2. Regen openapi.json: GET http://127.0.0.1:8000/api/v1/openapi.json > 'Hb Track - Backend/docs/ssot/openapi.json'.
3. OPENAPI_SPEC_QUALITY: npx @redocly/cli@latest lint 'Hb Track - Backend/docs/ssot/openapi.json'.
4. CONTRACT_DIFF_GATE: oasdiff breaking 'contracts/openapi/baseline/openapi_baseline.json' 'Hb Track - Backend/docs/ssot/openapi.json' -- documentar no evidence.
5. GENERATED_CLIENT_SYNC: cd 'Hb Track - Frontend' && npm run api:sync.
6. AUDITORIA FINAL: rg -rn '/publish|/close' 'Hb Track - Backend/app' -- PASS = exit 1 (zero ocorrencias de rota legada).

ARQUIVO 2: Hb Track - Backend/docs/ssot/openapi.json (DERIVADO — regen)
Apos remocao dos stubs e regen: verificar:
  - paths sem /api/v1/training-sessions/{id}/publish
  - paths sem /api/v1/training-sessions/{id}/close
  - paths com /api/v1/training-sessions/{id}/schedule e /finalize
  - componentes.schemas sem TrainingSessionCloseRequest (se removido)

ARQUIVO 3: Hb Track - Frontend/src/api/generated/api.ts (DERIVADO — api:sync)
Apos api:sync: verificar:
  - sem publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost
  - sem closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost
  - com scheduleTrainingSession... e finalizeTrainingSession...

NOTA: contracts/openapi/baseline/openapi_baseline.json NAO e alvo de write_scope (fora de governed roots). Se necessario, atualizar o baseline e uma acao de governanca separada fora deste AR.

PROIBIDO:
  - Criar adapter semantico publish->schedule
  - Manter /publish ou /close como rota ativa ou stub
  - Deixar o FE core consumindo /publish ou /close

## Critérios de Aceite
1) Router training_sessions.py: zero @router.post com 'publish' ou 'close' em paths.
2) openapi.json: zero paths /publish e /close em training-sessions.
3) openapi.json: paths /schedule e /finalize presentes com operationIds.
4) FE api.ts: sem publishTrainingSession* e closeTrainingSession* hooks.
5) FE api.ts: scheduleTrainingSession* e finalizeTrainingSession* presentes.
6) OPENAPI_SPEC_QUALITY: redocly lint sem erros criticos.
7) validation_command exit=0.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/training_sessions.py
- Hb Track - Backend/docs/ssot/openapi.json
- Hb Track - Frontend/src/api/generated/api.ts

## Validation Command (Contrato)
```
python -c "import pathlib,re,json;bk='Hb Track - Backend';o=json.loads(pathlib.Path(bk+'/docs/ssot/openapi.json').read_text('utf-8'));p=o.get('paths',{});pp=[k for k in p if 'training-session' in k];assert not any('/publish' in k for k in pp),'G1:publish path in final openapi';assert not any(k.endswith('/close') and 'training' in k for k in pp),'G2:close path in final openapi';sp=[k for k in pp if '/schedule' in k];assert sp,'G3a:schedule absent';fp=[k for k in pp if '/finalize' in k];assert fp,'G3b:finalize absent';fe=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in fe,'G4:publish hook FE';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in fe,'G5:close hook FE';assert any(x in fe for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G6:schedule hook absent';router=pathlib.Path(bk+'/app/api/v1/routers/training_sessions.py').read_text('utf-8');rp=[m.group() for m in re.finditer(r'@router[.]post[(][^)]+[)]',router)];assert not any('publish' in x for x in rp),'G7:publish stub in router';print('PASS AR_276 sunset final OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_276/executor_main.log`

## Notas do Arquiteto
Classe A (sem mudanca documental de governanca — governo ja feito em AR_272+REC-02). Pipeline spec-driven COMPLETO obrigatorio. oasdiff reportara breaking changes (remocao definitiva de /publish e /close) — documentar no evidence, NAO bloquear (contrato nao e producao). PROOF: TRUTH_BE — openapi.json e router sem /publish /close; FE api.ts sem hooks legados; validation_command exit=0. TRACE: router training_sessions.py clean de stubs, openapi.json paths canonicos /schedule+/finalize, FE api.ts hooks reconciliados.

## Riscos
- Se AR_273 foi executado com remocao direta (sem stubs deprecated), router ja pode estar limpo — Executor verificar com grep antes de qualquer edicao
- Se stubs deprecated foram mantidos para janela de migracao, remover apenas quando FE core nao consuma mais (garantido por AR_275)
- oasdiff reportara breaking changes — isso e esperado e documentado; NAO usar --breaking-changes-only sem documentar
- openapi.json e api.ts sao DERIVADOS — NAO editar manualmente; usar regen (uvicorn + GET) e api:sync

## Análise de Impacto

**Diagnóstico pré-execução (grep + validação):**
- `training_sessions.py`: zero `@router.post` com `/publish` ou `/close` — removidos pela AR_273.
- `openapi.json`: zero paths `/publish` e `/close` em training-sessions — já derivado correto da AR_273.
- `api.ts`: sem hooks `publishTrainingSession*` ou `closeTrainingSession*` — gerado corretamente pela AR_273 via `npm run api:sync`.

**Resultado:** Todos os 7 gates do validation_command passam sem necessidade de edição de código. O sunset já foi efetivado pela execução da AR_273 (reconciliação contratual). Esta AR valida e certifica o estado final via pipeline spec-driven + validation_command.

**Arquivos verificados (não modificados — já no estado correto):**
1. `Hb Track - Backend/app/api/v1/routers/training_sessions.py` — sem stubs `/publish`/`/close`; apenas `/schedule` e `/finalize` como transições humanas.
2. `Hb Track - Backend/docs/ssot/openapi.json` — paths `/schedule` e `/finalize` presentes; `/publish` e `/close` ausentes.
3. `Hb Track - Frontend/src/api/generated/api.ts` — hooks `scheduleTrainingSession` e `finalizeTrainingSession` presentes; hooks legados ausentes.

**Riscos mitigados:**
- oasdiff poderá reportar breaking changes históricas (remoção de `/publish`/`/close` já feita na AR_273) — documentado e esperado per notas do Arquiteto.
- `contracts/openapi/baseline/openapi_baseline.json` fora do write_scope — não alterado.

**Pipeline spec-driven:**
- Obrigatório por regra Executor (contrato FE↔BE tocado via openapi.json regen).
- openapi.json já está no estado correto — regen confirmatória via uvicorn + GET necessária para evidência.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b07ecee
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib,re,json;bk='Hb Track - Backend';o=json.loads(pathlib.Path(bk+'/docs/ssot/openapi.json').read_text('utf-8'));p=o.get('paths',{});pp=[k for k in p if 'training-session' in k];assert not any('/publish' in k for k in pp),'G1:publish path in final openapi';assert not any(k.endswith('/close') and 'training' in k for k in pp),'G2:close path in final openapi';sp=[k for k in pp if '/schedule' in k];assert sp,'G3a:schedule absent';fp=[k for k in pp if '/finalize' in k];assert fp,'G3b:finalize absent';fe=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in fe,'G4:publish hook FE';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in fe,'G5:close hook FE';assert any(x in fe for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G6:schedule hook absent';router=pathlib.Path(bk+'/app/api/v1/routers/training_sessions.py').read_text('utf-8');rp=[m.group() for m in re.finditer(r'@router[.]post[(][^)]+[)]',router)];assert not any('publish' in x for x in rp),'G7:publish stub in router';print('PASS AR_276 sunset final OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-10T04:38:12.898003+00:00
**Behavior Hash**: 9818fa908c1b08ae46a894152d93e024d8e1dc3a18b2d25ede07747cf5208f2d
**Evidence File**: `docs/hbtrack/evidence/AR_276/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b07ecee
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib,re,json;bk='Hb Track - Backend';o=json.loads(pathlib.Path(bk+'/docs/ssot/openapi.json').read_text('utf-8'));p=o.get('paths',{});pp=[k for k in p if 'training-session' in k];assert not any('/publish' in k for k in pp),'G1:publish path in final openapi';assert not any(k.endswith('/close') and 'training' in k for k in pp),'G2:close path in final openapi';sp=[k for k in pp if '/schedule' in k];assert sp,'G3a:schedule absent';fp=[k for k in pp if '/finalize' in k];assert fp,'G3b:finalize absent';fe=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in fe,'G4:publish hook FE';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in fe,'G5:close hook FE';assert any(x in fe for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G6:schedule hook absent';router=pathlib.Path(bk+'/app/api/v1/routers/training_sessions.py').read_text('utf-8');rp=[m.group() for m in re.finditer(r'@router[.]post[(][^)]+[)]',router)];assert not any('publish' in x for x in rp),'G7:publish stub in router';print('PASS AR_276 sunset final OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-10T04:38:51.573482+00:00
**Behavior Hash**: 9818fa908c1b08ae46a894152d93e024d8e1dc3a18b2d25ede07747cf5208f2d
**Evidence File**: `docs/hbtrack/evidence/AR_276/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b07ecee
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib,re,json;bk='Hb Track - Backend';o=json.loads(pathlib.Path(bk+'/docs/ssot/openapi.json').read_text('utf-8'));p=o.get('paths',{});pp=[k for k in p if 'training-session' in k];assert not any('/publish' in k for k in pp),'G1:publish path in final openapi';assert not any(k.endswith('/close') and 'training' in k for k in pp),'G2:close path in final openapi';sp=[k for k in pp if '/schedule' in k];assert sp,'G3a:schedule absent';fp=[k for k in pp if '/finalize' in k];assert fp,'G3b:finalize absent';fe=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in fe,'G4:publish hook FE';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in fe,'G5:close hook FE';assert any(x in fe for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G6:schedule hook absent';router=pathlib.Path(bk+'/app/api/v1/routers/training_sessions.py').read_text('utf-8');rp=[m.group() for m in re.finditer(r'@router[.]post[(][^)]+[)]',router)];assert not any('publish' in x for x in rp),'G7:publish stub in router';print('PASS AR_276 sunset final OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-10T04:39:07.584206+00:00
**Behavior Hash**: 9818fa908c1b08ae46a894152d93e024d8e1dc3a18b2d25ede07747cf5208f2d
**Evidence File**: `docs/hbtrack/evidence/AR_276/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em b07ecee
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib,re,json;bk='Hb Track - Backend';o=json.loads(pathlib.Path(bk+'/docs/ssot/openapi.json').read_text('utf-8'));p=o.get('paths',{});pp=[k for k in p if 'training-session' in k];assert not any('/publish' in k for k in pp),'G1:publish path in final openapi';assert not any(k.endswith('/close') and 'training' in k for k in pp),'G2:close path in final openapi';sp=[k for k in pp if '/schedule' in k];assert sp,'G3a:schedule absent';fp=[k for k in pp if '/finalize' in k];assert fp,'G3b:finalize absent';fe=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in fe,'G4:publish hook FE';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in fe,'G5:close hook FE';assert any(x in fe for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G6:schedule hook absent';router=pathlib.Path(bk+'/app/api/v1/routers/training_sessions.py').read_text('utf-8');rp=[m.group() for m in re.finditer(r'@router[.]post[(][^)]+[)]',router)];assert not any('publish' in x for x in rp),'G7:publish stub in router';print('PASS AR_276 sunset final OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-10T04:40:21.849978+00:00
**Behavior Hash**: 9818fa908c1b08ae46a894152d93e024d8e1dc3a18b2d25ede07747cf5208f2d
**Evidence File**: `docs/hbtrack/evidence/AR_276/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b07ecee
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_276_b07ecee/result.json`
