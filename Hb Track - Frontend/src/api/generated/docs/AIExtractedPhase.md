# AIExtractedPhase

Fase extraída pelo Gemini.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**phase_type** | **string** |  | [default to undefined]
**order_index** | **number** |  | [optional] [default to 0]
**teams** | [**Array&lt;AIExtractedTeam&gt;**](AIExtractedTeam.md) |  | [optional] [default to undefined]
**matches** | [**Array&lt;AIExtractedMatch&gt;**](AIExtractedMatch.md) |  | [optional] [default to undefined]
**confidence_score** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { AIExtractedPhase } from './api';

const instance: AIExtractedPhase = {
    name,
    phase_type,
    order_index,
    teams,
    matches,
    confidence_score,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
