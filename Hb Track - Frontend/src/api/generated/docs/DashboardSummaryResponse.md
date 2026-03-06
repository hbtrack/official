# DashboardSummaryResponse

Resposta completa do dashboard em uma única requisição.  Cache: TTL 60-120s por team_id + season_id

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [optional] [default to undefined]
**team_name** | **string** |  | [optional] [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**season_name** | **string** |  | [optional] [default to undefined]
**generated_at** | **string** |  | [optional] [default to undefined]
**cache_ttl_seconds** | **number** |  | [optional] [default to 120]
**athletes** | [**DashboardAthleteStats**](DashboardAthleteStats.md) |  | [default to undefined]
**training** | [**DashboardTrainingStats**](DashboardTrainingStats.md) |  | [default to undefined]
**training_trends** | [**Array&lt;DashboardTrainingTrend&gt;**](DashboardTrainingTrend.md) |  | [optional] [default to undefined]
**matches** | [**DashboardMatchStats**](DashboardMatchStats.md) |  | [default to undefined]
**wellness** | [**DashboardWellnessStats**](DashboardWellnessStats.md) |  | [default to undefined]
**medical** | [**DashboardMedicalStats**](DashboardMedicalStats.md) |  | [default to undefined]
**alerts** | [**Array&lt;DashboardAlert&gt;**](DashboardAlert.md) |  | [optional] [default to undefined]
**next_training** | [**DashboardNextTraining**](DashboardNextTraining.md) |  | [optional] [default to undefined]
**next_match** | [**DashboardNextMatch**](DashboardNextMatch.md) |  | [optional] [default to undefined]

## Example

```typescript
import { DashboardSummaryResponse } from './api';

const instance: DashboardSummaryResponse = {
    team_id,
    team_name,
    season_id,
    season_name,
    generated_at,
    cache_ttl_seconds,
    athletes,
    training,
    training_trends,
    matches,
    wellness,
    medical,
    alerts,
    next_training,
    next_match,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
