# SessionClosureResponse

Resposta do fechamento de sessão.  Se success=True, session contém a sessão atualizada. Se success=False, validation contém os erros detalhados.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** | True se fechou com sucesso | [default to undefined]
**session** | [**TrainingSessionResponse**](TrainingSessionResponse.md) |  | [optional] [default to undefined]
**validation** | [**SessionClosureValidationResult**](SessionClosureValidationResult.md) |  | [optional] [default to undefined]
**message** | **string** | Mensagem descritiva | [default to undefined]

## Example

```typescript
import { SessionClosureResponse } from './api';

const instance: SessionClosureResponse = {
    success,
    session,
    validation,
    message,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
