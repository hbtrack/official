# CompetitionMatchResponse

Schema de resposta para jogo.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**competition_id** | **string** |  | [default to undefined]
**phase_id** | **string** |  | [optional] [default to undefined]
**external_reference_id** | **string** |  | [optional] [default to undefined]
**home_team_id** | **string** |  | [optional] [default to undefined]
**away_team_id** | **string** |  | [optional] [default to undefined]
**is_our_match** | **boolean** |  | [optional] [default to undefined]
**our_team_is_home** | **boolean** |  | [optional] [default to undefined]
**linked_match_id** | **string** |  | [optional] [default to undefined]
**match_date** | **string** |  | [optional] [default to undefined]
**match_time** | **string** |  | [optional] [default to undefined]
**match_datetime** | **string** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**round_number** | **number** |  | [optional] [default to undefined]
**round_name** | **string** |  | [optional] [default to undefined]
**home_score** | **number** |  | [optional] [default to undefined]
**away_score** | **number** |  | [optional] [default to undefined]
**home_score_extra** | **number** |  | [optional] [default to undefined]
**away_score_extra** | **number** |  | [optional] [default to undefined]
**home_score_penalties** | **number** |  | [optional] [default to undefined]
**away_score_penalties** | **number** |  | [optional] [default to undefined]
**status** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [optional] [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]
**home_team** | [**CompetitionOpponentTeamResponse**](CompetitionOpponentTeamResponse.md) |  | [optional] [default to undefined]
**away_team** | [**CompetitionOpponentTeamResponse**](CompetitionOpponentTeamResponse.md) |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionMatchResponse } from './api';

const instance: CompetitionMatchResponse = {
    id,
    competition_id,
    phase_id,
    external_reference_id,
    home_team_id,
    away_team_id,
    is_our_match,
    our_team_is_home,
    linked_match_id,
    match_date,
    match_time,
    match_datetime,
    location,
    round_number,
    round_name,
    home_score,
    away_score,
    home_score_extra,
    away_score_extra,
    home_score_penalties,
    away_score_penalties,
    status,
    notes,
    created_at,
    updated_at,
    home_team,
    away_team,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
