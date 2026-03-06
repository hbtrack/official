# MatchEventCorrection

Schema para correção de evento com justificativa. Mantido para compatibilidade. Campos corrigidos para o enum canônico.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_type** | [**CanonicalEventType**](CanonicalEventType.md) |  | [optional] [default to undefined]
**period_number** | **number** |  | [optional] [default to undefined]
**game_time_seconds** | **number** |  | [optional] [default to undefined]
**correction_note** | **string** | Justificativa da correção (obrigatória) | [default to undefined]

## Example

```typescript
import { MatchEventCorrection } from './api';

const instance: MatchEventCorrection = {
    event_type,
    period_number,
    game_time_seconds,
    correction_note,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
