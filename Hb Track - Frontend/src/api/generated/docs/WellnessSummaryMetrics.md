# WellnessSummaryMetrics

Métricas agregadas de bem-estar

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**avg_sleep_hours** | **number** |  | [optional] [default to undefined]
**avg_sleep_quality** | **number** |  | [optional] [default to undefined]
**avg_fatigue_pre** | **number** |  | [optional] [default to undefined]
**avg_stress** | **number** |  | [optional] [default to undefined]
**avg_muscle_soreness** | **number** |  | [optional] [default to undefined]
**avg_fatigue_after** | **number** |  | [optional] [default to undefined]
**avg_mood_after** | **number** |  | [optional] [default to undefined]
**athletes_high_fatigue** | **number** | Atletas com fadiga alta (&gt; 7) | [optional] [default to 0]
**athletes_poor_sleep** | **number** | Atletas com sono ruim (&lt; 6h ou qualidade &lt; 3) | [optional] [default to 0]
**athletes_high_stress** | **number** | Atletas com estresse alto (&gt; 7) | [optional] [default to 0]
**total_athletes** | **number** | Total de atletas | [default to undefined]
**athletes_with_wellness** | **number** | Atletas com dados de wellness | [default to undefined]
**data_completeness_pct** | **number** | % de dados completos | [default to undefined]

## Example

```typescript
import { WellnessSummaryMetrics } from './api';

const instance: WellnessSummaryMetrics = {
    avg_sleep_hours,
    avg_sleep_quality,
    avg_fatigue_pre,
    avg_stress,
    avg_muscle_soreness,
    avg_fatigue_after,
    avg_mood_after,
    athletes_high_fatigue,
    athletes_poor_sleep,
    athletes_high_stress,
    total_athletes,
    athletes_with_wellness,
    data_completeness_pct,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
