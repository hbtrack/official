# LoadReportResponse

Resposta do relatório de carga.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**team_name** | **string** |  | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**season_name** | **string** |  | [optional] [default to undefined]
**period_start** | **string** |  | [default to undefined]
**period_end** | **string** |  | [default to undefined]
**period_days** | **number** |  | [default to undefined]
**load_threshold_daily** | **number** | Limiar de carga diária para alerta | [optional] [default to 500]
**load_threshold_weekly** | **number** | Limiar de carga semanal para alerta | [optional] [default to 3000]
**team_avg_load** | **number** |  | [default to undefined]
**team_total_load** | **number** |  | [default to undefined]
**athletes_overloaded_count** | **number** |  | [default to undefined]
**athletes** | [**Array&lt;AthleteLoadRecord&gt;**](AthleteLoadRecord.md) |  | [default to undefined]
**pagination** | [**PaginationMeta**](PaginationMeta.md) |  | [optional] [default to undefined]

## Example

```typescript
import { LoadReportResponse } from './api';

const instance: LoadReportResponse = {
    team_id,
    team_name,
    season_id,
    season_name,
    period_start,
    period_end,
    period_days,
    load_threshold_daily,
    load_threshold_weekly,
    team_avg_load,
    team_total_load,
    athletes_overloaded_count,
    athletes,
    pagination,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
