# DeviationItem

Item de desvio detectado.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **string** |  | [default to undefined]
**session_at** | **string** | Data da sessão (ISO) | [default to undefined]
**planned_rpe** | **number** |  | [default to undefined]
**actual_rpe** | **number** |  | [default to undefined]
**deviation** | **number** | Desvio calculado com threshold | [default to undefined]
**exceeded_threshold** | **boolean** |  | [default to undefined]

## Example

```typescript
import { DeviationItem } from './api';

const instance: DeviationItem = {
    session_id,
    session_at,
    planned_rpe,
    actual_rpe,
    deviation,
    exceeded_threshold,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
