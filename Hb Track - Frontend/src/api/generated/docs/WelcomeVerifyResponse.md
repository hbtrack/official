# WelcomeVerifyResponse

Resposta de verificação de token de welcome

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **boolean** | Se o token é válido | [default to undefined]
**email** | **string** | Email do convidado | [default to undefined]
**full_name** | **string** |  | [optional] [default to undefined]
**role** | **string** | Papel do convidado (ex: membro, treinador) | [default to undefined]
**invitee_kind** | **string** | Tipo: \&#39;staff\&#39; ou \&#39;athlete\&#39; | [default to undefined]
**team_name** | **string** |  | [optional] [default to undefined]
**organization_name** | **string** |  | [optional] [default to undefined]
**expires_at** | **string** | Data de expiração do token | [default to undefined]

## Example

```typescript
import { WelcomeVerifyResponse } from './api';

const instance: WelcomeVerifyResponse = {
    valid,
    email,
    full_name,
    role,
    invitee_kind,
    team_name,
    organization_name,
    expires_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
