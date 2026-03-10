# TrainingSessionScheduleRequest

Payload para agendamento de sessão (draft → scheduled).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**starts_at** | **string** | Data/hora de início da sessão | [default to undefined]
**ends_at** | **string** | Data/hora de término da sessão | [default to undefined]

## Example

```typescript
import { TrainingSessionScheduleRequest } from './api';

const instance: TrainingSessionScheduleRequest = {
    starts_at,
    ends_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
