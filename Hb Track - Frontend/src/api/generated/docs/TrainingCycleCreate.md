# TrainingCycleCreate

Schema para criação de ciclo de treinamento.

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

## Example

```typescript
import { TrainingCycleCreate } from './api';

const instance: TrainingCycleCreate = {
    team_id,
    type,
    start_date,
    end_date,
    objective,
    notes,
    status,
    parent_cycle_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
