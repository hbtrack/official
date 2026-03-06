# TrainingCycleWithMicrocycles

Schema de resposta com microciclos incluídos.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** | ID da equipe | [default to undefined]
**type** | **string** | Tipo: \&#39;macro\&#39; ou \&#39;meso\&#39; | [default to undefined]
**start_date** | **string** | Data de início do ciclo | [default to undefined]
**end_date** | **string** | Data de término do ciclo | [default to undefined]
**objective** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**status** | **string** | Status: active, completed, cancelled | [optional] [default to 'active']
**parent_cycle_id** | **string** |  | [optional] [default to undefined]
**id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**created_by_user_id** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]
**microcycles** | [**Array&lt;TrainingMicrocycleResponse&gt;**](TrainingMicrocycleResponse.md) |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingCycleWithMicrocycles } from './api';

const instance: TrainingCycleWithMicrocycles = {
    team_id,
    type,
    start_date,
    end_date,
    objective,
    notes,
    status,
    parent_cycle_id,
    id,
    organization_id,
    created_by_user_id,
    created_at,
    updated_at,
    deleted_at,
    microcycles,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
