# Organization

Schema completo de Organization para responses.  Inclui campos somente leitura (id, created_at, updated_at). Inclui campos de soft delete (deleted_at, deleted_reason) para suporte RDB4.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Nome da organização | [default to undefined]
**code** | **string** |  | [optional] [default to undefined]
**id** | **string** | ID único da organização | [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]

## Example

```typescript
import { Organization } from './api';

const instance: Organization = {
    name,
    code,
    id,
    deleted_at,
    deleted_reason,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
