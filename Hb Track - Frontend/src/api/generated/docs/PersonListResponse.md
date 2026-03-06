# PersonListResponse

Schema de resposta para listagem de Person (simplificado)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**full_name** | **string** |  | [default to undefined]
**first_name** | **string** |  | [default to undefined]
**last_name** | **string** |  | [default to undefined]
**birth_date** | **string** |  | [optional] [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**primary_phone** | **string** |  | [optional] [default to undefined]
**primary_email** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { PersonListResponse } from './api';

const instance: PersonListResponse = {
    id,
    full_name,
    first_name,
    last_name,
    birth_date,
    gender,
    primary_phone,
    primary_email,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
