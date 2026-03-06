# Attendance

Resposta completa de registro de presença.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID do registro | [default to undefined]
**training_session_id** | **string** | ID da sessão de treino | [default to undefined]
**team_registration_id** | **string** | ID do team_registration | [default to undefined]
**athlete_id** | **string** | ID do atleta | [default to undefined]
**presence_status** | **string** | Status de presença | [default to undefined]
**minutes_effective** | **number** |  | [optional] [default to undefined]
**comment** | **string** |  | [optional] [default to undefined]
**source** | **string** | Fonte do registro | [optional] [default to 'manual']
**participation_type** | **string** |  | [optional] [default to undefined]
**reason_absence** | **string** |  | [optional] [default to undefined]
**is_medical_restriction** | **boolean** |  | [optional] [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**created_by_user_id** | **string** | Usuário que criou | [default to undefined]
**updated_at** | **string** | Data/hora de atualização | [default to undefined]
**correction_by_user_id** | **string** |  | [optional] [default to undefined]
**correction_at** | **string** |  | [optional] [default to undefined]
**athlete** | [**AppSchemasAttendanceAthleteNested**](AppSchemasAttendanceAthleteNested.md) |  | [optional] [default to undefined]

## Example

```typescript
import { Attendance } from './api';

const instance: Attendance = {
    id,
    training_session_id,
    team_registration_id,
    athlete_id,
    presence_status,
    minutes_effective,
    comment,
    source,
    participation_type,
    reason_absence,
    is_medical_restriction,
    created_at,
    created_by_user_id,
    updated_at,
    correction_by_user_id,
    correction_at,
    athlete,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
