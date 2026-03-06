# CompetitionOpponentTeamResponse

Schema de resposta para equipe adversária.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**competition_id** | **string** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**short_name** | **string** |  | [optional] [default to undefined]
**category** | **string** |  | [optional] [default to undefined]
**city** | **string** |  | [optional] [default to undefined]
**logo_url** | **string** |  | [optional] [default to undefined]
**linked_team_id** | **string** |  | [optional] [default to undefined]
**group_name** | **string** |  | [optional] [default to undefined]
**stats** | [**OpponentTeamStats**](OpponentTeamStats.md) |  | [optional] [default to undefined]
**status** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [optional] [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionOpponentTeamResponse } from './api';

const instance: CompetitionOpponentTeamResponse = {
    id,
    competition_id,
    name,
    short_name,
    category,
    city,
    logo_url,
    linked_team_id,
    group_name,
    stats,
    status,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
