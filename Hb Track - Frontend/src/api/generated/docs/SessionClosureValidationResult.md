# SessionClosureValidationResult

Resultado da validação de revisão operacional.  Retornado pelo endpoint de revisão para informar ao frontend quais campos precisam de correção antes de finalizar.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**can_close** | **boolean** | True se a sessão pode ser finalizada sem erros | [default to undefined]
**error_code** | **string** |  | [optional] [default to undefined]
**field_errors** | [**SessionClosureFieldErrors**](SessionClosureFieldErrors.md) | Erros detalhados por campo | [optional] [default to undefined]
**athletes_without_presence** | [**Array&lt;AthleteWithoutPresence&gt;**](AthleteWithoutPresence.md) | Lista de atletas ativos sem presença registrada | [optional] [default to undefined]

## Example

```typescript
import { SessionClosureValidationResult } from './api';

const instance: SessionClosureValidationResult = {
    can_close,
    error_code,
    field_errors,
    athletes_without_presence,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
