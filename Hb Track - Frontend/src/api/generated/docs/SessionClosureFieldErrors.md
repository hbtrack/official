# SessionClosureFieldErrors

Erros estruturados por campo para revisão operacional.  Usado para retornar validações detalhadas ao frontend, permitindo exibição de erros inline no fluxo de revisão.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**execution_outcome** | **string** |  | [optional] [default to undefined]
**delay_minutes** | **string** |  | [optional] [default to undefined]
**duration_actual_minutes** | **string** |  | [optional] [default to undefined]
**cancellation_reason** | **string** |  | [optional] [default to undefined]
**deviation_justification** | **string** |  | [optional] [default to undefined]
**presence** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { SessionClosureFieldErrors } from './api';

const instance: SessionClosureFieldErrors = {
    execution_outcome,
    delay_minutes,
    duration_actual_minutes,
    cancellation_reason,
    deviation_justification,
    presence,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
