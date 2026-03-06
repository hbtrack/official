# WellnessPre

Resposta completa de wellness pré-treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** | ID do atleta | [default to undefined]
**organization_id** | **string** | ID da organização | [default to undefined]
**created_by_membership_id** | **string** |  | [optional] [default to undefined]
**sleep_hours** | **number** |  | [optional] [default to undefined]
**sleep_quality** | **number** |  | [optional] [default to undefined]
**fatigue** | **number** |  | [optional] [default to undefined]
**stress** | **number** |  | [optional] [default to undefined]
**muscle_soreness** | **number** |  | [optional] [default to undefined]
**pain** | **boolean** | Indica presença de dor | [optional] [default to false]
**pain_level** | **number** |  | [optional] [default to undefined]
**pain_location** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**id** | **string** | ID do registro de wellness pré-treino | [default to undefined]
**session_id** | **string** | ID da sessão de treino | [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]

## Example

```typescript
import { WellnessPre } from './api';

const instance: WellnessPre = {
    athlete_id,
    organization_id,
    created_by_membership_id,
    sleep_hours,
    sleep_quality,
    fatigue,
    stress,
    muscle_soreness,
    pain,
    pain_level,
    pain_location,
    notes,
    id,
    session_id,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
