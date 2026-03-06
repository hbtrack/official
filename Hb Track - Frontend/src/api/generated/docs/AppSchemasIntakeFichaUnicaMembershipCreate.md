# AppSchemasIntakeFichaUnicaMembershipCreate

Vínculo organizacional (org_memberships).  Criado para staff (dirigente, coordenador, treinador). Atletas não têm org_membership, apenas team_registration.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_id** | **number** | ID do papel no vínculo | [default to undefined]
**start_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasIntakeFichaUnicaMembershipCreate } from './api';

const instance: AppSchemasIntakeFichaUnicaMembershipCreate = {
    role_id,
    start_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
