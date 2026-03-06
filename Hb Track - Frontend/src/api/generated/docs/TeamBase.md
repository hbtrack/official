# TeamBase

Response completo de equipe.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**organization_name** | **string** |  | [optional] [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**category_id** | **number** |  | [optional] [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**is_our_team** | **boolean** |  | [optional] [default to true]
**coach_membership_id** | **string** |  | [optional] [default to undefined]
**created_by_user_id** | **string** |  | [optional] [default to undefined]
**created_by_membership_id** | **string** |  | [optional] [default to undefined]
**alert_threshold_multiplier** | **number** |  | [optional] [default to 2.0]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamBase } from './api';

const instance: TeamBase = {
    id,
    organization_id,
    organization_name,
    season_id,
    name,
    category_id,
    gender,
    is_our_team,
    coach_membership_id,
    created_by_user_id,
    created_by_membership_id,
    alert_threshold_multiplier,
    created_at,
    updated_at,
    deleted_at,
    deleted_reason,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
