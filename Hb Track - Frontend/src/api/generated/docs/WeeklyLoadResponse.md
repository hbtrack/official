# WeeklyLoadResponse

Resposta GET /analytics/team/{teamId}/weekly-load

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**weeks** | **number** | Quantidade de semanas analisadas | [default to undefined]
**data** | [**Array&lt;WeeklyLoadItem&gt;**](WeeklyLoadItem.md) |  | [default to undefined]

## Example

```typescript
import { WeeklyLoadResponse } from './api';

const instance: WeeklyLoadResponse = {
    team_id,
    weeks,
    data,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
