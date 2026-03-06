# CompetitionSeasonUpdate

Schema para atualização de vínculo competição ↔ temporada (PATCH).  Campos editáveis: - name: Nome/descrição do vínculo  Campos NÃO editáveis (omitidos): - competition_id (imutável) - season_id (imutável)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionSeasonUpdate } from './api';

const instance: CompetitionSeasonUpdate = {
    name,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
