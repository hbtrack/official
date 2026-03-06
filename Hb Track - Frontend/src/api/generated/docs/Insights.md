# Insights

Insights interpretativos gerados pelo backend.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**works** | **Array&lt;string&gt;** | O que está funcionando (foco alto + eficiência alta) | [optional] [default to undefined]
**adjust** | **Array&lt;string&gt;** | O que precisa ajustar (foco médio ou eficiência média) | [optional] [default to undefined]
**avoid** | **Array&lt;string&gt;** | O que não está funcionando (foco baixo + eficiência baixa) | [optional] [default to undefined]

## Example

```typescript
import { Insights } from './api';

const instance: Insights = {
    works,
    adjust,
    avoid,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
