# UnifiedRegistrationRequest

Request completo para cadastro unificado

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registration_type** | [**RegistrationType**](RegistrationType.md) |  | [optional] [default to undefined]
**create_user** | **boolean** |  | [optional] [default to false]
**core** | [**CoreDataSchema**](CoreDataSchema.md) |  | [default to undefined]
**documents** | [**DocumentsSchema**](DocumentsSchema.md) |  | [optional] [default to undefined]
**contacts** | [**ContactsSchema**](ContactsSchema.md) |  | [optional] [default to undefined]
**address** | [**AddressSchema**](AddressSchema.md) |  | [optional] [default to undefined]
**athlete** | [**AthleteDataSchema**](AthleteDataSchema.md) |  | [optional] [default to undefined]
**organization** | [**OrganizationBindingSchema**](OrganizationBindingSchema.md) |  | [optional] [default to undefined]
**team** | [**TeamBindingSchema**](TeamBindingSchema.md) |  | [optional] [default to undefined]

## Example

```typescript
import { UnifiedRegistrationRequest } from './api';

const instance: UnifiedRegistrationRequest = {
    registration_type,
    create_user,
    core,
    documents,
    contacts,
    address,
    athlete,
    organization,
    team,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
