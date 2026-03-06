# SessionExerciseCreate

Schema para criar vínculo exercise → session. Usado ao arrastar exercício do banco para a sessão.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_index** | **number** | Ordem do exercício na sessão (0-based) | [default to undefined]
**duration_minutes** | **number** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**exercise_id** | **string** | UUID do exercício a adicionar | [default to undefined]

## Example

```typescript
import { SessionExerciseCreate } from './api';

const instance: SessionExerciseCreate = {
    order_index,
    duration_minutes,
    notes,
    exercise_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
