# TrainingSessionFinalizeRequest

Payload para finalização de revisão operacional (pending_review → readonly).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attendance_completed** | **boolean** | Confirma que presenças foram marcadas | [default to undefined]
**review_completed** | **boolean** | Confirma que revisão operacional foi concluída | [default to undefined]
**confirm** | **boolean** | Confirmação de fechamento | [optional] [default to true]

## Example

```typescript
import { TrainingSessionFinalizeRequest } from './api';

const instance: TrainingSessionFinalizeRequest = {
    attendance_completed,
    review_completed,
    confirm,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
