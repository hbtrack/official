# MatchSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**match_date** | **string** |  | [default to undefined]
**match_time** | **string** |  | [optional] [default to undefined]
**opponent_name** | **string** |  | [default to undefined]
**match_type** | [**MatchType**](MatchType.md) |  | [default to undefined]
**is_home** | **boolean** |  | [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**status** | [**AppModelsMatchMatchStatus**](AppModelsMatchMatchStatus.md) |  | [default to undefined]

## Example

```typescript
import { MatchSummary } from './api';

const instance: MatchSummary = {
    id,
    match_date,
    match_time,
    opponent_name,
    match_type,
    is_home,
    location,
    status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
