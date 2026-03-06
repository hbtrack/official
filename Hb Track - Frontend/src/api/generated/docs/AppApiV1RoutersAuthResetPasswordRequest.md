# AppApiV1RoutersAuthResetPasswordRequest

Requisição para resetar senha

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **string** | Token de reset | [default to undefined]
**new_password** | **string** | Nova senha (mínimo 8 caracteres) | [default to undefined]
**confirm_password** | **string** | Confirmação da nova senha | [default to undefined]

## Example

```typescript
import { AppApiV1RoutersAuthResetPasswordRequest } from './api';

const instance: AppApiV1RoutersAuthResetPasswordRequest = {
    token,
    new_password,
    confirm_password,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
