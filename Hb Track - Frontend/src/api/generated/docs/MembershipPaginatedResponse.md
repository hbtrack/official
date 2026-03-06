# MembershipPaginatedResponse

Resposta paginada de vínculos.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;Membership&gt;**](Membership.md) | Lista de vínculos | [default to undefined]
**page** | **number** | Página atual | [default to undefined]
**limit** | **number** | Itens por página | [default to undefined]
**total** | **number** | Total de itens | [default to undefined]

## Example

```typescript
import { MembershipPaginatedResponse } from './api';

const instance: MembershipPaginatedResponse = {
    items,
    page,
    limit,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
