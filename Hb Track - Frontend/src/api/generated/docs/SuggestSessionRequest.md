# SuggestSessionRequest

Solicitar sugestão de sessão de treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **string** |  | [optional] [default to undefined]
**justification** | **string** | Justificativa baseada em sinais do sistema (INV-081) | [default to undefined]
**context** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { SuggestSessionRequest } from './api';

const instance: SuggestSessionRequest = {
    title,
    justification,
    context,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
