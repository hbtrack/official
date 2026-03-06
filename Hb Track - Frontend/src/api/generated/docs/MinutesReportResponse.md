# MinutesReportResponse

Resposta do relatório de minutos.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**team_name** | **string** |  | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**season_name** | **string** |  | [optional] [default to undefined]
**period_start** | **string** |  | [optional] [default to undefined]
**period_end** | **string** |  | [optional] [default to undefined]
**athletes** | [**Array&lt;AthleteMinutesRecord&gt;**](AthleteMinutesRecord.md) |  | [default to undefined]
**pagination** | [**PaginationMeta**](PaginationMeta.md) |  | [optional] [default to undefined]

## Example

```typescript
import { MinutesReportResponse } from './api';

const instance: MinutesReportResponse = {
    team_id,
    team_name,
    season_id,
    season_name,
    period_start,
    period_end,
    athletes,
    pagination,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
