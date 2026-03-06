# AIParseResponse

Response do parse de PDF via Gemini.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** |  | [default to undefined]
**extracted_data** | [**AIExtractedCompetitionOutput**](AIExtractedCompetitionOutput.md) |  | [optional] [default to undefined]
**error_message** | **string** |  | [optional] [default to undefined]
**processing_time_ms** | **number** |  | [optional] [default to undefined]
**tokens_used** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { AIParseResponse } from './api';

const instance: AIParseResponse = {
    success,
    extracted_data,
    error_message,
    processing_time_ms,
    tokens_used,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
