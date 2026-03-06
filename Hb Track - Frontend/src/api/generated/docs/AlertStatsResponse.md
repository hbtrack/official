# AlertStatsResponse

Schema de resposta de estatísticas de alertas.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total** | **number** | Total de alertas | [default to undefined]
**active** | **number** | Alertas ativos | [default to undefined]
**dismissed** | **number** | Alertas dismissados | [default to undefined]
**critical_count** | **number** | Alertas críticos ativos | [default to undefined]
**warning_count** | **number** | Alertas de warning ativos | [default to undefined]
**by_type** | **{ [key: string]: number; }** | Contagem por tipo | [optional] [default to undefined]
**recent_alerts** | [**Array&lt;AlertResponse&gt;**](AlertResponse.md) | 5 alertas mais recentes | [optional] [default to undefined]

## Example

```typescript
import { AlertStatsResponse } from './api';

const instance: AlertStatsResponse = {
    total,
    active,
    dismissed,
    critical_count,
    warning_count,
    by_type,
    recent_alerts,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
