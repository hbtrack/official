# CompetitionMatchResultUpdate

Schema específico para atualização de resultado.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**home_score** | **number** |  | [default to undefined]
**away_score** | **number** |  | [default to undefined]
**home_score_extra** | **number** |  | [optional] [default to undefined]
**away_score_extra** | **number** |  | [optional] [default to undefined]
**home_score_penalties** | **number** |  | [optional] [default to undefined]
**away_score_penalties** | **number** |  | [optional] [default to undefined]
**status** | [**AppSchemasCompetitionsV2MatchStatus**](AppSchemasCompetitionsV2MatchStatus.md) |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionMatchResultUpdate } from './api';

const instance: CompetitionMatchResultUpdate = {
    home_score,
    away_score,
    home_score_extra,
    away_score_extra,
    home_score_penalties,
    away_score_penalties,
    status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
