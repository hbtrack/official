# CategoryCreate

Schema para criação de Category

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Nome da categoria (ex: Mirim, Infantil) | [default to undefined]
**max_age** | **number** | Idade máxima para a categoria | [default to undefined]
**is_active** | **boolean** | Se a categoria está ativa | [optional] [default to true]

## Example

```typescript
import { CategoryCreate } from './api';

const instance: CategoryCreate = {
    name,
    max_age,
    is_active,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
