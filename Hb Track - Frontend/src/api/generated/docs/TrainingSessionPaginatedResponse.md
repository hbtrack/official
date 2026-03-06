# TrainingSessionPaginatedResponse

Resposta paginada de sessões de treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;TrainingSession&gt;**](TrainingSession.md) | Lista de sessões de treino | [default to undefined]
**page** | **number** | Número da página atual | [default to undefined]
**limit** | **number** | Itens por página | [default to undefined]
**total** | **number** | Total de itens | [default to undefined]

## Example

```typescript
import { TrainingSessionPaginatedResponse } from './api';

const instance: TrainingSessionPaginatedResponse = {
    items,
    page,
    limit,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
