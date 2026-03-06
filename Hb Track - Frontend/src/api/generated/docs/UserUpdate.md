# UserUpdate

Payload para atualização de usuário. V1.2: full_name/phone pertencem a Person - usar endpoint /persons para atualizar.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **string** |  | [optional] [default to undefined]
**status** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { UserUpdate } from './api';

const instance: UserUpdate = {
    email,
    status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
