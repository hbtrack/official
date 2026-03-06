# DeviationAnalysisResponse

Resposta GET /analytics/team/{teamId}/deviation-analysis

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**threshold_multiplier** | **number** | Multiplicador configurado na equipe | [default to undefined]
**period** | [**AnalyticsPeriod**](AnalyticsPeriod.md) |  | [default to undefined]
**total_sessions** | **number** |  | [default to undefined]
**deviation_count** | **number** | Sessões que excederam threshold | [default to undefined]
**deviations** | [**Array&lt;DeviationItem&gt;**](DeviationItem.md) |  | [default to undefined]

## Example

```typescript
import { DeviationAnalysisResponse } from './api';

const instance: DeviationAnalysisResponse = {
    team_id,
    threshold_multiplier,
    period,
    total_sessions,
    deviation_count,
    deviations,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
