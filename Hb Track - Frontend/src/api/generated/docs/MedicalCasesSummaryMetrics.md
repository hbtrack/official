# MedicalCasesSummaryMetrics

Métricas agregadas de casos médicos

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_cases** | **number** | Total de casos médicos | [default to undefined]
**active_cases** | **number** | Casos ativos | [default to undefined]
**resolved_cases** | **number** | Casos resolvidos | [default to undefined]
**top_reasons** | **{ [key: string]: number; }** | Razões mais comuns | [optional] [default to undefined]
**athletes_affected** | **number** | Atletas com casos ativos | [default to undefined]
**athletes_with_history** | **number** | Atletas com histórico médico | [default to undefined]
**avg_duration_days** | **number** |  | [optional] [default to undefined]
**median_duration_days** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { MedicalCasesSummaryMetrics } from './api';

const instance: MedicalCasesSummaryMetrics = {
    total_cases,
    active_cases,
    resolved_cases,
    top_reasons,
    athletes_affected,
    athletes_with_history,
    avg_duration_days,
    median_duration_days,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
