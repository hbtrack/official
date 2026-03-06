# SeasonPaginatedResponse

Response paginado para listagem de temporadas.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;AppSchemasSeasonsSeasonResponse&gt;**](AppSchemasSeasonsSeasonResponse.md) |  | [default to undefined]
**page** | **number** | Página atual | [default to undefined]
**limit** | **number** | Itens por página | [default to undefined]
**total** | **number** | Total de itens | [default to undefined]

## Example

```typescript
import { SeasonPaginatedResponse } from './api';

const instance: SeasonPaginatedResponse = {
    items,
    page,
    limit,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
