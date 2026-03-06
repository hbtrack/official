# SessionSummaryResponse

Resumo de sessão para treinador/atleta.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **string** |  | [default to undefined]
**session_status** | **string** |  | [default to undefined]
**rating_avg** | **number** |  | [optional] [default to undefined]
**feedback_count** | **number** |  | [optional] [default to 0]
**note** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { SessionSummaryResponse } from './api';

const instance: SessionSummaryResponse = {
    session_id,
    session_status,
    rating_avg,
    feedback_count,
    note,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
