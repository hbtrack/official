# TeamSummaryResponse

Resposta GET /analytics/team/{teamId}/summary

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**period** | [**AnalyticsPeriod**](AnalyticsPeriod.md) |  | [default to undefined]
**metrics** | [**AnalyticsMetrics**](AnalyticsMetrics.md) |  | [default to undefined]
**calculated_at** | **string** | Timestamp UTC do cálculo | [default to undefined]

## Example

```typescript
import { TeamSummaryResponse } from './api';

const instance: TeamSummaryResponse = {
    team_id,
    period,
    metrics,
    calculated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
