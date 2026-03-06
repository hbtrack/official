# MatchEventUpdate

Schema para atualização de evento. Mantido para compatibilidade. Campos corrigidos para o enum canônico.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_type** | [**CanonicalEventType**](CanonicalEventType.md) |  | [optional] [default to undefined]
**period_number** | **number** |  | [optional] [default to undefined]
**game_time_seconds** | **number** |  | [optional] [default to undefined]
**x_coord** | **number** |  | [optional] [default to undefined]
**y_coord** | **number** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**outcome** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { MatchEventUpdate } from './api';

const instance: MatchEventUpdate = {
    event_type,
    period_number,
    game_time_seconds,
    x_coord,
    y_coord,
    notes,
    outcome,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
