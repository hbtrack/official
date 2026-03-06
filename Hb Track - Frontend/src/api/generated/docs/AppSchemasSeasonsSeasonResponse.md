# AppSchemasSeasonsSeasonResponse

Response completo de temporada. Inclui status derivado (6.1.1).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**team_id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**year** | **number** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**competition_type** | **string** |  | [optional] [default to undefined]
**start_date** | **string** |  | [default to undefined]
**end_date** | **string** |  | [default to undefined]
**is_active** | **boolean** |  | [optional] [default to false]
**status** | [**SeasonStatus**](SeasonStatus.md) | Status derivado (6.1.1) | [default to undefined]
**canceled_at** | **string** |  | [optional] [default to undefined]
**interrupted_at** | **string** |  | [optional] [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_by_user_id** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { AppSchemasSeasonsSeasonResponse } from './api';

const instance: AppSchemasSeasonsSeasonResponse = {
    id,
    team_id,
    organization_id,
    year,
    name,
    competition_type,
    start_date,
    end_date,
    is_active,
    status,
    canceled_at,
    interrupted_at,
    deleted_at,
    deleted_reason,
    created_by_user_id,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
