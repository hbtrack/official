# AppSchemasPersonPersonContactCreate

Schema para criação de PersonContact

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contact_type** | [**ContactTypeEnum**](ContactTypeEnum.md) | Tipo de contato | [default to undefined]
**contact_value** | **string** | Valor do contato | [default to undefined]
**is_primary** | **boolean** | Se é o contato primário deste tipo | [optional] [default to false]
**is_verified** | **boolean** | Se o contato foi verificado | [optional] [default to false]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasPersonPersonContactCreate } from './api';

const instance: AppSchemasPersonPersonContactCreate = {
    contact_type,
    contact_value,
    is_primary,
    is_verified,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
