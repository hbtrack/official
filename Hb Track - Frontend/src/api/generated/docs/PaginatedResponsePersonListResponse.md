# PaginatedResponsePersonListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;PersonListResponse&gt;**](PersonListResponse.md) | Lista de itens da página atual | [default to undefined]
**total** | **number** | Total de itens (sem paginação) | [default to undefined]
**skip** | **number** | Número de itens pulados | [optional] [default to 0]
**limit** | **number** | Limite de itens por página | [optional] [default to 100]

## Example

```typescript
import { PaginatedResponsePersonListResponse } from './api';

const instance: PaginatedResponsePersonListResponse = {
    items,
    total,
    skip,
    limit,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
