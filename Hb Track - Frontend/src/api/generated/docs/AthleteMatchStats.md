# AthleteMatchStats

Schema para estatísticas agregadas de um atleta em uma partida. Campos corrigidos para usar apenas tipos canônicos.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** |  | [default to undefined]
**match_id** | **string** |  | [default to undefined]
**goals** | **number** |  | [optional] [default to 0]
**goals_7m** | **number** |  | [optional] [default to 0]
**shots** | **number** |  | [optional] [default to 0]
**saves** | **number** |  | [optional] [default to 0]
**goals_conceded** | **number** |  | [optional] [default to 0]
**yellow_cards** | **number** |  | [optional] [default to 0]
**red_cards** | **number** |  | [optional] [default to 0]
**two_minutes** | **number** |  | [optional] [default to 0]
**turnovers** | **number** |  | [optional] [default to 0]
**minutes_played** | **number** |  | [optional] [default to 0]

## Example

```typescript
import { AthleteMatchStats } from './api';

const instance: AthleteMatchStats = {
    athlete_id,
    match_id,
    goals,
    goals_7m,
    shots,
    saves,
    goals_conceded,
    yellow_cards,
    red_cards,
    two_minutes,
    turnovers,
    minutes_played,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
