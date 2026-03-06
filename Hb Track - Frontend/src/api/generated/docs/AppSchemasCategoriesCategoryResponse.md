# AppSchemasCategoriesCategoryResponse

Schema de resposta com todos os campos

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Nome da categoria (ex: Mirim, Infantil) | [default to undefined]
**max_age** | **number** | Idade máxima para a categoria | [default to undefined]
**is_active** | **boolean** | Se a categoria está ativa | [optional] [default to true]
**id** | **number** | ID da categoria | [default to undefined]

## Example

```typescript
import { AppSchemasCategoriesCategoryResponse } from './api';

const instance: AppSchemasCategoriesCategoryResponse = {
    name,
    max_age,
    is_active,
    id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
