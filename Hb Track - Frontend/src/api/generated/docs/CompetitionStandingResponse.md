# CompetitionStandingResponse

Schema de resposta para classificação.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**competition_id** | **string** |  | [default to undefined]
**phase_id** | **string** |  | [optional] [default to undefined]
**opponent_team_id** | **string** |  | [default to undefined]
**position** | **number** |  | [default to undefined]
**group_name** | **string** |  | [optional] [default to undefined]
**points** | **number** |  | [optional] [default to undefined]
**played** | **number** |  | [optional] [default to undefined]
**wins** | **number** |  | [optional] [default to undefined]
**draws** | **number** |  | [optional] [default to undefined]
**losses** | **number** |  | [optional] [default to undefined]
**goals_for** | **number** |  | [optional] [default to undefined]
**goals_against** | **number** |  | [optional] [default to undefined]
**goal_difference** | **number** |  | [optional] [default to undefined]
**recent_form** | **string** |  | [optional] [default to undefined]
**qualification_status** | **string** |  | [optional] [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]
**opponent_team** | [**CompetitionOpponentTeamResponse**](CompetitionOpponentTeamResponse.md) |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionStandingResponse } from './api';

const instance: CompetitionStandingResponse = {
    id,
    competition_id,
    phase_id,
    opponent_team_id,
    position,
    group_name,
    points,
    played,
    wins,
    draws,
    losses,
    goals_for,
    goals_against,
    goal_difference,
    recent_form,
    qualification_status,
    updated_at,
    opponent_team,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
