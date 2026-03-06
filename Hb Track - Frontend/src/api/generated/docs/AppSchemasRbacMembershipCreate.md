# AppSchemasRbacMembershipCreate

Payload para criação de vínculo (V1.2).  V1.2: usa person_id (não user_id), sem season_id. organization_id vem da URL path parameter. superadmin não pode ser criado via API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**person_id** | **string** | ID da pessoa a vincular (V1.2: usa person_id) | [default to undefined]
**role_code** | [**RoleCodeCreate**](RoleCodeCreate.md) | Código do papel (superadmin não permitido via API) | [default to undefined]
**start_date** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasRbacMembershipCreate } from './api';

const instance: AppSchemasRbacMembershipCreate = {
    person_id,
    role_code,
    start_date,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
