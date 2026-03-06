# AppSchemasPersonPersonCreate

Schema para criação de Person (V1.2)  Permite criar pessoa com contatos, endereços, documentos e mídias de uma vez.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **string** | Primeiro nome | [default to undefined]
**last_name** | **string** | Sobrenome | [default to undefined]
**birth_date** | **string** |  | [optional] [default to undefined]
**gender** | [**GenderEnum**](GenderEnum.md) |  | [optional] [default to undefined]
**nationality** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**contacts** | [**Array&lt;AppSchemasPersonPersonContactCreate&gt;**](AppSchemasPersonPersonContactCreate.md) |  | [optional] [default to undefined]
**addresses** | [**Array&lt;AppSchemasPersonPersonAddressCreate&gt;**](AppSchemasPersonPersonAddressCreate.md) |  | [optional] [default to undefined]
**documents** | [**Array&lt;AppSchemasPersonPersonDocumentCreate&gt;**](AppSchemasPersonPersonDocumentCreate.md) |  | [optional] [default to undefined]
**media** | [**Array&lt;AppSchemasPersonPersonMediaCreate&gt;**](AppSchemasPersonPersonMediaCreate.md) |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasPersonPersonCreate } from './api';

const instance: AppSchemasPersonPersonCreate = {
    first_name,
    last_name,
    birth_date,
    gender,
    nationality,
    notes,
    contacts,
    addresses,
    documents,
    media,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
