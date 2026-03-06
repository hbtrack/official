# SessionExerciseResponse

Schema de resposta completo com dados do exercício aninhados. Inclui timestamps e dados do exercício relacionado.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_index** | **number** | Ordem do exercício na sessão (0-based) | [default to undefined]
**duration_minutes** | **number** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**id** | **string** |  | [default to undefined]
**session_id** | **string** |  | [default to undefined]
**exercise_id** | **string** |  | [default to undefined]
**exercise** | [**ExerciseNested**](ExerciseNested.md) | Dados completos do exercício | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { SessionExerciseResponse } from './api';

const instance: SessionExerciseResponse = {
    order_index,
    duration_minutes,
    notes,
    id,
    session_id,
    exercise_id,
    exercise,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
