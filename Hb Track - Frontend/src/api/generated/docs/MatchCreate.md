# MatchCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**match_date** | **string** | Data da partida | [default to undefined]
**opponent_name** | **string** |  | [optional] [default to undefined]
**match_type** | [**MatchType**](MatchType.md) | Tipo/fase da partida | [optional] [default to undefined]
**is_home** | **boolean** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**team_id** | **string** | ID do time (our_team_id) | [default to undefined]

## Example

```typescript
import { MatchCreate } from './api';

const instance: MatchCreate = {
    match_date,
    opponent_name,
    match_type,
    is_home,
    location,
    team_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
