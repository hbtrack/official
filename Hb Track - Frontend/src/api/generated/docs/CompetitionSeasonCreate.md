# CompetitionSeasonCreate

Schema para criação de vínculo competição ↔ temporada (POST).  Campos obrigatórios: - season_id: UUID da temporada a vincular  Constraint: UNIQUE (competition_id, season_id) - competition_id vem do path parameter - Violação retorna 409 conflict_unique

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**season_id** | **string** | ID da temporada a vincular (obrigatório) | [default to undefined]
**name** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionSeasonCreate } from './api';

const instance: CompetitionSeasonCreate = {
    season_id,
    name,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
