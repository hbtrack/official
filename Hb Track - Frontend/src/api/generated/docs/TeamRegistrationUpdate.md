# TeamRegistrationUpdate

Schema para atualização de inscrição (PATCH).  Campos editáveis: - end_at: Data de término (para encerramento) - role: Papel/posição na equipe  Campos NÃO editáveis (omitidos): - athlete_id, season_id, category_id, team_id, organization_id, created_by_membership_id  Validações (backend): - Não reabrir período encerrado (RDB10) - end_at >= start_at - Sem sobreposição de período - Temporada não bloqueada (R37/RF5.2)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**end_at** | **string** |  | [optional] [default to undefined]
**role** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamRegistrationUpdate } from './api';

const instance: TeamRegistrationUpdate = {
    end_at,
    role,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
