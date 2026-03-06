# WellnessSessionStats

Estatísticas agregadas de wellness da sessão.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_athletes** | **number** | Total de atletas presentes | [default to undefined]
**responded_pre** | **number** | Responderam wellness pré | [default to undefined]
**responded_post** | **number** | Responderam wellness pós | [default to undefined]
**response_rate_pre** | **number** | Taxa de resposta pré (%) | [default to undefined]
**response_rate_post** | **number** | Taxa de resposta pós (%) | [default to undefined]
**avg_fatigue_pre** | **number** | Média fadiga pré | [optional] [default to 0.0]
**avg_stress_pre** | **number** | Média stress pré | [optional] [default to 0.0]
**avg_readiness_pre** | **number** | Média prontidão pré | [optional] [default to 0.0]
**avg_rpe_post** | **number** | Média RPE pós | [optional] [default to 0.0]
**avg_internal_load_post** | **number** | Média carga interna pós | [optional] [default to 0.0]
**has_high_fatigue_alert** | **boolean** | Alerta fadiga alta (≥7) | [optional] [default to false]
**has_high_stress_alert** | **boolean** | Alerta stress alto (≥7) | [optional] [default to false]
**has_low_readiness_alert** | **boolean** | Alerta prontidão baixa (≤4) | [optional] [default to false]
**has_high_rpe_alert** | **boolean** | Alerta RPE alto (≥8) | [optional] [default to false]

## Example

```typescript
import { WellnessSessionStats } from './api';

const instance: WellnessSessionStats = {
    total_athletes,
    responded_pre,
    responded_post,
    response_rate_pre,
    response_rate_post,
    avg_fatigue_pre,
    avg_stress_pre,
    avg_readiness_pre,
    avg_rpe_post,
    avg_internal_load_post,
    has_high_fatigue_alert,
    has_high_stress_alert,
    has_low_readiness_alert,
    has_high_rpe_alert,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
