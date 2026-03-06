# ValidationResult

Resultado de validação (dry-run)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **boolean** |  | [default to undefined]
**errors** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**warnings** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**cpf_available** | **boolean** |  | [optional] [default to undefined]
**rg_available** | **boolean** |  | [optional] [default to undefined]
**email_available** | **boolean** |  | [optional] [default to undefined]
**phone_available** | **boolean** |  | [optional] [default to undefined]
**category_valid** | **boolean** |  | [optional] [default to undefined]
**gender_valid** | **boolean** |  | [optional] [default to undefined]
**goalkeeper_positions_valid** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { ValidationResult } from './api';

const instance: ValidationResult = {
    valid,
    errors,
    warnings,
    cpf_available,
    rg_available,
    email_available,
    phone_available,
    category_valid,
    gender_valid,
    goalkeeper_positions_valid,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
