# SuggestionListResponse

Schema de resposta paginada de sugestões.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**Array&lt;SuggestionResponse&gt;**](SuggestionResponse.md) |  | [default to undefined]
**total** | **number** | Total de sugestões | [default to undefined]
**page** | **number** | Página atual | [default to undefined]
**limit** | **number** | Items por página | [default to undefined]
**has_next** | **boolean** | Tem próxima página | [default to undefined]

## Example

```typescript
import { SuggestionListResponse } from './api';

const instance: SuggestionListResponse = {
    items,
    total,
    page,
    limit,
    has_next,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
