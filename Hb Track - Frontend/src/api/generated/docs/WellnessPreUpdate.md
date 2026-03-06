# WellnessPreUpdate

Payload para atualização de wellness pré-treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sleep_hours** | **number** |  | [optional] [default to undefined]
**sleep_quality** | **number** |  | [optional] [default to undefined]
**fatigue** | **number** |  | [optional] [default to undefined]
**stress** | **number** |  | [optional] [default to undefined]
**muscle_soreness** | **number** |  | [optional] [default to undefined]
**pain** | **boolean** |  | [optional] [default to undefined]
**pain_level** | **number** |  | [optional] [default to undefined]
**pain_location** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { WellnessPreUpdate } from './api';

const instance: WellnessPreUpdate = {
    sleep_hours,
    sleep_quality,
    fatigue,
    stress,
    muscle_soreness,
    pain,
    pain_level,
    pain_location,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
