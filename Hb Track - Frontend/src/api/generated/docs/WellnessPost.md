# WellnessPost

Resposta completa de wellness pós-treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** | ID do atleta | [default to undefined]
**organization_id** | **string** | ID da organização | [default to undefined]
**created_by_membership_id** | **string** |  | [optional] [default to undefined]
**session_rpe** | **number** |  | [optional] [default to undefined]
**minutes_effective** | **number** |  | [optional] [default to undefined]
**internal_load** | **number** |  | [optional] [default to undefined]
**fatigue_after** | **number** |  | [optional] [default to undefined]
**mood_after** | **number** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**id** | **string** | ID do registro de wellness pós-treino | [default to undefined]
**session_id** | **string** | ID da sessão de treino | [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]

## Example

```typescript
import { WellnessPost } from './api';

const instance: WellnessPost = {
    athlete_id,
    organization_id,
    created_by_membership_id,
    session_rpe,
    minutes_effective,
    internal_load,
    fatigue_after,
    mood_after,
    notes,
    id,
    session_id,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
