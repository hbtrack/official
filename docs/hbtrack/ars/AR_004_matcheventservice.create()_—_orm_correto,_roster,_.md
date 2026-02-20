# AR_004 — MatchEventService.create() — ORM correto, roster, is_shot e link goalkeeper_save

**Status**: 🏗️ EM_EXECUCAO
**Versão do Protocolo**: 1.0.5
**Plano Fonte**: `docs/_canon/planos/matchservice.json`

## Descrição
CONTEXTO: O método MatchEventService.create() em app/services/match_event_service.py apresenta quatro defeitos críticos detectados via leitura do código frente ao schema.sql e openapi.json: (A) mapeia campos inexistentes no modelo ORM — event.minute, event.period, event.x_position, event.y_position não existem; os campos reais são period_number, game_time_seconds, x_coord, y_coord; (B) valida atleta em team_registration em vez de match_roster — são entidades distintas; a regra correta (schema.sql match_roster) é: SELECT match_roster WHERE match_id=:match_id AND athlete_id=:athlete_id AND is_available=true; (C) não preenche is_shot no ORM — campo NOT NULL no banco; o valor canônico deve vir de SELECT event_types WHERE code=data.event_type, campo is_shot; (D) não implementa link goalkeeper_save→related_event_id: quando event_type='goalkeeper_save', o service deve verificar que related_event_id referencia um evento existente na mesma partida com event_type IN ('shot','seven_meter').

AÇÃO (patch mínimo, sem refactor amplo):
1) Substituir _validate_athlete_in_roster: query em match_roster (match_id + athlete_id + is_available=true); aplicar para athlete_id, assisting_athlete_id e secondary_athlete_id quando presentes.
2) Adicionar lookup: SELECT event_types WHERE code=data.event_type → is_shot_db = row.is_shot.
3) Adicionar regra goalkeeper_save: se event_type=='goalkeeper_save', verificar que related_event_id não é None (redundante com Pydantic, mas defensivo) E que match_events WHERE id=related_event_id AND match_id=match_id AND event_type IN ('shot','seven_meter') retorna linha — raise ValidationError se não.
4) Corrigir instanciação do ORM MatchEvent: usar period_number, game_time_seconds, x_coord, y_coord, is_shot=is_shot_db, is_goal=data.is_goal e todos os demais campos mapeados do payload ScoutEventCreate.
5) Adicionar comentário inline sobre score snapshot: '# score_our/score_opponent representam o placar NO MOMENTO do evento; o service NÃO recalcula — persiste o valor informado pelo chamador'.

ARQUIVOS AFETADOS: Hb Track - Backend/app/services/match_event_service.py (único). NÃO criar arquivo novo.

## Critérios de Aceite
1) pytest -k 'test_create_match_event' passa sem AttributeError (nenhuma referência a event.minute, event.period, event.x_position, event.y_position).
2) Criar evento com athlete_id ausente em match_roster retorna ValidationError (HTTP 422 ou exceção de serviço).
3) Criar goalkeeper_save sem related_event_id retorna ValidationError.
4) Criar goalkeeper_save com related_event_id apontando para evento não-shot/seven_meter retorna ValidationError com mensagem 'related_event must be a shot or seven_meter'.
5) Evento persistido no banco tem is_shot preenchido conforme event_types.is_shot (não NULL).
6) Evento persistido tem period_number e game_time_seconds preenchidos (não NULL); x_coord e y_coord presentes quando informados.
7) score_our e score_opponent no banco correspondem aos valores enviados no payload (passthrough, sem recálculo).

## SSOT Touches
- [ ] docs/ssot/schema.sql
- [ ] docs/ssot/openapi.json

## Validation Command (Contrato)
```
pytest "Hb Track - Backend/tests/" -k "match_event" -x --tb=short -q
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_004_match_event_service_create.log`

## Notas do Arquiteto
O lookup em event_types pressupõe que a tabela existe e está populada (assumption declarada). Se event_types não existir no banco de dev/test, o Executor deve bloquear (BLOCKED_INPUT 4) e reportar ao Arquiteto antes de prosseguir.

## Riscos
- Se event_types não estiver no schema.sql canônico ou não existir no banco, o lookup falhará em runtime — verificar schema.sql antes de executar.
- Remover _validate_athlete_in_roster pode quebrar outros callers do método — auditar usos no codebase antes de remover.
- bulk_create também chama lógica de validação de roster — verificar se precisa ser atualizado em conjunto (pode ser escopo da mesma task ou task separada).

## Análise de Impacto
- Arquivos afetados: `Hb Track - Backend/app/services/match_event_service.py`
- Mudança no Schema? Não
- Risco de Regressão? Médio

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em 9bebd2c
**Status Final**: ❌ FALHA
**Comando**: `pytest "Hb Track - Backend/tests/" -k "match_event" -x --tb=short -q`
**Exit Code**: 1
**Evidence File**: `docs/hbtrack/evidence/AR_004_match_event_service_create.log`
**Python Version**: 3.11.9


### Execução em 9bebd2c
**Status Final**: ❌ FALHA
**Comando**: `pytest "Hb Track - Backend/tests/" -k "match_event" -x --tb=short -q`
**Exit Code**: 5
**Evidence File**: `docs/hbtrack/evidence/AR_004_match_event_service_create.log`
**Python Version**: 3.11.9


### Execução em 9bebd2c
**Status Final**: ✅ SUCESSO
**Comando**: `pytest "Hb Track - Backend/tests/" -k "match_event" -x --tb=short -q`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_004_match_event_service_create.log`
**Python Version**: 3.11.9

