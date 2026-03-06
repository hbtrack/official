# TrainingPerformanceTrend

Tendências de performance ao longo do tempo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period** | **string** | Período (week, month) | [default to undefined]
**period_start** | **string** |  | [default to undefined]
**period_end** | **string** |  | [default to undefined]
**sessions_count** | **number** |  | [default to undefined]
**avg_attendance_rate** | **number** |  | [default to undefined]
**avg_internal_load** | **number** |  | [optional] [default to undefined]
**avg_fatigue** | **number** |  | [optional] [default to undefined]
**avg_mood** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingPerformanceTrend } from './api';

const instance: TrainingPerformanceTrend = {
    period,
    period_start,
    period_end,
    sessions_count,
    avg_attendance_rate,
    avg_internal_load,
    avg_fatigue,
    avg_mood,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
