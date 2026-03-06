# TrainingMicrocycleResponse

Schema de resposta para microciclo de treinamento.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** | ID da equipe | [default to undefined]
**week_start** | **string** | Início da semana (segunda) | [default to undefined]
**week_end** | **string** | Fim da semana (domingo) | [default to undefined]
**cycle_id** | **string** |  | [optional] [default to undefined]
**planned_focus_attack_positional_pct** | **string** |  | [optional] [default to undefined]
**planned_focus_defense_positional_pct** | **string** |  | [optional] [default to undefined]
**planned_focus_transition_offense_pct** | **string** |  | [optional] [default to undefined]
**planned_focus_transition_defense_pct** | **string** |  | [optional] [default to undefined]
**planned_focus_attack_technical_pct** | **string** |  | [optional] [default to undefined]
**planned_focus_defense_technical_pct** | **string** |  | [optional] [default to undefined]
**planned_focus_physical_pct** | **string** |  | [optional] [default to undefined]
**planned_weekly_load** | **number** |  | [optional] [default to undefined]
**microcycle_type** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**id** | **string** |  | [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**created_by_user_id** | **string** |  | [default to undefined]
**created_at** | **string** |  | [default to undefined]
**updated_at** | **string** |  | [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingMicrocycleResponse } from './api';

const instance: TrainingMicrocycleResponse = {
    team_id,
    week_start,
    week_end,
    cycle_id,
    planned_focus_attack_positional_pct,
    planned_focus_defense_positional_pct,
    planned_focus_transition_offense_pct,
    planned_focus_transition_defense_pct,
    planned_focus_attack_technical_pct,
    planned_focus_defense_technical_pct,
    planned_focus_physical_pct,
    planned_weekly_load,
    microcycle_type,
    notes,
    id,
    organization_id,
    created_by_user_id,
    created_at,
    updated_at,
    deleted_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
