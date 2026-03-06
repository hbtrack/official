# WellnessPostData

Dados resumidos do wellness pós-treino para exibição no dashboard.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_rpe** | **number** | RPE da sessão (0-10) | [default to undefined]
**internal_load** | **number** |  | [optional] [default to undefined]
**fatigue_after** | **number** | Fadiga após treino (0-10) | [default to undefined]
**filled_at** | **string** | Data/hora do preenchimento | [default to undefined]

## Example

```typescript
import { WellnessPostData } from './api';

const instance: WellnessPostData = {
    session_rpe,
    internal_load,
    fatigue_after,
    filled_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
