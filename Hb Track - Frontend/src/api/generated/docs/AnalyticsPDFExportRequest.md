# AnalyticsPDFExportRequest

Request to export analytics as PDF

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [default to undefined]
**start_date** | **string** | Start date for analytics period | [default to undefined]
**end_date** | **string** | End date for analytics period | [default to undefined]
**include_wellness** | **boolean** | Include wellness metrics | [optional] [default to true]
**include_badges** | **boolean** | Include badges and rankings | [optional] [default to true]
**include_prevention** | **boolean** | Include prevention effectiveness | [optional] [default to true]

## Example

```typescript
import { AnalyticsPDFExportRequest } from './api';

const instance: AnalyticsPDFExportRequest = {
    team_id,
    start_date,
    end_date,
    include_wellness,
    include_badges,
    include_prevention,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
