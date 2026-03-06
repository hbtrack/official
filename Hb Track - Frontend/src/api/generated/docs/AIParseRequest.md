# AIParseRequest

Request para parse de PDF via Gemini.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pdf_base64** | **string** | Conteúdo do PDF em base64 | [default to undefined]
**our_team_name** | **string** |  | [optional] [default to undefined]
**hints** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { AIParseRequest } from './api';

const instance: AIParseRequest = {
    pdf_base64,
    our_team_name,
    hints,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
