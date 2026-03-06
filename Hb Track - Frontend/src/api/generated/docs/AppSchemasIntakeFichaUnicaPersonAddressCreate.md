# AppSchemasIntakeFichaUnicaPersonAddressCreate

Endereço da pessoa (person_addresses)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_type** | **string** |  | [optional] [default to AddressTypeEnum_Residencial1]
**street** | **string** |  | [default to undefined]
**number** | **string** |  | [optional] [default to undefined]
**complement** | **string** |  | [optional] [default to undefined]
**neighborhood** | **string** |  | [optional] [default to undefined]
**city** | **string** |  | [default to undefined]
**state** | **string** |  | [default to undefined]
**postal_code** | **string** |  | [optional] [default to undefined]
**country** | **string** |  | [optional] [default to 'Brasil']

## Example

```typescript
import { AppSchemasIntakeFichaUnicaPersonAddressCreate } from './api';

const instance: AppSchemasIntakeFichaUnicaPersonAddressCreate = {
    address_type,
    street,
    number,
    complement,
    neighborhood,
    city,
    state,
    postal_code,
    country,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
