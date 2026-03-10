# AR_273 — Reconciliacao contratual REC-02: /schedule+/finalize no router, schemas, service, openapi e FE

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
ARQUIVO 1: docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md
(a) Localizar linha CONTRACT-TRAIN-006 (POST /publish). Alterar status de EVIDENCIADO para DEPRECADO ou REMOVIDO. Anotar substituido por /schedule.
(b) Localizar linha CONTRACT-TRAIN-007 (POST /close). Alterar status de EVIDENCIADO para DEPRECADO ou REMOVIDO. Anotar substituido por /finalize.
(c) Localizar CONTRACT-TRAIN-098 (/close) e marcar como DEPRECADO/REMOVIDO.
(d) Adicionar nova linha: CONTRACT-TRAIN-101 | POST | /training-sessions/{id}/schedule | scheduleTrainingSession | TrainingSessionScheduleRequest | TrainingSession | EVIDENCIADO | INV-TRAIN-006.
(e) Adicionar nova linha: CONTRACT-TRAIN-102 | POST | /training-sessions/{id}/finalize | finalizeTrainingSession | TrainingSessionFinalizeRequest | SessionClosureResponse | EVIDENCIADO | INV-TRAIN-006.

ARQUIVO 2: Hb Track - Backend/app/schemas/training_sessions.py
(a) Adicionar class TrainingSessionScheduleRequest(BaseModel) com campos obrigatorios: starts_at: datetime, ends_at: datetime.
(b) Renomear class TrainingSessionCloseRequest -> TrainingSessionFinalizeRequest. Adicionar campos obrigatorios: attendance_completed: bool, review_completed: bool. Manter confirm: bool = Field(default=True).
(c) Atualizar qualquer import/referencia ao nome antigo.

ARQUIVO 3: Hb Track - Backend/app/services/training_session_service.py
(a) Renomear publish_session -> schedule_session. Adicionar parametros starts_at: datetime, ends_at: datetime.
(b) Renomear close_session -> finalize_session. Adicionar parametros attendance_completed: bool, review_completed: bool.
(c) Corrigir todas as referencias internas e em outros arquivos que chamem publish_session ou close_session.

ARQUIVO 4: Hb Track - Backend/app/api/v1/routers/training_sessions.py
(a) Renomear @router.post('/{id}/publish') -> @router.post('/{id}/schedule'). Handler publish_training_session -> schedule_training_session. Adicionar body request_data: TrainingSessionScheduleRequest. Atualizar chamada para service.schedule_session(id, request_data.starts_at, request_data.ends_at).
(b) Renomear @router.post('/{id}/close') -> @router.post('/{id}/finalize'). Handler close_training_session -> finalize_training_session. Trocar TrainingSessionCloseRequest -> TrainingSessionFinalizeRequest. Atualizar chamada para service.finalize_session(id, request_data.attendance_completed, request_data.review_completed).

PIPELINE spec-driven (OBRIGATORIO — executar nesta ordem):
1. Regenerar openapi.json: iniciar uvicorn, GET http://127.0.0.1:8000/api/v1/openapi.json, salvar em 'Hb Track - Backend/docs/ssot/openapi.json'.
2. OPENAPI_SPEC_QUALITY: npx @redocly/cli@latest lint 'Hb Track - Backend/docs/ssot/openapi.json'.
3. CONTRACT_DIFF_GATE: oasdiff breaking 'contracts/openapi/baseline/openapi_baseline.json' 'Hb Track - Backend/docs/ssot/openapi.json'. Documentar breaking changes no evidence.
4. GENERATED_CLIENT_SYNC: cd 'Hb Track - Frontend' && npm run api:sync.
5. RUNTIME CONTRACT VALIDATION (Gate 11): python -m schemathesis run http://127.0.0.1:8000/api/v1/openapi.json --include-path '*/training-sessions/*/schedule' --include-path '*/training-sessions/*/finalize' --checks not_a_server_error.

ARQUIVO 6 (NOVO): Hb Track - Backend/tests/training/state_machine/test_schedule_transition_guards.py
Criar diretorio tests/training/state_machine/ com __init__.py.
Escrever 5 testes pytest:
  test_schedule_requires_draft_status
  test_schedule_sets_status_to_scheduled
  test_finalize_requires_pending_review_status
  test_finalize_sets_status_to_readonly
  test_schedule_validates_starts_at_required
