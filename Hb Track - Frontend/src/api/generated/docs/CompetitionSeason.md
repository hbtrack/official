# CompetitionSeason

Schema de resposta completo para vínculo competição ↔ temporada.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID único do vínculo | [default to undefined]
**competition_id** | **string** | ID da competição | [default to undefined]
**season_id** | **string** | ID da temporada | [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]

## Example

```typescript
import { CompetitionSeason } from './api';

const instance: CompetitionSeason = {
    id,
    competition_id,
    season_id,
    name,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
