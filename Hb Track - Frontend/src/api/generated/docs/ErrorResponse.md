# ErrorResponse

Resposta de erro padronizada (FASE 3)  Usado em todos os endpoints da API para retornar erros estruturados. Mapeia error_code para regras RAG V1.1 (seção 8).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error_code** | [**ErrorCode**](ErrorCode.md) | Código do erro (enum) | [default to undefined]
**message** | **string** | Mensagem legível do erro | [default to undefined]
**details** | [**ErrorDetail**](ErrorDetail.md) |  | [optional] [default to undefined]
**timestamp** | **string** | Timestamp UTC do erro | [optional] [default to undefined]
**request_id** | **string** | ID da requisição para rastreamento | [default to undefined]

## Example

```typescript
import { ErrorResponse } from './api';

const instance: ErrorResponse = {
    error_code,
    message,
    details,
    timestamp,
    request_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
