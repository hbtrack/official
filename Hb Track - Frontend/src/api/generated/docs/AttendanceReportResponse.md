# AttendanceReportResponse

Resposta do relatório de assiduidade.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**team_name** | **string** |  | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**season_name** | **string** |  | [optional] [default to undefined]
**period_start** | **string** |  | [optional] [default to undefined]
**period_end** | **string** |  | [optional] [default to undefined]
**total_training_sessions** | **number** |  | [default to undefined]
**total_matches** | **number** |  | [default to undefined]
**athletes** | [**Array&lt;AthleteAttendanceRecord&gt;**](AthleteAttendanceRecord.md) |  | [default to undefined]
**pagination** | [**PaginationMeta**](PaginationMeta.md) |  | [optional] [default to undefined]

## Example

```typescript
import { AttendanceReportResponse } from './api';

const instance: AttendanceReportResponse = {
    team_id,
    team_name,
    season_id,
    season_name,
    period_start,
    period_end,
    total_training_sessions,
    total_matches,
    athletes,
    pagination,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
