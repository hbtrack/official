# WellnessSummaryReport

Relatório de resumo de bem-estar (RP6, RP7, RP8)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **string** |  | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**start_date** | **string** |  | [default to undefined]
**end_date** | **string** |  | [default to undefined]
**metrics** | [**WellnessSummaryMetrics**](WellnessSummaryMetrics.md) |  | [default to undefined]

## Example

```typescript
import { WellnessSummaryReport } from './api';

const instance: WellnessSummaryReport = {
    organization_id,
    season_id,
    team_id,
    start_date,
    end_date,
    metrics,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
