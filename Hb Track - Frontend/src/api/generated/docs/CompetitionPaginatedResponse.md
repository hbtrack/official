# CompetitionPaginatedResponse

Resposta paginada para listagem de competições.  Envelope padrão: {items, page, limit, total}

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;Competition&gt;**](Competition.md) | Lista de competições na página atual | [default to undefined]
**page** | **number** | Página atual | [default to undefined]
**limit** | **number** | Itens por página | [default to undefined]
**total** | **number** | Total de itens (todas as páginas) | [default to undefined]

## Example

```typescript
import { CompetitionPaginatedResponse } from './api';

const instance: CompetitionPaginatedResponse = {
    items,
    page,
    limit,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
