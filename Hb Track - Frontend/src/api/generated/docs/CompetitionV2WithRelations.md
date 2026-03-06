# CompetitionV2WithRelations

Competition V2 com relacionamentos expandidos.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**kind** | **string** |  | [optional] [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**season** | **string** |  | [optional] [default to undefined]
**modality** | **string** |  | [optional] [default to undefined]
**competition_type** | **string** |  | [optional] [default to undefined]
**format_details** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**tiebreaker_criteria** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**points_per_win** | **number** |  | [optional] [default to undefined]
**status** | **string** |  | [optional] [default to undefined]
**current_phase_id** | **string** |  | [optional] [default to undefined]
**regulation_file_url** | **string** |  | [optional] [default to undefined]
**regulation_notes** | **string** |  | [optional] [default to undefined]
**created_by** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]
**phases** | [**Array&lt;CompetitionPhaseResponse&gt;**](CompetitionPhaseResponse.md) |  | [optional] [default to undefined]
**opponent_teams** | [**Array&lt;CompetitionOpponentTeamResponse&gt;**](CompetitionOpponentTeamResponse.md) |  | [optional] [default to undefined]
**matches_count** | **number** |  | [optional] [default to undefined]
**our_matches_count** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionV2WithRelations } from './api';

const instance: CompetitionV2WithRelations = {
    id,
    organization_id,
    name,
    kind,
    team_id,
    season,
    modality,
    competition_type,
    format_details,
    tiebreaker_criteria,
    points_per_win,
    status,
    current_phase_id,
    regulation_file_url,
    regulation_notes,
    created_by,
    created_at,
    updated_at,
    deleted_at,
    phases,
    opponent_teams,
    matches_count,
    our_matches_count,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
