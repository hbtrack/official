# SetPasswordRequest

Requisição para definir senha com token (primeira vez)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **string** | Token recebido no email | [default to undefined]
**password** | **string** | Nova senha (mínimo 8 caracteres) | [default to undefined]

## Example

```typescript
import { SetPasswordRequest } from './api';

const instance: SetPasswordRequest = {
    token,
    password,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
