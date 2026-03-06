# Role

Schema de Role (catálogo de papéis).  Papéis V1: dirigente, coordenador, treinador, atleta Ref: R4, RDB2.1

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **number** | ID do papel (smallint) | [default to undefined]
**code** | **string** | Código único do papel | [default to undefined]
**name** | **string** | Nome exibível do papel | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { Role } from './api';

const instance: Role = {
    id,
    code,
    name,
    description,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
