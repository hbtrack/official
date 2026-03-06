# DashboardMedicalStats

Estatísticas médicas

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active_cases** | **number** | Casos médicos ativos | [optional] [default to 0]
**recovering** | **number** | Atletas em recuperação | [optional] [default to 0]
**cleared_this_week** | **number** | Liberados esta semana | [optional] [default to 0]
**avg_days_out** | **number** | Média de dias fora por lesão | [optional] [default to 0.0]

## Example

```typescript
import { DashboardMedicalStats } from './api';

const instance: DashboardMedicalStats = {
    active_cases,
    recovering,
    cleared_this_week,
    avg_days_out,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
