# WeeklyLoadItem

Item de carga semanal.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**week_start** | **string** | Início da semana (ISO) | [default to undefined]
**week_end** | **string** | Fim da semana (ISO) | [default to undefined]
**microcycle_id** | **string** | UUID do microciclo | [default to undefined]
**total_sessions** | **number** |  | [default to undefined]
**total_internal_load** | **number** |  | [default to undefined]
**avg_rpe** | **number** |  | [default to undefined]
**attendance_rate** | **number** |  | [default to undefined]

## Example

```typescript
import { WeeklyLoadItem } from './api';

const instance: WeeklyLoadItem = {
    week_start,
    week_end,
    microcycle_id,
    total_sessions,
    total_internal_load,
    avg_rpe,
    attendance_rate,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
