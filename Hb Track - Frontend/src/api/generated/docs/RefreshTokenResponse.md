# RefreshTokenResponse

Resposta de refresh de token

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_token** | **string** | Novo access token JWT | [default to undefined]
**refresh_token** | **string** | Novo refresh token JWT | [default to undefined]
**token_type** | **string** | Tipo do token | [optional] [default to 'bearer']
**expires_in** | **number** | Expiração do access token em segundos | [default to undefined]

## Example

```typescript
import { RefreshTokenResponse } from './api';

const instance: RefreshTokenResponse = {
    access_token,
    refresh_token,
    token_type,
    expires_in,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
