# TrainingMicrocycleUpdate

Schema para atualização de microciclo de treinamento.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**planned_focus_attack_positional_pct** | [**PlannedFocusAttackPositionalPct1**](PlannedFocusAttackPositionalPct1.md) |  | [optional] [default to undefined]
**planned_focus_defense_positional_pct** | [**PlannedFocusDefensePositionalPct1**](PlannedFocusDefensePositionalPct1.md) |  | [optional] [default to undefined]
**planned_focus_transition_offense_pct** | [**PlannedFocusTransitionOffensePct1**](PlannedFocusTransitionOffensePct1.md) |  | [optional] [default to undefined]
**planned_focus_transition_defense_pct** | [**PlannedFocusTransitionDefensePct1**](PlannedFocusTransitionDefensePct1.md) |  | [optional] [default to undefined]
**planned_focus_attack_technical_pct** | [**PlannedFocusAttackTechnicalPct1**](PlannedFocusAttackTechnicalPct1.md) |  | [optional] [default to undefined]
**planned_focus_defense_technical_pct** | [**PlannedFocusDefenseTechnicalPct1**](PlannedFocusDefenseTechnicalPct1.md) |  | [optional] [default to undefined]
**planned_focus_physical_pct** | [**PlannedFocusPhysicalPct1**](PlannedFocusPhysicalPct1.md) |  | [optional] [default to undefined]
**planned_weekly_load** | **number** |  | [optional] [default to undefined]
**microcycle_type** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingMicrocycleUpdate } from './api';

const instance: TrainingMicrocycleUpdate = {
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
