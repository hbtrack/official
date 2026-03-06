# FichaUnicaRequest

Payload completo da Ficha Única.  Transação atômica: 1. Upsert Person (valida CPF/RG, email, telefone; dedup) 2. Criar User (opcional) - envia email welcome 3. Criar/Selecionar Season (obrigatório se criar/selecionar org/team) 4. Criar/Selecionar Organization (vinculada à temporada) 5. Criar/Selecionar Team (vinculada à temporada) 6. Criar Athlete (opcional) 7. Criar Vínculos (membership, team_registration) 8. Commit + invalidate_report_cache()  Suporta: - Idempotency-Key header para evitar duplicação - ?validate_only=true para dry-run

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**person** | [**AppSchemasIntakeFichaUnicaPersonCreate**](AppSchemasIntakeFichaUnicaPersonCreate.md) |  | [default to undefined]
**create_user** | **boolean** |  | [optional] [default to false]
**user** | [**AppSchemasIntakeFichaUnicaUserCreate**](AppSchemasIntakeFichaUnicaUserCreate.md) |  | [optional] [default to undefined]
**season** | [**SeasonSelection**](SeasonSelection.md) |  | [optional] [default to undefined]
**organization** | [**OrganizationSelection**](OrganizationSelection.md) |  | [optional] [default to undefined]
**membership** | [**AppSchemasIntakeFichaUnicaMembershipCreate**](AppSchemasIntakeFichaUnicaMembershipCreate.md) |  | [optional] [default to undefined]
**team** | [**TeamSelection**](TeamSelection.md) |  | [optional] [default to undefined]
**athlete** | [**AppSchemasIntakeFichaUnicaAthleteCreate**](AppSchemasIntakeFichaUnicaAthleteCreate.md) |  | [optional] [default to undefined]
**registration** | [**RegistrationCreate**](RegistrationCreate.md) |  | [optional] [default to undefined]

## Example

```typescript
import { FichaUnicaRequest } from './api';

const instance: FichaUnicaRequest = {
    person,
    create_user,
    user,
    season,
    organization,
    membership,
    team,
    athlete,
    registration,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
