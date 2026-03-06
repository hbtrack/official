# CompetitionPhaseCreate

Schema para criação de fase.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**phase_type** | [**PhaseType**](PhaseType.md) |  | [default to undefined]
**order_index** | **number** |  | [optional] [default to 0]
**is_olympic_cross** | **boolean** |  | [optional] [default to false]
**config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionPhaseCreate } from './api';

const instance: CompetitionPhaseCreate = {
    name,
    phase_type,
    order_index,
    is_olympic_cross,
    config,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
