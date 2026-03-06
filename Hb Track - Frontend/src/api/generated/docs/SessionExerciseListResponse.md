# SessionExerciseListResponse

Response para listagem de exercícios de uma sessão

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **string** |  | [default to undefined]
**total_exercises** | **number** | Total de exercícios na sessão | [default to undefined]
**total_duration_minutes** | **number** |  | [optional] [default to undefined]
**exercises** | [**Array&lt;SessionExerciseResponse&gt;**](SessionExerciseResponse.md) | Lista ordenada por order_index | [default to undefined]

## Example

```typescript
import { SessionExerciseListResponse } from './api';

const instance: SessionExerciseListResponse = {
    session_id,
    total_exercises,
    total_duration_minutes,
    exercises,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
