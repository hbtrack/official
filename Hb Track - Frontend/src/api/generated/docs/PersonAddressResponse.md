# PersonAddressResponse

Schema de resposta de PersonAddress

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data de criação (UTC) | [default to undefined]
**updated_at** | **string** | Data da última atualização (UTC) | [default to undefined]
**id** | **string** | ID único do recurso (UUID v4) | [default to undefined]
**address_type** | [**AddressTypeEnum**](AddressTypeEnum.md) | Tipo de endereço | [default to undefined]
**street** | **string** | Logradouro | [default to undefined]
**number** | **string** |  | [optional] [default to undefined]
**complement** | **string** |  | [optional] [default to undefined]
**neighborhood** | **string** |  | [optional] [default to undefined]
**city** | **string** | Cidade | [default to undefined]
**state** | **string** | Estado (UF) | [default to undefined]
**postal_code** | **string** |  | [optional] [default to undefined]
**country** | **string** | País | [optional] [default to 'Brasil']
**is_primary** | **boolean** | Se é o endereço primário | [optional] [default to false]
**person_id** | **string** |  | [default to undefined]

## Example

```typescript
import { PersonAddressResponse } from './api';

const instance: PersonAddressResponse = {
    deleted_at,
    deleted_reason,
    created_at,
    updated_at,
    id,
    address_type,
    street,
    number,
    complement,
    neighborhood,
    city,
    state,
    postal_code,
    country,
    is_primary,
    person_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
