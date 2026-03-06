# MatchEventSummary

Schema resumido para listagens.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**athlete_id** | **string** |  | [default to undefined]
**event_type** | [**CanonicalEventType**](CanonicalEventType.md) |  | [default to undefined]
**period_number** | **number** |  | [default to undefined]
**game_time_seconds** | **number** |  | [default to undefined]

## Example

```typescript
import { MatchEventSummary } from './api';

const instance: MatchEventSummary = {
    id,
    athlete_id,
    event_type,
    period_number,
    game_time_seconds,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
