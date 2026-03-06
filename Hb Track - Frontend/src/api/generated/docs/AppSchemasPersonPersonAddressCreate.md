# AppSchemasPersonPersonAddressCreate

Schema para criação de PersonAddress

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
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

## Example

```typescript
import { AppSchemasPersonPersonAddressCreate } from './api';

const instance: AppSchemasPersonPersonAddressCreate = {
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
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
