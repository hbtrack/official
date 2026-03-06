# ExerciseResponse

Schema de resposta com todos os campos do exercício.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**tag_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**category** | **string** |  | [optional] [default to undefined]
**media_url** | **string** |  | [optional] [default to undefined]
**id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**created_by_user_id** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { ExerciseResponse } from './api';

const instance: ExerciseResponse = {
    name,
    description,
    tag_ids,
    category,
    media_url,
    id,
    organization_id,
    created_by_user_id,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
