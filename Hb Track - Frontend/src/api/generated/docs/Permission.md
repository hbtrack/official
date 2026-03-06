# Permission

Schema de Permission (catálogo de permissões).  Permissões V1: - read_athlete, edit_athlete - read_training, edit_training - read_match, edit_match - admin_memberships, admin_organization

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **string** | Código único da permissão | [default to undefined]
**name** | **string** | Nome exibível da permissão | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**roles** | **Array&lt;string&gt;** | Papéis que possuem esta permissão | [default to undefined]

## Example

```typescript
import { Permission } from './api';

const instance: Permission = {
    code,
    name,
    description,
    roles,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
