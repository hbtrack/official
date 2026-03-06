# AttendanceCreate

Payload para criação de registro de presença. Campos derivados automaticamente: training_session_id (path), team_registration_id (lookup)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** | ID do atleta | [default to undefined]
**team_registration_id** | **string** |  | [optional] [default to undefined]
**presence_status** | [**PresenceStatus**](PresenceStatus.md) | Status: \&#39;present\&#39; ou \&#39;absent\&#39; | [optional] [default to undefined]
**minutes_effective** | **number** |  | [optional] [default to undefined]
**participation_type** | [**ParticipationType**](ParticipationType.md) |  | [optional] [default to undefined]
**reason_absence** | [**ReasonAbsence**](ReasonAbsence.md) |  | [optional] [default to undefined]
**comment** | **string** |  | [optional] [default to undefined]
**is_medical_restriction** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { AttendanceCreate } from './api';

const instance: AttendanceCreate = {
    athlete_id,
    team_registration_id,
    presence_status,
    minutes_effective,
    participation_type,
    reason_absence,
    comment,
    is_medical_restriction,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
