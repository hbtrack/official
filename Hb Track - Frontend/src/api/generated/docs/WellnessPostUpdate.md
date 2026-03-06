# WellnessPostUpdate

Payload para atualização de wellness pós-treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_rpe** | **number** |  | [optional] [default to undefined]
**minutes_effective** | **number** |  | [optional] [default to undefined]
**internal_load** | **number** |  | [optional] [default to undefined]
**fatigue_after** | **number** |  | [optional] [default to undefined]
**mood_after** | **number** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { WellnessPostUpdate } from './api';

const instance: WellnessPostUpdate = {
    session_rpe,
    minutes_effective,
    internal_load,
    fatigue_after,
    mood_after,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
