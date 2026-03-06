# MatchResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**season_id** | **string** |  | [default to undefined]
**team_id** | **string** |  | [default to undefined]
**match_date** | **string** |  | [default to undefined]
**opponent_name** | **string** |  | [default to undefined]
**match_type** | [**MatchType**](MatchType.md) |  | [default to undefined]
**is_home** | **boolean** |  | [default to undefined]
**location** | **string** |  | [default to undefined]
**status** | [**AppModelsMatchMatchStatus**](AppModelsMatchMatchStatus.md) |  | [default to undefined]
**finalized_at** | **string** |  | [optional] [default to undefined]
**validated_at** | **string** |  | [optional] [default to undefined]
**reopened_at** | **string** |  | [optional] [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**admin_note** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**is_finalized** | **boolean** | Se a partida está finalizada | [optional] [default to false]
**can_edit** | **boolean** | Se a partida pode ser editada | [optional] [default to true]

## Example

```typescript
import { MatchResponse } from './api';

const instance: MatchResponse = {
    id,
    organization_id,
    season_id,
    team_id,
    match_date,
    opponent_name,
    match_type,
    is_home,
    location,
    status,
    finalized_at,
    validated_at,
    reopened_at,
    deleted_at,
    deleted_reason,
    admin_note,
    created_at,
    updated_at,
    is_finalized,
    can_edit,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
