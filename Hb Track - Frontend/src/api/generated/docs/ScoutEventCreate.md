# ScoutEventCreate

Schema para criação de evento de scout. Campos alinhados com a tabela match_events do banco de dados.  Validações especiais: - event_type=\'goalkeeper_save\' exige related_event_id obrigatório

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** | ID do time que executou o evento | [default to undefined]
**period_number** | **number** | Número do período (1, 2, etc.) | [default to undefined]
**game_time_seconds** | **number** | Tempo de jogo em segundos | [default to undefined]
**phase_of_play** | **string** | FK para phases_of_play.code | [default to undefined]
**advantage_state** | **string** | FK para advantage_states.code | [default to undefined]
**score_our** | **number** | Placar do nosso time | [default to undefined]
**score_opponent** | **number** | Placar do adversário | [default to undefined]
**event_type** | [**CanonicalEventType**](CanonicalEventType.md) | Tipo do evento (canônico) | [default to undefined]
**outcome** | **string** | Resultado do evento | [default to undefined]
**is_shot** | **boolean** | Se o evento é uma finalização | [default to undefined]
**is_goal** | **boolean** | Se o evento resultou em gol | [default to undefined]
**source** | **string** | Fonte do registro | [default to undefined]
**athlete_id** | **string** |  | [optional] [default to undefined]
**assisting_athlete_id** | **string** |  | [optional] [default to undefined]
**secondary_athlete_id** | **string** |  | [optional] [default to undefined]
**opponent_team_id** | **string** |  | [optional] [default to undefined]
**possession_id** | **string** |  | [optional] [default to undefined]
**event_subtype** | **string** |  | [optional] [default to undefined]
**x_coord** | **number** |  | [optional] [default to undefined]
**y_coord** | **number** |  | [optional] [default to undefined]
**related_event_id** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ScoutEventCreate } from './api';

const instance: ScoutEventCreate = {
    team_id,
    period_number,
    game_time_seconds,
    phase_of_play,
    advantage_state,
    score_our,
    score_opponent,
    event_type,
    outcome,
    is_shot,
    is_goal,
    source,
    athlete_id,
    assisting_athlete_id,
    secondary_athlete_id,
    opponent_team_id,
    possession_id,
    event_subtype,
    x_coord,
    y_coord,
    related_event_id,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
