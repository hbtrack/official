# OrganizationPaginatedResponse

Resposta paginada de organizações.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;Organization&gt;**](Organization.md) | Lista de organizações | [default to undefined]
**page** | **number** | Página atual | [default to undefined]
**limit** | **number** | Itens por página | [default to undefined]
**total** | **number** | Total de itens | [default to undefined]

## Example

```typescript
import { OrganizationPaginatedResponse } from './api';

const instance: OrganizationPaginatedResponse = {
    items,
    page,
    limit,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
