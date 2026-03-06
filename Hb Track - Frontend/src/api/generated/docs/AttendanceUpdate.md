# AttendanceUpdate

Payload para atualização de registro de presença.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**presence_status** | [**PresenceStatus**](PresenceStatus.md) |  | [optional] [default to undefined]
**minutes_effective** | **number** |  | [optional] [default to undefined]
**participation_type** | [**ParticipationType**](ParticipationType.md) |  | [optional] [default to undefined]
**reason_absence** | [**ReasonAbsence**](ReasonAbsence.md) |  | [optional] [default to undefined]
**comment** | **string** |  | [optional] [default to undefined]
**is_medical_restriction** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { AttendanceUpdate } from './api';

const instance: AttendanceUpdate = {
    presence_status,
    minutes_effective,
    participation_type,
    reason_absence,
    comment,
    is_medical_restriction,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
