# TrainingPerformanceReport

Relatório completo de performance de treino (R18, R22)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**session_at** | **string** |  | [default to undefined]
**main_objective** | **string** |  | [optional] [default to undefined]
**planned_load** | **number** |  | [optional] [default to undefined]
**group_climate** | **number** |  | [optional] [default to undefined]
**metrics** | [**TrainingPerformanceMetrics**](TrainingPerformanceMetrics.md) |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]

## Example

```typescript
import { TrainingPerformanceReport } from './api';

const instance: TrainingPerformanceReport = {
    session_id,
    organization_id,
    season_id,
    team_id,
    session_at,
    main_objective,
    planned_load,
    group_climate,
    metrics,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
