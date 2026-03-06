# SessionExerciseUpdate

Schema para atualizar metadados de um exercício já adicionado. Permite editar apenas order_index, duration_minutes e notes.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_index** | **number** |  | [optional] [default to undefined]
**duration_minutes** | **number** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { SessionExerciseUpdate } from './api';

const instance: SessionExerciseUpdate = {
    order_index,
    duration_minutes,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
