# AR_005 — Router match_events — schemas canônicos ScoutEventCreate/ScoutEventRead e await AsyncSession

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.0.5

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
pytest "Hb Track - Backend/tests/" -k "test_add_event" -x --tb=short -q
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_005_endpoint_match_events.log`

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

