# ExerciseListResponse

Schema de resposta paginada para listagem de exercícios.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exercises** | [**Array&lt;ExerciseResponse&gt;**](ExerciseResponse.md) |  | [default to undefined]
**total** | **number** |  | [default to undefined]
**page** | **number** |  | [default to undefined]
**per_page** | **number** |  | [default to undefined]

## Example

```typescript
import { ExerciseListResponse } from './api';

const instance: ExerciseListResponse = {
    exercises,
    total,
    page,
    per_page,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
