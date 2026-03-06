# ExerciseCreate

Schema para criação de exercício.  organization_id e created_by_user_id são obtidos do contexto.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**tag_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**category** | **string** |  | [optional] [default to undefined]
**media_url** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ExerciseCreate } from './api';

const instance: ExerciseCreate = {
    name,
    description,
    tag_ids,
    category,
    media_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
