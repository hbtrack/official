# AlertResponse

Schema de resposta de alerta.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **number** |  | [default to undefined]
**team_id** | **number** |  | [default to undefined]
**alert_type** | **string** |  | [default to undefined]
**severity** | **string** |  | [default to undefined]
**message** | **string** |  | [default to undefined]
**alert_metadata** | **{ [key: string]: any; }** |  | [default to undefined]
**triggered_at** | **string** |  | [default to undefined]
**dismissed_at** | **string** |  | [default to undefined]
**dismissed_by_user_id** | **number** |  | [default to undefined]
**is_active** | **boolean** |  | [default to undefined]
**is_dismissed** | **boolean** |  | [default to undefined]
**is_critical** | **boolean** |  | [default to undefined]

## Example

```typescript
import { AlertResponse } from './api';

const instance: AlertResponse = {
    id,
    team_id,
    alert_type,
    severity,
    message,
    alert_metadata,
    triggered_at,
    dismissed_at,
    dismissed_by_user_id,
    is_active,
    is_dismissed,
    is_critical,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
