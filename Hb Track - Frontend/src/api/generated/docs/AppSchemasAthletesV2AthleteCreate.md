# AppSchemasAthletesV2AthleteCreate

Payload para criação de atleta.  Campos obrigatórios: - athlete_name (min 3 chars) - birth_date - main_defensive_position_id - athlete_rg (UNIQUE) - athlete_cpf (UNIQUE) - athlete_phone - team_id (UUID opcional; se ausente, usa equipe institucional)  Campos opcionais: - athlete_nickname - shirt_number (1-99) - main_offensive_position_id (OBRIGATÓRIO exceto goleiras - RD13) - secondary_defensive_position_id - secondary_offensive_position_id - athlete_email (UNIQUE, case-insensitive) - guardian_name, guardian_phone - schooling_id - zip_code, street, neighborhood, city, address_state, address_number, address_complement  NOTA: category_id NÃO está aqui (será atribuído em team_registrations - RD1/RD2)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_name** | **string** | Nome completo da atleta | [default to undefined]
**birth_date** | **string** | Data de nascimento (YYYY-MM-DD) | [default to undefined]
**gender** | **string** | Gênero: \&#39;masculino\&#39; ou \&#39;feminino\&#39; (obrigatório para validação R15) | [default to undefined]
**main_defensive_position_id** | **number** | Posição defensiva principal (FK defensive_positions) | [default to undefined]
**secondary_defensive_position_id** | **number** |  | [optional] [default to undefined]
**main_offensive_position_id** | **number** |  | [optional] [default to undefined]
**secondary_offensive_position_id** | **number** |  | [optional] [default to undefined]
**athlete_rg** | **string** | RG (UNIQUE) | [default to undefined]
**athlete_cpf** | **string** | CPF (UNIQUE) | [default to undefined]
**athlete_phone** | **string** | Telefone | [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**athlete_nickname** | **string** |  | [optional] [default to undefined]
**shirt_number** | **number** |  | [optional] [default to undefined]
**athlete_email** | **string** |  | [optional] [default to undefined]
**guardian_name** | **string** |  | [optional] [default to undefined]
**guardian_phone** | **string** |  | [optional] [default to undefined]
**schooling_id** | **number** |  | [optional] [default to undefined]
**zip_code** | **string** |  | [optional] [default to undefined]
**street** | **string** |  | [optional] [default to undefined]
**neighborhood** | **string** |  | [optional] [default to undefined]
**city** | **string** |  | [optional] [default to undefined]
**address_state** | **string** |  | [optional] [default to undefined]
**address_number** | **string** |  | [optional] [default to undefined]
**address_complement** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasAthletesV2AthleteCreate } from './api';

const instance: AppSchemasAthletesV2AthleteCreate = {
    athlete_name,
    birth_date,
    gender,
    main_defensive_position_id,
    secondary_defensive_position_id,
    main_offensive_position_id,
    secondary_offensive_position_id,
    athlete_rg,
    athlete_cpf,
    athlete_phone,
    team_id,
    athlete_nickname,
    shirt_number,
    athlete_email,
    guardian_name,
    guardian_phone,
    schooling_id,
    zip_code,
    street,
    neighborhood,
    city,
    address_state,
    address_number,
    address_complement,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
