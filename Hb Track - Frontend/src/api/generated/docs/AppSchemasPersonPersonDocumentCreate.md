# AppSchemasPersonPersonDocumentCreate

Schema para criação de PersonDocument

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_type** | [**DocumentTypeEnum**](DocumentTypeEnum.md) | Tipo de documento | [default to undefined]
**document_number** | **string** | Número do documento | [default to undefined]
**issuing_authority** | **string** |  | [optional] [default to undefined]
**issue_date** | **string** |  | [optional] [default to undefined]
**expiry_date** | **string** |  | [optional] [default to undefined]
**document_file_url** | **string** |  | [optional] [default to undefined]
**is_verified** | **boolean** | Se o documento foi verificado | [optional] [default to false]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasPersonPersonDocumentCreate } from './api';

const instance: AppSchemasPersonPersonDocumentCreate = {
    document_type,
    document_number,
    issuing_authority,
    issue_date,
    expiry_date,
    document_file_url,
    is_verified,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
