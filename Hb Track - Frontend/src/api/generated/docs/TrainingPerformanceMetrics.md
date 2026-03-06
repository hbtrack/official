# TrainingPerformanceMetrics

Métricas agregadas de um treino (R22, RP6)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_athletes** | **number** | Total de atletas registrados | [default to undefined]
**presentes** | **number** | Atletas presentes | [default to undefined]
**ausentes** | **number** | Atletas ausentes (RP5: carga &#x3D; 0) | [default to undefined]
**dm** | **number** | Atletas em DM (dispensados médico) | [default to undefined]
**lesionadas** | **number** | Atletas lesionadas (R13) | [default to undefined]
**attendance_rate** | **number** | Taxa de presença (%) | [default to undefined]
**avg_minutes** | **number** |  | [optional] [default to undefined]
**avg_rpe** | **number** |  | [optional] [default to undefined]
**avg_internal_load** | **number** |  | [optional] [default to undefined]
**stddev_internal_load** | **number** |  | [optional] [default to undefined]
**load_ok_count** | **number** | Atletas com carga registrada | [default to undefined]
**data_completeness_pct** | **number** | % de dados completos | [default to undefined]
**avg_fatigue_after** | **number** |  | [optional] [default to undefined]
**avg_mood_after** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingPerformanceMetrics } from './api';

const instance: TrainingPerformanceMetrics = {
    total_athletes,
    presentes,
    ausentes,
    dm,
    lesionadas,
    attendance_rate,
    avg_minutes,
    avg_rpe,
    avg_internal_load,
    stddev_internal_load,
    load_ok_count,
    data_completeness_pct,
    avg_fatigue_after,
    avg_mood_after,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
