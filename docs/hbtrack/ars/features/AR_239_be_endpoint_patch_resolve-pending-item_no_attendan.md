# AR_239 — BE: endpoint PATCH resolve-pending-item no attendance router (AR-TRAIN-055)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Adicionar endpoint PATCH /api/v1/attendance/pending-items/{item_id}/resolve ao router de attendance.

Contexto: training_pending_service.py ja tem resolve_pending_item() implementado (linha 210). O router attendance.py lista pending items (GET /attendance/sessions/{id}/pending-items, ja no openapi.json) mas nao tem o endpoint de resolucao.

Contrato alvo: CONTRACT-TRAIN-100
- Metodo: PATCH
- Path: /api/v1/attendance/pending-items/{item_id}/resolve
- Body: {resolution: string, new_status: 'present'|'absent'|'justified'}
- Response: PendingItem completo
- Auth: apenas treinador/coach pode resolver (INV-TRAIN-067)
- INV-TRAIN-066: atleta pode enviar justificativa mas NAO pode resolver

PASSOSS:
1. Ler Hb Track - Backend/app/api/v1/routers/attendance.py para entender estrutura existente
2. Adicionar endpoint @router.patch('/pending-items/{item_id}/resolve') chamando training_pending_service.resolve_pending_item()
3. Adicionar schema de request (ResolveItemRequest) se necessario
4. Executar gen_docs_ssot.py para atualizar openapi.json
5. Rodar hb report 239

## Critérios de Aceite
AC-001: GET python -c com io.open openapi.json mostra path /api/v1/attendance/pending-items/{item_id}/resolve com metodo PATCH.
AC-002: operationId do novo endpoint contem 'resolve' ou 'pending'.
AC-003: suite 594+ passed, 0 failed apos adicao.

## Write Scope
- Hb Track - Backend/app/api/v1/routers/attendance.py
- Hb Track - Backend/docs/ssot/openapi.json
- Hb Track - Backend/docs/ssot/manifest.json

## Validation Command (Contrato)
```
python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; targets=[p for p in paths if 'pending-items' in p and 'resolve' in p]; print('PASS: resolve endpoint found:', targets) if targets else (print('FAIL: resolve pending-items endpoint missing'), __import__('sys').exit(1))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_239/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/api/v1/routers/attendance.py
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- INV-TRAIN-067: apenas treinador/coach pode resolver — RBAC deve ser aplicado no decorator do endpoint.
- INV-TRAIN-066: atleta pode submeter justificativa (campo 'athlete_notes') mas NAO pode alterar status — se o service ja enforcar isso, o router apenas repassa.
- Verificar se o schema PendingItemResolve ja existe em app/schemas/ ou se precisa ser criado.
- training_pending_service.resolve_pending_item() pode ter assinatura diferente — ler antes de implementar.

## Análise de Impacto

**Arquivos modificados:**
- `Hb Track - Backend/app/api/v1/routers/attendance.py` — adicionar PATCH endpoint + schema `ResolveItemRequest` inline
- `Hb Track - Backend/docs/ssot/openapi.json` — regenerado via gen_docs_ssot.py

**Método do serviço:** `TrainingPendingService.resolve_pending_item(item_id, resolved_by_user_id)` — linha 210, já implementado, retorna dict com status 'resolved'.

**RBAC:** INV-TRAIN-067 — endpoint protegido por `get_current_user`; service já enforça que atleta não pode resolver outro atleta.

**Schema de request:** `ResolveItemRequest` será definido inline no router (sem arquivo separado de schema).

**Impacto suite:** Zero — nenhum teste existente cobre o path `/attendance/pending-items/{item_id}/resolve`; adição é aditiva.

**Dependência de geração:** gen_docs_ssot.py deve ser executado após adição para atualizar openapi.json.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; targets=[p for p in paths if 'pending-items' in p and 'resolve' in p]; print('PASS: resolve endpoint found:', targets) if targets else (print('FAIL: resolve pending-items endpoint missing'), __import__('sys').exit(1))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:11:42.092906+00:00
**Behavior Hash**: d2a808965f134fd16d51ade4d7f98f61eb14b1fd9421167d047eed00ea3ad6fa
**Evidence File**: `docs/hbtrack/evidence/AR_239/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em a7ab568
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import json,io; spec=json.load(io.open('Hb Track - Backend/docs/ssot/openapi.json',encoding='utf-8')); paths=spec['paths']; targets=[p for p in paths if 'pending-items' in p and 'resolve' in p]; print('PASS: resolve endpoint found:', targets) if targets else (print('FAIL: resolve pending-items endpoint missing'), __import__('sys').exit(1))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-04T18:12:38.030932+00:00
**Behavior Hash**: d2a808965f134fd16d51ade4d7f98f61eb14b1fd9421167d047eed00ea3ad6fa
**Evidence File**: `docs/hbtrack/evidence/AR_239/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em a7ab568
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_239_a7ab568/result.json`

### Selo Humano em a7ab568
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-04T18:38:52.920176+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_239_a7ab568/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_239/executor_main.log`
