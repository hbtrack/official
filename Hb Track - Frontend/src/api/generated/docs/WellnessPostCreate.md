# WellnessPostCreate

Payload para criação de wellness pós-treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** | ID do atleta | [default to undefined]
**organization_id** | **string** | ID da organização | [default to undefined]
**created_by_membership_id** | **string** | ID do membership que criou | [default to undefined]
**session_rpe** | **number** |  | [optional] [default to undefined]
**minutes_effective** | **number** |  | [optional] [default to undefined]
**internal_load** | **number** |  | [optional] [default to undefined]
**fatigue_after** | **number** |  | [optional] [default to undefined]
**mood_after** | **number** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { WellnessPostCreate } from './api';

const instance: WellnessPostCreate = {
    athlete_id,
    organization_id,
    created_by_membership_id,
    session_rpe,
    minutes_effective,
    internal_load,
    fatigue_after,
    mood_after,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
