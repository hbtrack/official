# PostTrainingFeedbackRequest

Corpo da requisição para registrar feedback pós-treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**feedback_text** | **string** | Texto do feedback (privado — INV-077) | [default to undefined]
**rating** | **number** | Percepção subjetiva de esforço 0–10 | [default to undefined]

## Example

```typescript
import { PostTrainingFeedbackRequest } from './api';

const instance: PostTrainingFeedbackRequest = {
    feedback_text,
    rating,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
