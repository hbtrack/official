# ScoutEventRead

Schema de resposta para evento de scout. Inclui todos os campos de ScoutEventCreate mais campos de auditoria.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**period_number** | **number** |  | [default to undefined]
**game_time_seconds** | **number** |  | [default to undefined]
**phase_of_play** | **string** |  | [default to undefined]
**advantage_state** | **string** |  | [default to undefined]
**score_our** | **number** |  | [default to undefined]
**score_opponent** | **number** |  | [default to undefined]
**event_type** | [**CanonicalEventType**](CanonicalEventType.md) |  | [default to undefined]
**outcome** | **string** |  | [default to undefined]
**is_shot** | **boolean** |  | [default to undefined]
**is_goal** | **boolean** |  | [default to undefined]
**source** | **string** |  | [default to undefined]
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
**id** | **string** |  | [default to undefined]
**match_id** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**created_by_user_id** | **string** |  | [default to undefined]

## Example

```typescript
import { ScoutEventRead } from './api';

const instance: ScoutEventRead = {
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
    id,
    match_id,
    created_at,
    created_by_user_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
