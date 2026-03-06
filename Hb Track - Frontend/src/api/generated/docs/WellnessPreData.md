# WellnessPreData

Dados resumidos do wellness pré-treino para exibição no dashboard.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fatigue_level** | **number** | Nível de fadiga (0-10) | [default to undefined]
**stress_level** | **number** | Nível de estresse (0-10) | [default to undefined]
**readiness** | **number** |  | [optional] [default to undefined]
**filled_at** | **string** | Data/hora do preenchimento | [default to undefined]

## Example

```typescript
import { WellnessPreData } from './api';

const instance: WellnessPreData = {
    fatigue_level,
    stress_level,
    readiness,
    filled_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
