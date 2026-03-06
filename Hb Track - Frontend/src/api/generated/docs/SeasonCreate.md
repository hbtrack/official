# SeasonCreate

Payload para criação de temporada (RF4).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** | Equipe dona da temporada | [default to undefined]
**year** | **number** | Ano da temporada (único) | [default to undefined]
**name** | **string** | Nome da temporada | [default to undefined]
**competition_type** | **string** |  | [optional] [default to undefined]
**start_date** | **string** | Data de início | [default to undefined]
**end_date** | **string** | Data de término | [default to undefined]

## Example

```typescript
import { SeasonCreate } from './api';

const instance: SeasonCreate = {
    team_id,
    year,
    name,
    competition_type,
    start_date,
    end_date,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
