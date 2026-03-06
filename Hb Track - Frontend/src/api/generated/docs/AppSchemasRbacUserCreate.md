# AppSchemasRbacUserCreate

Payload para criação de usuário.  V1.2 - RF1.1: - person_id obrigatório (Person deve existir antes) - full_name/phone pertencem a Person, não a User - role define o papel do usuário

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **string** | Email (único no sistema) | [default to undefined]
**password** | **string** |  | [optional] [default to undefined]
**person_id** | **string** | ID da pessoa associada (R1 - Person deve existir) | [default to undefined]
**role** | **string** | Papel do usuário: dirigente, coordenador, treinador | [optional] [default to 'dirigente']
**send_welcome_email** | **boolean** | Se true, envia email de boas-vindas com link para criar senha | [optional] [default to true]

## Example

```typescript
import { AppSchemasRbacUserCreate } from './api';

const instance: AppSchemasRbacUserCreate = {
    email,
    password,
    person_id,
    role,
    send_welcome_email,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
