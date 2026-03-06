# AIExtractedCompetitionInput

Dados completos extraídos pelo Gemini de um PDF de regulamento. Este é o formato retornado pela IA para validação do usuário.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**season** | **string** |  | [optional] [default to undefined]
**modality** | **string** |  | [optional] [default to undefined]
**competition_type** | **string** |  | [optional] [default to undefined]
**format_details** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**tiebreaker_criteria** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**points_per_win** | **number** |  | [optional] [default to undefined]
**regulation_notes** | **string** |  | [optional] [default to undefined]
**phases** | [**Array&lt;AIExtractedPhase&gt;**](AIExtractedPhase.md) |  | [optional] [default to undefined]
**teams** | [**Array&lt;AIExtractedTeam&gt;**](AIExtractedTeam.md) |  | [optional] [default to undefined]
**matches** | [**Array&lt;AIExtractedMatch&gt;**](AIExtractedMatch.md) |  | [optional] [default to undefined]
**overall_confidence_score** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { AIExtractedCompetitionInput } from './api';

const instance: AIExtractedCompetitionInput = {
    name,
    season,
    modality,
    competition_type,
    format_details,
    tiebreaker_criteria,
    points_per_win,
    regulation_notes,
    phases,
    teams,
    matches,
    overall_confidence_score,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
