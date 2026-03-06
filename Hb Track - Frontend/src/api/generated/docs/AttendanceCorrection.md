# AttendanceCorrection

Payload para correção administrativa de presença.  Correções são permitidas apenas para: - Coordenadores com permissão attendance:correction_write - Após fechamento da sessão (R37: ação administrativa auditada)  Campos correction_by_user_id e correction_at são preenchidos automaticamente.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**presence_status** | [**PresenceStatus**](PresenceStatus.md) |  | [optional] [default to undefined]
**minutes_effective** | **number** |  | [optional] [default to undefined]
**participation_type** | [**ParticipationType**](ParticipationType.md) |  | [optional] [default to undefined]
**reason_absence** | [**ReasonAbsence**](ReasonAbsence.md) |  | [optional] [default to undefined]
**comment** | **string** | Motivo da correção (obrigatório para auditoria) | [default to undefined]
**is_medical_restriction** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { AttendanceCorrection } from './api';

const instance: AttendanceCorrection = {
    presence_status,
    minutes_effective,
    participation_type,
    reason_absence,
    comment,
    is_medical_restriction,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
