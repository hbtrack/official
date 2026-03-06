# TrainingMicrocycleCreate

Schema para criação de microciclo de treinamento.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** | ID da equipe | [default to undefined]
**week_start** | **string** | Início da semana (segunda) | [default to undefined]
**week_end** | **string** | Fim da semana (domingo) | [default to undefined]
**cycle_id** | **string** |  | [optional] [default to undefined]
**planned_focus_attack_positional_pct** | [**PlannedFocusAttackPositionalPct**](PlannedFocusAttackPositionalPct.md) |  | [optional] [default to undefined]
**planned_focus_defense_positional_pct** | [**PlannedFocusDefensePositionalPct**](PlannedFocusDefensePositionalPct.md) |  | [optional] [default to undefined]
**planned_focus_transition_offense_pct** | [**PlannedFocusTransitionOffensePct**](PlannedFocusTransitionOffensePct.md) |  | [optional] [default to undefined]
**planned_focus_transition_defense_pct** | [**PlannedFocusTransitionDefensePct**](PlannedFocusTransitionDefensePct.md) |  | [optional] [default to undefined]
**planned_focus_attack_technical_pct** | [**PlannedFocusAttackTechnicalPct**](PlannedFocusAttackTechnicalPct.md) |  | [optional] [default to undefined]
**planned_focus_defense_technical_pct** | [**PlannedFocusDefenseTechnicalPct**](PlannedFocusDefenseTechnicalPct.md) |  | [optional] [default to undefined]
**planned_focus_physical_pct** | [**PlannedFocusPhysicalPct**](PlannedFocusPhysicalPct.md) |  | [optional] [default to undefined]
**planned_weekly_load** | **number** |  | [optional] [default to undefined]
**microcycle_type** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingMicrocycleCreate } from './api';

const instance: TrainingMicrocycleCreate = {
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
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
