# WelcomeCompleteRequest

Requisição para completar cadastro de welcome

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **string** | Token de welcome | [default to undefined]
**password** | **string** | Nova senha (mínimo 8 caracteres) | [default to undefined]
**confirm_password** | **string** | Confirmação da senha | [default to undefined]
**full_name** | **string** | Nome completo | [default to undefined]
**phone** | **string** |  | [optional] [default to undefined]
**birth_date** | **string** | Data de nascimento (obrigatório) | [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**certifications** | **string** |  | [optional] [default to undefined]
**specialization** | **string** |  | [optional] [default to undefined]
**area_of_expertise** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { WelcomeCompleteRequest } from './api';

const instance: WelcomeCompleteRequest = {
    token,
    password,
    confirm_password,
    full_name,
    phone,
    birth_date,
    gender,
    certifications,
    specialization,
    area_of_expertise,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
