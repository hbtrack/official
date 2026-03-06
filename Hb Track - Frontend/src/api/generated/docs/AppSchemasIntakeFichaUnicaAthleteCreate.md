# AppSchemasIntakeFichaUnicaAthleteCreate

Dados do atleta (athletes).  Criado apenas se create=True.  REGRAS: - Posição defensiva primária é OBRIGATÓRIA - Posição ofensiva primária é OBRIGATÓRIA, EXCETO para goleira (RD13) - Se posição defensiva = goleira, posições ofensivas são NULL

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**create** | **boolean** |  | [optional] [default to false]
**athlete_name** | **string** |  | [optional] [default to '']
**birth_date** | **string** |  | [optional] [default to undefined]
**athlete_nickname** | **string** |  | [optional] [default to undefined]
**shirt_number** | **number** |  | [optional] [default to undefined]
**schooling_id** | **number** |  | [optional] [default to undefined]
**guardian_name** | **string** |  | [optional] [default to undefined]
**guardian_phone** | **string** |  | [optional] [default to undefined]
**main_defensive_position_id** | **number** |  | [optional] [default to undefined]
**secondary_defensive_position_id** | **number** |  | [optional] [default to undefined]
**main_offensive_position_id** | **number** |  | [optional] [default to undefined]
**secondary_offensive_position_id** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { AppSchemasIntakeFichaUnicaAthleteCreate } from './api';

const instance: AppSchemasIntakeFichaUnicaAthleteCreate = {
    create,
    athlete_name,
    birth_date,
    athlete_nickname,
    shirt_number,
    schooling_id,
    guardian_name,
    guardian_phone,
    main_defensive_position_id,
    secondary_defensive_position_id,
    main_offensive_position_id,
    secondary_offensive_position_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
