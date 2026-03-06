# TeamRegistration

Schema de resposta completo para inscrição.  Nota (RDB10): start_at/end_at garantem períodos não sobrepostos por pessoa+equipe+temporada. Reativação cria nova linha (novo UUID).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID único da inscrição | [default to undefined]
**athlete_id** | **string** | ID do atleta | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**category_id** | **number** |  | [optional] [default to undefined]
**team_id** | **string** | ID da equipe | [default to undefined]
**organization_id** | **string** |  | [optional] [default to undefined]
**created_by_membership_id** | **string** |  | [optional] [default to undefined]
**role** | **string** |  | [optional] [default to undefined]
**start_at** | **string** | Data de início da inscrição (RDB10) | [default to undefined]
**end_at** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]
**athlete** | [**AppSchemasTeamRegistrationsAthleteNested**](AppSchemasTeamRegistrationsAthleteNested.md) |  | [optional] [default to undefined]

## Example

```typescript
import { TeamRegistration } from './api';

const instance: TeamRegistration = {
    id,
    athlete_id,
    season_id,
    category_id,
    team_id,
    organization_id,
    created_by_membership_id,
    role,
    start_at,
    end_at,
    created_at,
    updated_at,
    athlete,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
