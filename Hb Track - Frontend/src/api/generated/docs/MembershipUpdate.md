# MembershipUpdate

Payload para atualização de vínculo.  user_id e organization_id não podem ser alterados via API. superadmin não pode ser atribuído via API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_code** | [**RoleCodeCreate**](RoleCodeCreate.md) |  | [optional] [default to undefined]
**is_active** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { MembershipUpdate } from './api';

const instance: MembershipUpdate = {
    role_code,
    is_active,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
