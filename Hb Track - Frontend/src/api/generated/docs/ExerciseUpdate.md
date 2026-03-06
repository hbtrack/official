# ExerciseUpdate

Schema para atualização de exercício.  Todos os campos são opcionais.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**tag_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**category** | **string** |  | [optional] [default to undefined]
**media_url** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ExerciseUpdate } from './api';

const instance: ExerciseUpdate = {
    name,
    description,
    tag_ids,
    category,
    media_url,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
