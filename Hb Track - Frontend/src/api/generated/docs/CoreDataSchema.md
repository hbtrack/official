# CoreDataSchema

Dados pessoais básicos (obrigatórios)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**full_name** | **string** |  | [default to undefined]
**birth_date** | **string** |  | [default to undefined]
**gender** | [**Gender**](Gender.md) |  | [default to undefined]
**email** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CoreDataSchema } from './api';

const instance: CoreDataSchema = {
    full_name,
    birth_date,
    gender,
    email,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
