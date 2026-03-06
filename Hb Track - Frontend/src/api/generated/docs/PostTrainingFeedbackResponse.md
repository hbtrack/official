# PostTrainingFeedbackResponse

Resposta ao registrar feedback.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **string** |  | [default to undefined]
**athlete_id** | **string** |  | [default to undefined]
**rating** | **number** |  | [default to undefined]
**message** | **string** |  | [optional] [default to 'Feedback registrado com sucesso.']

## Example

```typescript
import { PostTrainingFeedbackResponse } from './api';

const instance: PostTrainingFeedbackResponse = {
    session_id,
    athlete_id,
    rating,
    message,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
