# UserMeResponse

Resposta do /auth/me - Step 3: Incluir permissões

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **string** |  | [default to undefined]
**person_id** | **string** |  | [default to undefined]
**email** | **string** |  | [default to undefined]
**full_name** | **string** |  | [default to undefined]
**role_code** | **string** |  | [default to undefined]
**is_superadmin** | **boolean** |  | [default to undefined]
**membership_id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**permissions** | **{ [key: string]: boolean; }** | Mapa de permissões (step 3) | [optional] [default to undefined]

## Example

```typescript
import { UserMeResponse } from './api';

const instance: UserMeResponse = {
    user_id,
    person_id,
    email,
    full_name,
    role_code,
    is_superadmin,
    membership_id,
    organization_id,
    permissions,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
