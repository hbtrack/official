# CompetitionMatchCreate

Schema para criação de jogo da competição.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**phase_id** | **string** |  | [optional] [default to undefined]
**external_reference_id** | **string** |  | [optional] [default to undefined]
**home_team_id** | **string** |  | [optional] [default to undefined]
**away_team_id** | **string** |  | [optional] [default to undefined]
**is_our_match** | **boolean** |  | [optional] [default to false]
**our_team_is_home** | **boolean** |  | [optional] [default to undefined]
**match_date** | **string** |  | [optional] [default to undefined]
**match_time** | **string** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**round_number** | **number** |  | [optional] [default to undefined]
**round_name** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionMatchCreate } from './api';

const instance: CompetitionMatchCreate = {
    phase_id,
    external_reference_id,
    home_team_id,
    away_team_id,
    is_our_match,
    our_team_is_home,
    match_date,
    match_time,
    location,
    round_number,
    round_name,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
