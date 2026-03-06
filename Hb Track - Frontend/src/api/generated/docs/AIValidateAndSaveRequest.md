# AIValidateAndSaveRequest

Request para validar e salvar dados extraídos pela IA.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extracted_data** | [**AIExtractedCompetitionInput**](AIExtractedCompetitionInput.md) |  | [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**auto_link_teams** | **boolean** | Tentar vincular equipes automaticamente via fuzzy search | [optional] [default to true]

## Example

```typescript
import { AIValidateAndSaveRequest } from './api';

const instance: AIValidateAndSaveRequest = {
    extracted_data,
    team_id,
    auto_link_teams,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
