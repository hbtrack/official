# TeamRegistrationCreate

Schema para criação de inscrição (POST).  Validações: - start_at obrigatório - end_at >= start_at (quando informado) - Backend valida R16/RD1-RD2 (categoria vs birth_date) - Backend valida RDB10 (não-sobreposição de período) - Backend valida RF5.2/R37 (temporada bloqueada)  Campos obrigatórios: season_id, category_id, team_id, organization_id, created_by_membership_id, start_at

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**season_id** | **string** | ID da temporada (obrigatório) | [default to undefined]
**category_id** | **number** | ID da categoria (obrigatório; validar R16) | [default to undefined]
**team_id** | **string** | ID da equipe (obrigatório) | [default to undefined]
**organization_id** | **string** | ID da organização (obrigatório) | [default to undefined]
**created_by_membership_id** | **string** | ID do membership criador (obrigatório) | [default to undefined]
**role** | **string** |  | [optional] [default to undefined]
**start_at** | **string** | Data de início (obrigatório; RDB10) | [default to undefined]
**end_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamRegistrationCreate } from './api';

const instance: TeamRegistrationCreate = {
    season_id,
    category_id,
    team_id,
    organization_id,
    created_by_membership_id,
    role,
    start_at,
    end_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
