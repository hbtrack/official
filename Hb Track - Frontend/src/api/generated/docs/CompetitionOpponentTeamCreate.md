# CompetitionOpponentTeamCreate

Schema para criação de equipe adversária.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**short_name** | **string** |  | [optional] [default to undefined]
**category** | **string** |  | [optional] [default to undefined]
**city** | **string** |  | [optional] [default to undefined]
**logo_url** | **string** |  | [optional] [default to undefined]
**linked_team_id** | **string** |  | [optional] [default to undefined]
**group_name** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionOpponentTeamCreate } from './api';

const instance: CompetitionOpponentTeamCreate = {
    name,
    short_name,
    category,
    city,
    logo_url,
    linked_team_id,
    group_name,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
