# PersonDocumentUpdate

Schema para atualização de PersonDocument

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_number** | **string** |  | [optional] [default to undefined]
**issuing_authority** | **string** |  | [optional] [default to undefined]
**issue_date** | **string** |  | [optional] [default to undefined]
**expiry_date** | **string** |  | [optional] [default to undefined]
**document_file_url** | **string** |  | [optional] [default to undefined]
**is_verified** | **boolean** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { PersonDocumentUpdate } from './api';

const instance: PersonDocumentUpdate = {
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
