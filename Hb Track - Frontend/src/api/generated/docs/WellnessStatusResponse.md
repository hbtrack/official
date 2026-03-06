# WellnessStatusResponse

Resposta completa do endpoint wellness-status.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athletes** | [**Array&lt;WellnessAthleteData&gt;**](WellnessAthleteData.md) | Lista de atletas com status | [default to undefined]
**stats** | [**WellnessSessionStats**](WellnessSessionStats.md) | Estatísticas agregadas | [default to undefined]

## Example

```typescript
import { WellnessStatusResponse } from './api';

const instance: WellnessStatusResponse = {
    athletes,
    stats,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
