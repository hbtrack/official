# AR_005 — Router match_events — schemas canônicos ScoutEventCreate/ScoutEventRead e await AsyncSession

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.5
**Plano Fonte**: `docs/_canon/planos/matchservice.json`

## Descrição
CONTEXTO: O endpoint POST /matches/{match_id}/events em app/api/v1/routers/match_events.py tem três problemas confirmados: (A) importa e usa MatchEventCreate (schema antigo com campos errados) em vez de ScoutEventCreate — causando mismatch com o service refatorado na task 004; (B) chamadas db.commit() e db.refresh(event) sem await — bug silencioso em AsyncSession que produz RuntimeWarning de coroutine não aguardada e comportamento não determinístico; (C) docstring lista event_type codes inválidos (goal_7m, own_goal, shot_on_target) — não existem no enum CanonicalEventType.

AÇÃO (patch mínimo):
1) IMPORTS: trocar MatchEventCreate → ScoutEventCreate; MatchEventResponse → ScoutEventRead.
2) ASSINATURA do handler: payload: ScoutEventCreate; return type: ScoutEventRead; response_model=ScoutEventRead.
3) CORPO: event = await service.create(match_id, payload); await db.commit(); await db.refresh(event).
4) DOCSTRING: remover lista de event_type inválidos; substituir por: 'event_type canônicos (11): goal, shot, seven_meter, goalkeeper_save, turnover, foul, exclusion_2min, yellow_card, red_card, substitution, timeout — ref: event_types table'.
5) Aplicar mesma correção de await nas rotas: update_match_event, correct_match_event, delete_match_event, bulk_create_match_events.
6) Rota scoped scoped_add_event_to_match: mesma atualização de schema (ScoutEventCreate/ScoutEventRead) e await.

ARQUIVOS AFETADOS: Hb Track - Backend/app/api/v1/routers/match_events.py (único). NÃO criar arquivo novo.

## Critérios de Aceite
1) POST /matches/{id}/events com payload ScoutEventCreate válido retorna HTTP 201 e JSON com todos os campos de ScoutEventRead (id, match_id, is_shot, is_goal, period_number, game_time_seconds, score_our, score_opponent, event_type, outcome, source, created_at, created_by_user_id).
2) POST com event_type='goal_7m' retorna HTTP 422 Unprocessable Entity.
3) POST com event_type='goalkeeper_save' e related_event_id=null retorna HTTP 422.
4) Nenhum RuntimeWarning de coroutine não aguardada nos logs do uvicorn ao chamar o endpoint.
5) python -c 'from app.api.v1.routers.match_events import add_event_to_match' executa sem ImportError.
6) pytest -k 'test_add_event_to_match' passa com response_model=ScoutEventRead.

## SSOT Touches
- [ ] docs/ssot/openapi.json

## Validation Command (Contrato)
```
python -c "import pathlib; c=pathlib.Path('Hb Track - Backend/app/api/v1/routers/match_events.py').read_text(encoding='utf-8'); checks={'ScoutEventCreate import':('ScoutEventCreate' in c),'await service.create':('event = await service.create(match_id, payload)' in c),'await db.commit':('await db.commit()' in c),'await db.refresh':('await db.refresh(event)' in c),'bulk_create':('created = await service.bulk_create(match_id, events)' in c),'event_type canonicos':('event_type canônicos (11)' in c)}; fails=[k for k,v in checks.items() if not v]; [print(f'FAIL: {f}') for f in fails]; exit(len(fails)) if fails else print(f'PASS: match_events router has all required patterns ({len(checks)} checks)')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_005/executor_main.log`

## Notas do Arquiteto
Task 005 tem dependência de task 004: o service.create() com assinatura (match_id, payload) deve estar implementado antes de corrigir o router. Executor deve executar 004 antes de 005.

## Riscos
- Trocar MatchEventCreate por ScoutEventCreate pode quebrar outros endpoints que ainda importam MatchEventCreate — auditar imports antes de remover.
- Corrigir await em bulk_create pode alterar o comportamento de rollback em batch — testar cenário de erro parcial.
- A rota scoped usa _get_match_scoped() com validação de team_id — garantir que a validação de roster também verifica match_id correto após o patch.

## Análise de Impacto
- Arquivos afetados: `Hb Track - Backend/app/api/v1/routers/match_events.py`
- Mudança no Schema? Não
- Risco de Regressão? Médio

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução em 9bebd2c
**Status Final**: ❌ FALHA
**Comando**: `pytest "Hb Track - Backend/tests/" -k "test_add_event" -x --tb=short -q`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_005_endpoint_match_events.log`
**Python Version**: 3.11.9

### Execução em 9bebd2c
**Status Final**: ❌ FALHA
**Comando**: `pytest "Hb Track - Backend/tests/" -k "test_add_event" -x --tb=short -q`
**Exit Code**: 5
**Evidence File**: `docs/hbtrack/evidence/AR_005_endpoint_match_events.log`
**Python Version**: 3.11.9

### Execução em 9bebd2c
**Status Final**: ✅ SUCESSO
**Comando**: `pytest "Hb Track - Backend/tests/" -k "test_add_event" -x --tb=short -q`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_005_endpoint_match_events.log`
**Python Version**: 3.11.9

> 📋 Kanban routing: Arquiteto: Output não-determinístico: behavior_hash diverge nos 3 runs (exit 0 em todos, mas hash diferente)

### Execução Executor em 8d39a14
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `pytest "Hb Track - Backend/tests/" -k "test_add_event" -x --tb=short -q`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T20:54:30.972443+00:00
**Behavior Hash**: 202107661471687079ebf21ccc95b6bf2e4139dd1855081e51303beaa383943f
**Evidence File**: `docs/hbtrack/evidence/AR_005/executor_main.log`
**Python Version**: 3.11.9

> 📋 Kanban routing: Arquiteto: Output não-determinístico: behavior_hash diverge nos 3 runs (exit 0 em todos, mas hash diferente)

### Execução Executor em 8d39a14
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import pathlib; c=pathlib.Path('Hb Track - Backend/app/api/v1/routers/match_events.py').read_text(encoding='utf-8'); checks={'ScoutEventCreate import':('ScoutEventCreate' in c),'await service.create':('event = await service.create(match_id, payload)' in c),'await db.commit':('await db.commit()' in c),'await db.refresh':('await db.refresh(event)' in c),'bulk_create':('created = await service.bulk_create(match_id, events)' in c),'event_type canonicos':('event_type canônicos (11)' in c)}; fails=[k for k,v in checks.items() if not v]; [print(f'FAIL: {f}') for f in fails]; exit(len(fails)) if fails else print(f'PASS: match_events router has all required patterns ({len(checks)} checks)')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T20:56:01.986740+00:00
**Behavior Hash**: c17e182c19318e8706945dc0b00fc99725cd3c705e15862be65b2956a4c5cd7c
**Evidence File**: `docs/hbtrack/evidence/AR_005/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 8d39a14
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_005_8d39a14/result.json`

### Selo Humano em 8d39a14
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-24T20:56:19.263234+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_005_8d39a14/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_005/executor_main.log`
