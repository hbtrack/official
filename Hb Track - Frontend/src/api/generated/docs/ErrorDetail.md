# ErrorDetail

Detalhes adicionais do erro

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**field** | **string** |  | [optional] [default to undefined]
**constraint** | **string** |  | [optional] [default to undefined]
**existing_id** | **string** |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ErrorDetail } from './api';

const instance: ErrorDetail = {
    field,
    constraint,
    existing_id,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
