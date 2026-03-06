# DashboardWellnessStats

Médias de wellness da equipe

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**avg_sleep_quality** | **number** |  | [optional] [default to 0.0]
**avg_fatigue** | **number** |  | [optional] [default to 0.0]
**avg_stress** | **number** |  | [optional] [default to 0.0]
**avg_mood** | **number** |  | [optional] [default to 0.0]
**avg_soreness** | **number** |  | [optional] [default to 0.0]
**readiness_score** | **number** | Score de prontidão 0-100 | [optional] [default to 0.0]
**athletes_reported** | **number** | Atletas que reportaram hoje | [optional] [default to 0]
**athletes_at_risk** | **number** | Atletas com indicadores preocupantes | [optional] [default to 0]

## Example

```typescript
import { DashboardWellnessStats } from './api';

const instance: DashboardWellnessStats = {
    avg_sleep_quality,
    avg_fatigue,
    avg_stress,
    avg_mood,
    avg_soreness,
    readiness_score,
    athletes_reported,
    athletes_at_risk,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
