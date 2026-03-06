# AppSchemasIntakeFichaUnicaUserCreate

Usuário para login (users).  Se create_user=True no payload principal, este bloco é processado. - Cria user vinculado à person - Gera password_reset com token_type=\'welcome\' - Envia email de ativação via SendGrid

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **string** |  | [default to undefined]
**role_id** | **number** | ID do papel: 1&#x3D;dirigente, 2&#x3D;coordenador, 3&#x3D;treinador, 4&#x3D;atleta | [default to undefined]

## Example

```typescript
import { AppSchemasIntakeFichaUnicaUserCreate } from './api';

const instance: AppSchemasIntakeFichaUnicaUserCreate = {
    email,
    role_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
