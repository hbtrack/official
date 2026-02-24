# AR_003 — Schemas Pydantic Canônicos de Scout

**Status**: 🔴 REJEITADO
**Plano Fonte**: `docs/_canon/planos/matchservice.json`

### 🛠️ Especificação Técnica (Arquiteto)
CONTEXTO: O arquivo app/schemas/match_events.py contém um EventType enum com códigos inválidos (goal_7m, own_goal, shot_on_target, assist, technical_foul) que NÃO existem na tabela event_types do banco. Os schemas atuais (MatchEventBase/Create) mapeiam campos inexistentes ('minute', 'period', 'x_position', 'y_position') em vez dos campos reais do banco (period_number, game_time_seconds, x_coord, y_coord). O arquivo app/schemas/matches_subresources.py usa event_type como str livre com campo 'points' que também não existe na tabela.

AÇÃO: Substituir o conteúdo de app/schemas/match_events.py pelos schemas canônicos abaixo. NÃO criar arquivo novo — editar o existente.

1) ENUM CANÔNICO (substituir a classe EventType atual):
class CanonicalEventType(str, Enum):
    goal = 'goal'
    shot = 'shot'
    seven_meter = 'seven_meter'
    goalkeeper_save = 'goalkeeper_save'
    turnover = 'turnover'
    foul = 'foul'
    exclusion_2min = 'exclusion_2min'
    yellow_card = 'yellow_card'
    red_card = 'red_card'
    substitution = 'substitution'
    timeout = 'timeout'
# Manter alias EventType = CanonicalEventType para não quebrar imports.

2) SCHEMA ScoutEventCreate (substituir MatchEventCreate):
Campos obrigatórios: team_id (UUID), period_number (int >= 1), game_time_seconds (int >= 0), phase_of_play (str — FK phases_of_play.code), advantage_state (str — FK advantage_states.code), score_our (int >= 0), score_opponent (int >= 0), event_type (CanonicalEventType), outcome (str, max 64), is_shot (bool), is_goal (bool), source (Literal['live','video','post_game_correction']).
Campos opcionais: athlete_id, assisting_athlete_id, secondary_athlete_id, opponent_team_id, possession_id, event_subtype, x_coord (0-100), y_coord (0-100), related_event_id, notes.
Validation: quando event_type='goalkeeper_save', related_event_id é OBRIGATÓRIO (validator deve levantar ValueError se ausente).

3) SCHEMA ScoutEventRead (substituir MatchEventResponse):
Todos os campos de ScoutEventCreate mais: id (UUID), match_id (UUID), created_at (datetime), created_by_user_id (UUID).
model_config = ConfigDict(from_attributes=True).

4) Manter MatchEventList, AthleteMatchStats e TeamMatchStats mas corrigir as referências ao enum (EventType.goal_7m → remover; EventType.save → goalkeeper_save; EventType.card → yellow_card/red_card; EventType.other → remover).

5) Manter MatchEventCorrection e MatchEventUpdate sem breaking changes (apenas corrigir referências ao enum).

## Critérios de Aceite
- Import ScoutEventCreate, ScoutEventRead, CanonicalEventType executa sem ImportError
- CanonicalEventType não contém valores inválidos: goal_7m, own_goal, shot_on_target, assist, technical_foul
- ScoutEventCreate aceita campos DB-aligned: period_number, game_time_seconds, x_coord, y_coord, is_shot, is_goal, source, phase_of_play, advantage_state, score_our, score_opponent, event_subtype, related_event_id
- ScoutEventCreate validation: goalkeeper_save com related_event_id=None levanta ValidationError
- Alias EventType = CanonicalEventType funciona corretamente (backward compatibility)

## Write Scope
- Hb Track - Backend/app/schemas/match_events.py

## Validation Command (Contrato)
```
import sys, uuid
sys.path.insert(0, 'Hb Track - Backend')
from app.schemas.match_events import ScoutEventCreate, CanonicalEventType, EventType
FIXED = uuid.UUID('00000000-0000-0000-0000-000000000001')
invalid = [v for v in ['goal_7m','own_goal','shot_on_target','assist','technical_foul'] if v in [e.value for e in CanonicalEventType]]
assert not invalid, f'Enum invalido: {invalid}'
base = {'team_id': FIXED, 'period_number': 1, 'game_time_seconds': 300, 'phase_of_play': 'attack', 'advantage_state': 'even', 'score_our': 5, 'score_opponent': 3, 'event_type': 'goal', 'outcome': 'success', 'is_shot': True, 'is_goal': True, 'source': 'live', 'x_coord': 50.0, 'y_coord': 40.0}
e = ScoutEventCreate(**base)
assert e.period_number == 1 and e.game_time_seconds == 300 and e.x_coord == 50.0 and e.y_coord == 40.0
assert EventType is CanonicalEventType
gk_ok = False
try:
    ScoutEventCreate(**{**base, 'event_type': 'goalkeeper_save', 'related_event_id': None})
except ValueError as err:
    gk_ok = 'goalkeeper_save' in str(err).lower() and 'related_event_id' in str(err).lower()
assert gk_ok, 'goalkeeper_save nao levantou ValidationError correta'
print('PASS: Schemas Pydantic canonicos OK')
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_003/executor_main.log`

## Rollback Plan (Contrato)
```
git checkout -- Hb Track - Backend/app/schemas/match_events.py
```

## Análise de Impacto
**Escopo**: Schemas Pydantic para match events (Scout canônico)

**Impacto**:
- Substituição de enum EventType (legado) por CanonicalEventType (sem códigos inválidos)
- Novos schemas ScoutEventCreate/ScoutEventRead alinhados com tabela match_events do DB
- Campos renomeados para match DB: period_number (era 'period'), game_time_seconds (era 'minute'), x_coord/y_coord (eram 'x_position'/'y_position')
- Validação de goalkeeper_save requer related_event_id obrigatório
- Alias EventType mantém compatibilidade com imports existentes no router

**Risco**: Baixo (alias preserva imports existentes, campos DB-aligned já eram esperados por models)

**Implementação**: Código já presente no arquivo desde implementação anterior (verificado via grep). Esta AR gera evidence canônica retroativamente.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 38b62a5
**Status Executor**: ❌ FALHA
**Comando**: `python temp/validate_ar003.py`
**Exit Code**: 1
**Timestamp UTC**: 2026-02-24T17:01:44.472025+00:00
**Behavior Hash**: 5dad134366f921aff3a99f1d61cfd711646c40b192c16fc2b55344e7ed2fd3e7
**Evidence File**: `docs/hbtrack/evidence/AR_003/executor_main.log`
**Python Version**: 3.11.9

### Execução Executor em 38b62a5
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python temp/validate_ar003.py`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-24T17:02:22.291617+00:00
**Behavior Hash**: 4f4879b1d369502185309595bf57110e0bfedcf1191196f944b6b29cbb23bab3
**Evidence File**: `docs/hbtrack/evidence/AR_003/executor_main.log`
**Python Version**: 3.11.9

> 📋 Kanban routing: Arquiteto: Executor reported exit 0 but Testador got exit 1

### Verificacao Testador em 494d48a
**Status Testador**: 🔴 REJEITADO
**Consistency**: AH_DIVERGENCE
**Triple-Run**: TRIPLE_FAIL (3x)
**Exit Testador**: 1 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_003_494d48a/result.json`
