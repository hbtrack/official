# FichaUnicaDryRunResponse

Resposta do modo dry-run (validate_only=true).  Usado para pré-validação do formulário sem efetivar a criação. Retorna validação completa + preview das entidades que seriam criadas.  Exemplo de uso:     POST /api/v1/intake/ficha-unica?validate_only=true      Response:     {         \"valid\": true,         \"warnings\": [\"Atleta será cadastrada em categoria acima da natural\"],         \"preview\": {             \"person\": {\"first_name\": \"Maria\", \"last_name\": \"Silva\", ...},             \"user_will_be_created\": true,             \"organization_will_be_created\": false,             \"team_will_be_created\": false,             \"athlete_will_be_created\": true,             \"membership_will_be_created\": false,             \"registration_will_be_created\": true         }     }

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **boolean** |  | [default to undefined]
**warnings** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**errors** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**preview** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**validation_details** | [**ValidationResult**](ValidationResult.md) |  | [optional] [default to undefined]

## Example

```typescript
import { FichaUnicaDryRunResponse } from './api';

const instance: FichaUnicaDryRunResponse = {
    valid,
    warnings,
    errors,
    preview,
    validation_details,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
