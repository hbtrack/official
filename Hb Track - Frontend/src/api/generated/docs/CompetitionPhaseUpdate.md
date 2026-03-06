# CompetitionPhaseUpdate

Schema para atualização de fase.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**phase_type** | [**PhaseType**](PhaseType.md) |  | [optional] [default to undefined]
**order_index** | **number** |  | [optional] [default to undefined]
**is_olympic_cross** | **boolean** |  | [optional] [default to undefined]
**config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**status** | [**PhaseStatus**](PhaseStatus.md) |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionPhaseUpdate } from './api';

const instance: CompetitionPhaseUpdate = {
    name,
    phase_type,
    order_index,
    is_olympic_cross,
    config,
    status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
