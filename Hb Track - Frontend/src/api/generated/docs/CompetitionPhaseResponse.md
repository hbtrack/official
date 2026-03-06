# CompetitionPhaseResponse

Schema de resposta para fase.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [default to undefined]
**competition_id** | **string** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**phase_type** | **string** |  | [default to undefined]
**order_index** | **number** |  | [default to undefined]
**is_olympic_cross** | **boolean** |  | [optional] [default to undefined]
**config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**status** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [optional] [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionPhaseResponse } from './api';

const instance: CompetitionPhaseResponse = {
    id,
    competition_id,
    name,
    phase_type,
    order_index,
    is_olympic_cross,
    config,
    status,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
