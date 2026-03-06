# User

Schema completo de User para responses.  Inclui campos somente leitura (id, created_at, updated_at). Inclui campos de soft delete (deleted_at, deleted_reason) para suporte RDB4.  V1.2: full_name vem de Person (R1), não é campo direto de User.  Note: Uses str for email instead of EmailStr to allow special addresses like superadmin@seed.local which are used in database seeds.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID único do usuário | [default to undefined]
**person_id** | **string** |  | [optional] [default to undefined]
**email** | **string** | Email (único no sistema) | [default to undefined]
**status** | **string** | Status do usuário: ativo, inativo, arquivado | [optional] [default to 'ativo']
**is_superadmin** | **boolean** | Se é Super Administrador (R3) | [optional] [default to false]
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]

## Example

```typescript
import { User } from './api';

const instance: User = {
    id,
    person_id,
    email,
    status,
    is_superadmin,
    deleted_at,
    deleted_reason,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
