# AlertListResponse

Schema de resposta paginada de alertas.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;AlertResponse&gt;**](AlertResponse.md) |  | [default to undefined]
**total** | **number** | Total de alertas | [default to undefined]
**page** | **number** | Página atual | [default to undefined]
**limit** | **number** | Items por página | [default to undefined]
**has_next** | **boolean** | Tem próxima página | [default to undefined]

## Example

```typescript
import { AlertListResponse } from './api';

const instance: AlertListResponse = {
    items,
    total,
    page,
    limit,
    has_next,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
