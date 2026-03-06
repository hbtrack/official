# CompetitionV2Create

Schema para criação de competição V2 (POST). Suporta todos os novos campos do módulo de IA.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Nome da competição | [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**season** | **string** |  | [optional] [default to undefined]
**modality** | [**Modality**](Modality.md) |  | [optional] [default to undefined]
**kind** | **string** |  | [optional] [default to undefined]
**competition_type** | [**CompetitionType**](CompetitionType.md) |  | [optional] [default to undefined]
**format_details** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**tiebreaker_criteria** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**points_per_win** | **number** |  | [optional] [default to undefined]
**regulation_file_url** | **string** |  | [optional] [default to undefined]
**regulation_notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionV2Create } from './api';

const instance: CompetitionV2Create = {
    name,
    team_id,
    season,
    modality,
    kind,
    competition_type,
    format_details,
    tiebreaker_criteria,
    points_per_win,
    regulation_file_url,
    regulation_notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
