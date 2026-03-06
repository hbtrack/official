# DashboardTrainingStats

Estatísticas agregadas de treinos

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_sessions** | **number** | Total de sessões no período | [optional] [default to 0]
**avg_attendance_rate** | **number** | Taxa média de presença (%) | [optional] [default to 0.0]
**avg_internal_load** | **number** | Carga interna média | [optional] [default to 0.0]
**recent_sessions** | [**Array&lt;DashboardTrainingSession&gt;**](DashboardTrainingSession.md) | Últimas sessões de treino | [optional] [default to undefined]

## Example

```typescript
import { DashboardTrainingStats } from './api';

const instance: DashboardTrainingStats = {
    total_sessions,
    avg_attendance_rate,
    avg_internal_load,
    recent_sessions,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
