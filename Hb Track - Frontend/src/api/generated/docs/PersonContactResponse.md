# PersonContactResponse

Schema de resposta de PersonContact

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data de criação (UTC) | [default to undefined]
**updated_at** | **string** | Data da última atualização (UTC) | [default to undefined]
**id** | **string** | ID único do recurso (UUID v4) | [default to undefined]
**contact_type** | [**ContactTypeEnum**](ContactTypeEnum.md) | Tipo de contato | [default to undefined]
**contact_value** | **string** | Valor do contato | [default to undefined]
**is_primary** | **boolean** | Se é o contato primário deste tipo | [optional] [default to false]
**is_verified** | **boolean** | Se o contato foi verificado | [optional] [default to false]
**notes** | **string** |  | [optional] [default to undefined]
**person_id** | **string** |  | [default to undefined]

## Example

```typescript
import { PersonContactResponse } from './api';

const instance: PersonContactResponse = {
    deleted_at,
    deleted_reason,
    created_at,
    updated_at,
    id,
    contact_type,
    contact_value,
    is_primary,
    is_verified,
    notes,
    person_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
