# DashboardMatchStats

Estatísticas de jogos

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_matches** | **number** |  | [optional] [default to 0]
**wins** | **number** |  | [optional] [default to 0]
**draws** | **number** |  | [optional] [default to 0]
**losses** | **number** |  | [optional] [default to 0]
**goals_scored** | **number** |  | [optional] [default to 0]
**goals_conceded** | **number** |  | [optional] [default to 0]
**recent_matches** | [**Array&lt;DashboardRecentMatch&gt;**](DashboardRecentMatch.md) |  | [optional] [default to undefined]
**next_match** | [**DashboardNextMatch**](DashboardNextMatch.md) |  | [optional] [default to undefined]

## Example

```typescript
import { DashboardMatchStats } from './api';

const instance: DashboardMatchStats = {
    total_matches,
    wins,
    draws,
    losses,
    goals_scored,
    goals_conceded,
    recent_matches,
    next_match,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
