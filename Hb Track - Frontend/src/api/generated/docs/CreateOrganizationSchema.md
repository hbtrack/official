# CreateOrganizationSchema

Dados para criar nova organização

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**legal_name** | **string** |  | [optional] [default to undefined]
**document** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CreateOrganizationSchema } from './api';

const instance: CreateOrganizationSchema = {
    name,
    legal_name,
    document,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
