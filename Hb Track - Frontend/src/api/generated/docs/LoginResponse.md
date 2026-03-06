# LoginResponse

Resposta de login com JWT

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_token** | **string** | JWT access token | [default to undefined]
**refresh_token** | **string** | JWT refresh token (validade 7 dias) | [default to undefined]
**token_type** | **string** | Tipo do token | [optional] [default to 'bearer']
**expires_in** | **number** | Expiração em segundos | [default to undefined]
**user_id** | **string** | ID do usuário | [default to undefined]
**full_name** | **string** |  | [optional] [default to undefined]
**email** | **string** | Email do usuário | [default to undefined]
**role_code** | **string** | Papel do usuário | [default to undefined]
**role_name** | **string** |  | [optional] [default to undefined]
**is_superadmin** | **boolean** | Se é superadmin | [default to undefined]
**organization_id** | **string** |  | [optional] [default to undefined]
**photo_url** | **string** |  | [optional] [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**permissions** | **{ [key: string]: boolean; }** | Mapa de permissões do usuário | [optional] [default to undefined]
**needs_setup** | **boolean** | Se dirigente precisa configurar organização inicial | [optional] [default to false]

## Example

```typescript
import { LoginResponse } from './api';

const instance: LoginResponse = {
    access_token,
    refresh_token,
    token_type,
    expires_in,
    user_id,
    full_name,
    email,
    role_code,
    role_name,
    is_superadmin,
    organization_id,
    photo_url,
    gender,
    permissions,
    needs_setup,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
