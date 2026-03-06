# SuggestionStatsResponse

Schema de resposta de estatísticas de sugestões.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total** | **number** | Total de sugestões | [default to undefined]
**pending** | **number** | Sugestões pendentes | [default to undefined]
**applied** | **number** | Sugestões aplicadas | [default to undefined]
**dismissed** | **number** | Sugestões dismissadas | [default to undefined]
**acceptance_rate** | **number** | Taxa de aceitação (%) | [default to undefined]
**by_type** | **{ [key: string]: number; }** | Contagem por tipo | [optional] [default to undefined]
**recent_suggestions** | [**Array&lt;SuggestionResponse&gt;**](SuggestionResponse.md) | 5 sugestões mais recentes | [optional] [default to undefined]

## Example

```typescript
import { SuggestionStatsResponse } from './api';

const instance: SuggestionStatsResponse = {
    total,
    pending,
    applied,
    dismissed,
    acceptance_rate,
    by_type,
    recent_suggestions,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
