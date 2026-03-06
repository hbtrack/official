# SuggestionResponse

Schema de resposta de sugestão.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **number** |  | [default to undefined]
**team_id** | **number** |  | [default to undefined]
**type** | **string** |  | [default to undefined]
**origin_session_id** | **number** |  | [default to undefined]
**target_session_ids** | **Array&lt;number&gt;** |  | [default to undefined]
**recommended_adjustment_pct** | **number** |  | [default to undefined]
**reason** | **string** |  | [default to undefined]
**status** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**applied_at** | **string** |  | [default to undefined]
**dismissed_at** | **string** |  | [default to undefined]
**dismissal_reason** | **string** |  | [default to undefined]
**is_pending** | **boolean** |  | [default to undefined]
**is_applied** | **boolean** |  | [default to undefined]
**is_dismissed** | **boolean** |  | [default to undefined]
**target_count** | **number** |  | [default to undefined]

## Example

```typescript
import { SuggestionResponse } from './api';

const instance: SuggestionResponse = {
    id,
    team_id,
    type,
    origin_session_id,
    target_session_ids,
    recommended_adjustment_pct,
    reason,
    status,
    created_at,
    applied_at,
    dismissed_at,
    dismissal_reason,
    is_pending,
    is_applied,
    is_dismissed,
    target_count,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
