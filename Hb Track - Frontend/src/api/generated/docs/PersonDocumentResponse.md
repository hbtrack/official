# PersonDocumentResponse

Schema de resposta de PersonDocument

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data de criação (UTC) | [default to undefined]
**updated_at** | **string** | Data da última atualização (UTC) | [default to undefined]
**id** | **string** | ID único do recurso (UUID v4) | [default to undefined]
**document_type** | [**DocumentTypeEnum**](DocumentTypeEnum.md) | Tipo de documento | [default to undefined]
**document_number** | **string** | Número do documento | [default to undefined]
**issuing_authority** | **string** |  | [optional] [default to undefined]
**issue_date** | **string** |  | [optional] [default to undefined]
**expiry_date** | **string** |  | [optional] [default to undefined]
**document_file_url** | **string** |  | [optional] [default to undefined]
**is_verified** | **boolean** | Se o documento foi verificado | [optional] [default to false]
**notes** | **string** |  | [optional] [default to undefined]
**person_id** | **string** |  | [default to undefined]

## Example

```typescript
import { PersonDocumentResponse } from './api';

const instance: PersonDocumentResponse = {
    deleted_at,
    deleted_reason,
    created_at,
    updated_at,
    id,
    document_type,
    document_number,
    issuing_authority,
    issue_date,
    expiry_date,
    document_file_url,
    is_verified,
    notes,
    person_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