(Gate 12): pytest 'Hb Track - Backend/tests/training/state_machine/test_schedule_transition_guards.py' -v — 5 testes PASS.
PROIBIDO: editar src/api/generated/* manualmente. PROIBIDO: alterar _INDEX.md do modulo.

## Critérios de Aceite
1) TRAINING_FRONT_BACK_CONTRACT.md: CONTRACT-006 e CONTRACT-007 sem EVIDENCIADO; /schedule e /finalize presentes com EVIDENCIADO.
2) openapi.json: sem paths /publish e /close em training-sessions; paths /schedule e /finalize com operationIds.
3) openapi.json schemas: TrainingSessionScheduleRequest com starts_at+ends_at; TrainingSessionFinalizeRequest com attendance_completed+review_completed.
4) FE api.ts: sem hooks publishTrainingSessionApiV1... e closeTrainingSessionApiV1...; hooks scheduleTrainingSession... e finalizeTrainingSession... presentes.
5) validation_command (Gates 1-10) exit=0.
6) OPENAPI_SPEC_QUALITY: redocly lint sem erros criticos.
7) CONTRACT_DIFF_GATE: oasdiff registrado no evidence.
8) GENERATED_CLIENT_SYNC: api:sync OK.
9) (Gate 11) schemathesis smoke PASS em /schedule e /finalize.
10) (Gate 12) pytest test_schedule_transition_guards.py — 5 testes PASS.

## Write Scope
- docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md
- Hb Track - Backend/app/api/v1/routers/training_sessions.py
- Hb Track - Backend/app/schemas/training_sessions.py
- Hb Track - Backend/app/services/training_session_service.py
- Hb Track - Backend/docs/ssot/openapi.json
- Hb Track - Frontend/src/api/generated/api.ts
- Hb Track - Backend/tests/training/state_machine/__init__.py
- Hb Track - Backend/tests/training/state_machine/test_schedule_transition_guards.py

## Validation Command (Contrato)
```
python -c "import json,pathlib,re;c=pathlib.Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text('utf-8');o=json.loads(pathlib.Path('Hb Track - Backend/docs/ssot/openapi.json').read_text('utf-8'));f=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');p=o.get('paths',{});s=o.get('components',{}).get('schemas',{});assert not re.search(r'\|\s*CONTRACT-TRAIN-006\s*\|[^\n]+EVIDENCIADO',c),'G1a';assert not re.search(r'\|\s*CONTRACT-TRAIN-007\s*\|[^\n]+EVIDENCIADO',c),'G1b';assert '/schedule' in c,'G2a';assert '/finalize' in c,'G2b';pp=[x for x in p if 'publish' in x and 'training' in x];assert not pp,'G3a';cp=[x for x in p if x.endswith('/close') and 'training' in x];assert not cp,'G3b';sp=[x for x in p if 'schedule' in x and 'training' in x];assert sp,'G4a';fp=[x for x in p if 'finalize' in x and 'training' in x];assert fp,'G4b';assert p[sp[0]].get('post',{}).get('operationId'),'G5a';assert p[fp[0]].get('post',{}).get('operationId'),'G5b';se=s.get('TrainingSession',{}).get('properties',{}).get('status',{}).get('enum',[]);assert 'published' not in se,'G6a';assert 'closed' not in se,'G6b';sr=s.get('TrainingSessionScheduleRequest',{});assert 'properties' in sr,'G7a';sp2=sr.get('properties',{});assert 'starts_at' in sp2,'G7b';assert 'ends_at' in sp2,'G7c';fr=s.get('TrainingSessionFinalizeRequest',{});assert 'properties' in fr,'G8a';fp2=fr.get('properties',{});assert 'attendance_completed' in fp2,'G8b';assert 'review_completed' in fp2,'G8c';assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in f,'G9a';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in f,'G9b';assert any(x in f for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G10a';assert any(x in f for x in ['finalizeTrainingSession','FinalizeTrainingSession']),'G10b';print('PASS AR_273: Gates 1-10 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_273/executor_main.log`

## Notas do Arquiteto
Classe A+G. Pipeline spec-driven COMPLETO obrigatorio. Gate 11 (schemathesis): python -m schemathesis run http://127.0.0.1:8000/api/v1/openapi.json --include-path '*/training-sessions/*/schedule' --include-path '*/training-sessions/*/finalize' --checks not_a_server_error. Gate 12 (pytest state machine): cd 'Hb Track - Backend' && pytest tests/training/state_machine/test_schedule_transition_guards.py -v. openapi.json e api.ts sao DERIVADOS — NAO editar manualmente. Executor iniciar backend (uvicorn) antes de regen openapi e api:sync. PROOF: TRUTH_BE — pytest tests/training/state_machine/test_schedule_transition_guards.py 5 PASS. TRACE: TRAINING_FRONT_BACK_CONTRACT.md CONTRACT-101/102, openapi /schedule+/finalize, FE scheduleTrainingSession+finalizeTrainingSession, test_schedule_transition_guards.py.

## Riscos
- publish_session pode ter callers internos alem do router — Executor DEVE buscar todas as referencias com grep antes de renomear
- close_session pode ter callers alem do router (testes existentes) — Executor DEVE verificar e atualizar referencias
- TrainingSessionCloseRequest pode ser importada em outros modulos — Executor DEVE verificar imports
- api:sync requer backend ativo em 127.0.0.1:8000 — se backend nao iniciar, Executor DEVE reportar BLOCKED
- oasdiff reportara breaking changes (renomear /publish->/schedule e /close->/finalize SAO breaking) — documentar no evidence, nao bloquear (contrato nao e producao)
- tests/training/state_machine/ precisa de __init__.py para pytest descobrir — criar junto com arquivo de teste
- scheduled_at/starts_at campo pode nao existir no modelo TrainingSession — Executor verificar schema antes de persistir

## Análise de Impacto
Preenchido pelo Executor em 2026-03-09.

**Arquivos no write_scope:**
1. `app/schemas/training_sessions.py` (L459): `TrainingSessionCloseRequest` → `TrainingSessionFinalizeRequest` + adicionar `attendance_completed: bool, review_completed: bool`; adicionar nova `TrainingSessionScheduleRequest` com `starts_at: datetime, ends_at: datetime`.
2. `app/services/training_session_service.py` (L488): renomear `publish_session` → `schedule_session`, adicionar params `starts_at: datetime, ends_at: datetime`, atualizar `session.session_at = starts_at`; (L834): renomear `close_session` → `finalize_session`, adicionar params `attendance_completed: bool, review_completed: bool`.
3. `app/api/v1/routers/training_sessions.py` (L33): adicionar imports `TrainingSessionScheduleRequest, TrainingSessionFinalizeRequest`; (L565-628): renomear rota + handler para `/schedule`/`schedule_training_session` com body `request_data: TrainingSessionScheduleRequest`; (L629-695): renomear rota + handler para `/finalize`/`finalize_training_session` com body `request_data: TrainingSessionFinalizeRequest`.
4. `TRAINING_FRONT_BACK_CONTRACT.md`: CONTRACT-TRAIN-006 e 007 EVIDENCIADO→DEPRECADO; CONTRACT-TRAIN-098 DEPRECADO; adicionar CONTRACT-TRAIN-101 + 102.
5. `tests/training/state_machine/` (NOVO): criar `__init__.py` + `test_schedule_transition_guards.py` com 5 testes.

**Callers fora do write_scope (necessitam atualização):**
- `tests/training/invariants/test_inv_train_019_training_session_audit_logs.py` (L79): `service.publish_session(session.id)` → `service.schedule_session(session.id, starts_at=..., ends_at=...)`.
- `tests/training/invariants/test_inv_train_019_training_session_audit_logs.py` (L189): `service.close_session(session.id)` → `service.finalize_session(session.id, attendance_completed=True, review_completed=True)`.
- `tests/integration/test_training_closure_validation.py` (L199,L221,L239,L261,L280): 5 calls `service.close_session(session.id)` → `service.finalize_session(session.id, attendance_completed=True, review_completed=True)`.

**Sem impacto:**
- `tests/training/invariants/test_inv_train_065_close_pending_guard.py`: usa SQL direto, sem chamada ao service.
- `app/services/attendance_service.py` L642: método distinto `close_session_attendance`, sem relação.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 284e769
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,pathlib,re;c=pathlib.Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text('utf-8');o=json.loads(pathlib.Path('Hb Track - Backend/docs/ssot/openapi.json').read_text('utf-8'));f=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');p=o.get('paths',{});s=o.get('components',{}).get('schemas',{});assert not re.search(r'\|\s*CONTRACT-TRAIN-006\s*\|[^\n]+EVIDENCIADO',c),'G1a';assert not re.search(r'\|\s*CONTRACT-TRAIN-007\s*\|[^\n]+EVIDENCIADO',c),'G1b';assert '/schedule' in c,'G2a';assert '/finalize' in c,'G2b';pp=[x for x in p if 'publish' in x and 'training' in x];assert not pp,'G3a';cp=[x for x in p if x.endswith('/close') and 'training' in x];assert not cp,'G3b';sp=[x for x in p if 'schedule' in x and 'training' in x];assert sp,'G4a';fp=[x for x in p if 'finalize' in x and 'training' in x];assert fp,'G4b';assert p[sp[0]].get('post',{}).get('operationId'),'G5a';assert p[fp[0]].get('post',{}).get('operationId'),'G5b';se=s.get('TrainingSession',{}).get('properties',{}).get('status',{}).get('enum',[]);assert 'published' not in se,'G6a';assert 'closed' not in se,'G6b';sr=s.get('TrainingSessionScheduleRequest',{});assert 'properties' in sr,'G7a';sp2=sr.get('properties',{});assert 'starts_at' in sp2,'G7b';assert 'ends_at' in sp2,'G7c';fr=s.get('TrainingSessionFinalizeRequest',{});assert 'properties' in fr,'G8a';fp2=fr.get('properties',{});assert 'attendance_completed' in fp2,'G8b';assert 'review_completed' in fp2,'G8c';assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in f,'G9a';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in f,'G9b';assert any(x in f for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G10a';assert any(x in f for x in ['finalizeTrainingSession','FinalizeTrainingSession']),'G10b';print('PASS AR_273: Gates 1-10 OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-09T08:33:47.584294+00:00
**Behavior Hash**: 81ca8d9271b6b2f55f7bfea80df94d0562df78dbdf6ac575f305f5522107f1ec
**Evidence File**: `docs/hbtrack/evidence/AR_273/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 284e769
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,pathlib,re;c=pathlib.Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text('utf-8');o=json.loads(pathlib.Path('Hb Track - Backend/docs/ssot/openapi.json').read_text('utf-8'));f=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');p=o.get('paths',{});s=o.get('components',{}).get('schemas',{});assert not re.search(r'\|\s*CONTRACT-TRAIN-006\s*\|[^\n]+EVIDENCIADO',c),'G1a';assert not re.search(r'\|\s*CONTRACT-TRAIN-007\s*\|[^\n]+EVIDENCIADO',c),'G1b';assert '/schedule' in c,'G2a';assert '/finalize' in c,'G2b';pp=[x for x in p if 'publish' in x and 'training' in x];assert not pp,'G3a';cp=[x for x in p if x.endswith('/close') and 'training' in x];assert not cp,'G3b';sp=[x for x in p if 'schedule' in x and 'training' in x];assert sp,'G4a';fp=[x for x in p if 'finalize' in x and 'training' in x];assert fp,'G4b';assert p[sp[0]].get('post',{}).get('operationId'),'G5a';assert p[fp[0]].get('post',{}).get('operationId'),'G5b';se=s.get('TrainingSession',{}).get('properties',{}).get('status',{}).get('enum',[]);assert 'published' not in se,'G6a';assert 'closed' not in se,'G6b';sr=s.get('TrainingSessionScheduleRequest',{});assert 'properties' in sr,'G7a';sp2=sr.get('properties',{});assert 'starts_at' in sp2,'G7b';assert 'ends_at' in sp2,'G7c';fr=s.get('TrainingSessionFinalizeRequest',{});assert 'properties' in fr,'G8a';fp2=fr.get('properties',{});assert 'attendance_completed' in fp2,'G8b';assert 'review_completed' in fp2,'G8c';assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in f,'G9a';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in f,'G9b';assert any(x in f for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G10a';assert any(x in f for x in ['finalizeTrainingSession','FinalizeTrainingSession']),'G10b';print('PASS AR_273: Gates 1-10 OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-09T08:36:29.878766+00:00
**Behavior Hash**: 81ca8d9271b6b2f55f7bfea80df94d0562df78dbdf6ac575f305f5522107f1ec
**Evidence File**: `docs/hbtrack/evidence/AR_273/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 284e769
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,pathlib,re;c=pathlib.Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text('utf-8');o=json.loads(pathlib.Path('Hb Track - Backend/docs/ssot/openapi.json').read_text('utf-8'));f=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');p=o.get('paths',{});s=o.get('components',{}).get('schemas',{});assert not re.search(r'\|\s*CONTRACT-TRAIN-006\s*\|[^\n]+EVIDENCIADO',c),'G1a';assert not re.search(r'\|\s*CONTRACT-TRAIN-007\s*\|[^\n]+EVIDENCIADO',c),'G1b';assert '/schedule' in c,'G2a';assert '/finalize' in c,'G2b';pp=[x for x in p if 'publish' in x and 'training' in x];assert not pp,'G3a';cp=[x for x in p if x.endswith('/close') and 'training' in x];assert not cp,'G3b';sp=[x for x in p if 'schedule' in x and 'training' in x];assert sp,'G4a';fp=[x for x in p if 'finalize' in x and 'training' in x];assert fp,'G4b';assert p[sp[0]].get('post',{}).get('operationId'),'G5a';assert p[fp[0]].get('post',{}).get('operationId'),'G5b';se=s.get('TrainingSession',{}).get('properties',{}).get('status',{}).get('enum',[]);assert 'published' not in se,'G6a';assert 'closed' not in se,'G6b';sr=s.get('TrainingSessionScheduleRequest',{});assert 'properties' in sr,'G7a';sp2=sr.get('properties',{});assert 'starts_at' in sp2,'G7b';assert 'ends_at' in sp2,'G7c';fr=s.get('TrainingSessionFinalizeRequest',{});assert 'properties' in fr,'G8a';fp2=fr.get('properties',{});assert 'attendance_completed' in fp2,'G8b';assert 'review_completed' in fp2,'G8c';assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in f,'G9a';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in f,'G9b';assert any(x in f for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G10a';assert any(x in f for x in ['finalizeTrainingSession','FinalizeTrainingSession']),'G10b';print('PASS AR_273: Gates 1-10 OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-09T08:46:42.930555+00:00
**Behavior Hash**: 81ca8d9271b6b2f55f7bfea80df94d0562df78dbdf6ac575f305f5522107f1ec
**Evidence File**: `docs/hbtrack/evidence/AR_273/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 284e769
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,pathlib,re;c=pathlib.Path('docs/hbtrack/modulos/treinos/TRAINING_FRONT_BACK_CONTRACT.md').read_text('utf-8');o=json.loads(pathlib.Path('Hb Track - Backend/docs/ssot/openapi.json').read_text('utf-8'));f=pathlib.Path('Hb Track - Frontend/src/api/generated/api.ts').read_text('utf-8');p=o.get('paths',{});s=o.get('components',{}).get('schemas',{});assert not re.search(r'\|\s*CONTRACT-TRAIN-006\s*\|[^\n]+EVIDENCIADO',c),'G1a';assert not re.search(r'\|\s*CONTRACT-TRAIN-007\s*\|[^\n]+EVIDENCIADO',c),'G1b';assert '/schedule' in c,'G2a';assert '/finalize' in c,'G2b';pp=[x for x in p if 'publish' in x and 'training' in x];assert not pp,'G3a';cp=[x for x in p if x.endswith('/close') and 'training' in x];assert not cp,'G3b';sp=[x for x in p if 'schedule' in x and 'training' in x];assert sp,'G4a';fp=[x for x in p if 'finalize' in x and 'training' in x];assert fp,'G4b';assert p[sp[0]].get('post',{}).get('operationId'),'G5a';assert p[fp[0]].get('post',{}).get('operationId'),'G5b';se=s.get('TrainingSession',{}).get('properties',{}).get('status',{}).get('enum',[]);assert 'published' not in se,'G6a';assert 'closed' not in se,'G6b';sr=s.get('TrainingSessionScheduleRequest',{});assert 'properties' in sr,'G7a';sp2=sr.get('properties',{});assert 'starts_at' in sp2,'G7b';assert 'ends_at' in sp2,'G7c';fr=s.get('TrainingSessionFinalizeRequest',{});assert 'properties' in fr,'G8a';fp2=fr.get('properties',{});assert 'attendance_completed' in fp2,'G8b';assert 'review_completed' in fp2,'G8c';assert 'publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost' not in f,'G9a';assert 'closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost' not in f,'G9b';assert any(x in f for x in ['scheduleTrainingSession','ScheduleTrainingSession']),'G10a';assert any(x in f for x in ['finalizeTrainingSession','FinalizeTrainingSession']),'G10b';print('PASS AR_273: Gates 1-10 OK')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-09T08:48:33.840423+00:00
**Behavior Hash**: 81ca8d9271b6b2f55f7bfea80df94d0562df78dbdf6ac575f305f5522107f1ec
**Evidence File**: `docs/hbtrack/evidence/AR_273/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 284e769
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_273_284e769/result.json`

### Selo Humano em 284e769
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-10T00:26:23.189626+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_273_284e769/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_273/executor_main.log`
