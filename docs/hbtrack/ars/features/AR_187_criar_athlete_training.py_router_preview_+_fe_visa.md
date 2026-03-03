# AR_187 — Criar athlete_training.py router (preview) + FE visao pre-treino atleta com wellness gate

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
BACKEND: Criar Hb Track - Backend/app/api/v1/routers/athlete_training.py com endpoint: GET /athlete/training-sessions/{session_id}/preview — retorna dados da sessao pre-treino para atleta: exercicios (lista minima: nome, descricao, media_urls se disponivel), horario, objetivo, wellness_blocked=bool (resultado de athlete_content_gate_service.check_content_access). Se wellness_blocked=True: retornar apenas info basica (nome da sessao, horario) mais flag wellness_blocked=True. Se wellness_blocked=False: retornar exercicios com detalhes + media. Permissao: atleta autenticado da sessao. Registrar o router em Hb Track - Backend/app/api/v1/api.py (adicionar include_router). FRONTEND: Criar Hb Track - Frontend/src/app/(athlete)/training/[sessionId]/page.tsx — tela pre-treino: (1) se wellness_blocked=True: mostrar banner de alerta pedindo preenchimento de wellness antes de ver conteudo completo; (2) se wellness_blocked=False: mostrar exercicios com nome/descricao/media (preview). Criar Hb Track - Frontend/src/lib/api/athlete-training.ts com funcao getTrainingPreview(sessionId). INV-TRAIN-068: atleta PODE ver treino antes. INV-TRAIN-069: midia acessivel ao atleta. INV-TRAIN-071: wellness missing bloqueia conteudo completo. INV-TRAIN-076: wellness obrigatorio. INV-TRAIN-078: progresso exige compliance wellness. PROIBIDO: nao alterar athlete_content_gate_service.py.

## Critérios de Aceite
1) Hb Track - Backend/app/api/v1/routers/athlete_training.py existe com endpoint /preview. 2) athlete_training router registrado em api.py. 3) athlete_content_gate_service.check_content_access chamado no endpoint. 4) Response inclui wellness_blocked bool. 5) Hb Track - Frontend/src/app/(athlete)/training/[sessionId]/page.tsx existe. 6) Hb Track - Frontend/src/lib/api/athlete-training.ts existe. 7) Tela mostra banner de wellness se wellness_blocked=True (INV-TRAIN-071).

## Write Scope
- Hb Track - Backend/app/api/v1/routers/athlete_training.py
- Hb Track - Backend/app/api/v1/api.py
- Hb Track - Frontend/src/lib/api/athlete-training.ts
- Hb Track - Frontend/src/app/*/training

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Backend'; r=open(os.path.join(b,'app','api','v1','routers','athlete_training.py')).read(); assert 'preview' in r, 'router missing preview endpoint'; assert 'wellness_blocked' in r or 'check_content_access' in r, 'router missing wellness gate call'; api=open(os.path.join(b,'app','api','v1','api.py')).read(); assert 'athlete_training' in api, 'api.py missing athlete_training router include'; fb='Hb Track - Frontend'; fe=os.path.join(fb,'src','lib','api','athlete-training.ts'); assert os.path.exists(fe), 'athlete-training.ts missing'; fp=os.path.join(fb,'src','app','(athlete)','training'); assert os.path.exists(fp), 'athlete training page missing'; print('PASS AR_187')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_187/executor_main.log`

## Notas do Arquiteto
athlete_content_gate_service.py tem check_content_access(session_id, user_id) — chamar para determinar wellness_blocked. Se AccessGated retornado: wellness_blocked=True; se AccessGranted: wellness_blocked=False. Verificar assinatura exata do service antes de codificar o router. api.py: adicionar include_router(athlete_training.router, prefix='/athlete', tags=['athlete-training']).

## Riscos
- athlete_training.py pode conflitar com athlete_states.py ou athletes.py — verificar rotas existentes antes de registrar
- A tela FE /athlete/training/[sessionId] pode ja existir parcialmente (athlete/training path) — inspecionar src/app/(athlete)/ antes
- Media de exercicios depende de exercise_media (AR_181) — verificar se ExerciseMedia model esta corretamente importado no servico de preview

## Análise de Impacto
**Executor**: 2026-03-01

- **BE novo**: `athlete_training.py` router com 1 endpoint `GET /training-sessions/{session_id}/preview`
- **`check_content_access(athlete_id, resource_type, ref_date)`**: assinatura real toma `athlete_id` (não `session_id`) → necessário lookup por `person_id` (mesmo padrão AR_185)
- **`AthleteContentGateService(db)`**: construtor simples sem contexto
- **`AccessGated`** → `wellness_blocked=True`; **`AccessGranted`** → `wellness_blocked=False`
- **api.py**: 1 import + 1 `include_router` com `prefix="/athlete"`
- **FE**: `(athlete)` folder inexistente → criar toda a hierarquia; `athlete-training.ts` e `[sessionId]/page.tsx`
- INV-TRAIN-071: FE deve mostrar banner wellness se `wellness_blocked=True`
- Zero migrations; `athlete_content_gate_service.py` intocado (proibido)

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Backend'; r=open(os.path.join(b,'app','api','v1','routers','athlete_training.py')).read(); assert 'preview' in r, 'router missing preview endpoint'; assert 'wellness_blocked' in r or 'check_content_access' in r, 'router missing wellness gate call'; api=open(os.path.join(b,'app','api','v1','api.py')).read(); assert 'athlete_training' in api, 'api.py missing athlete_training router include'; fb='Hb Track - Frontend'; fe=os.path.join(fb,'src','lib','api','athlete-training.ts'); assert os.path.exists(fe), 'athlete-training.ts missing'; fp=os.path.join(fb,'src','app','(athlete)','training'); assert os.path.exists(fp), 'athlete training page missing'; print('PASS AR_187')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T05:13:05.770038+00:00
**Behavior Hash**: a5c9f72f97dcc720a1e46649fdf964713375f7592d6e4d7ea31538b316a6fbfb
**Evidence File**: `docs/hbtrack/evidence/AR_187/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_187_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T05:38:59.223382+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_187_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_187/executor_main.log`
