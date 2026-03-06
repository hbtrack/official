# ExportJobResponse

Response for export job status

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**export_type** | **string** |  | [default to undefined]
**status** | **string** |  | [default to undefined]
**params** | **{ [key: string]: any; }** |  | [default to undefined]
**file_url** | **string** |  | [optional] [default to undefined]
**file_size_bytes** | **number** |  | [optional] [default to undefined]
**error_message** | **string** |  | [optional] [default to undefined]
**started_at** | **string** |  | [optional] [default to undefined]
**completed_at** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [default to undefined]
**expires_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ExportJobResponse } from './api';

const instance: ExportJobResponse = {
    id,
    export_type,
    status,
    params,
    file_url,
    file_size_bytes,
    error_message,
    started_at,
    completed_at,
    created_at,
    expires_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
