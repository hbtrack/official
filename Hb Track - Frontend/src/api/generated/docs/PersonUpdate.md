# PersonUpdate

Schema para atualização parcial de Person (V1.2)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **string** |  | [optional] [default to undefined]
**last_name** | **string** |  | [optional] [default to undefined]
**birth_date** | **string** |  | [optional] [default to undefined]
**gender** | [**GenderEnum**](GenderEnum.md) |  | [optional] [default to undefined]
**nationality** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { PersonUpdate } from './api';

const instance: PersonUpdate = {
    first_name,
    last_name,
    birth_date,
    gender,
    nationality,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
