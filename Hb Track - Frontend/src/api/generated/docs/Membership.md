# Membership

Schema completo de Membership para responses.  Vínculo user↔organization+role com constraint: UNIQUE(user_id, organization_id) onde is_active=true

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID único do vínculo | [default to undefined]
**user_id** | **string** | ID do usuário vinculado | [default to undefined]
**organization_id** | **string** | ID da organização | [default to undefined]
**role_code** | [**RoleCode**](RoleCode.md) | Código do papel atribuído | [default to undefined]
**is_active** | **boolean** | Se o vínculo está ativo | [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]

## Example

```typescript
import { Membership } from './api';

const instance: Membership = {
    id,
    user_id,
    organization_id,
    role_code,
    is_active,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
