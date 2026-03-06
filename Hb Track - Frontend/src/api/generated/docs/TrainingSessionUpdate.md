# TrainingSessionUpdate

Payload para atualização de sessão de treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_at** | **string** |  | [optional] [default to undefined]
**session_type** | [**SessionTypeEnum**](SessionTypeEnum.md) |  | [optional] [default to undefined]
**main_objective** | **string** |  | [optional] [default to undefined]
**secondary_objective** | **string** |  | [optional] [default to undefined]
**planned_load** | **number** |  | [optional] [default to undefined]
**intensity_target** | **number** |  | [optional] [default to undefined]
**actual_load_avg** | **number** |  | [optional] [default to undefined]
**group_climate** | **number** |  | [optional] [default to undefined]
**duration_planned_minutes** | **number** |  | [optional] [default to undefined]
**duration_actual_minutes** | **number** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**highlight** | **string** |  | [optional] [default to undefined]
**next_corrections** | **string** |  | [optional] [default to undefined]
**execution_outcome** | [**TrainingExecutionOutcome**](TrainingExecutionOutcome.md) |  | [optional] [default to undefined]
**delay_minutes** | **number** |  | [optional] [default to undefined]
**cancellation_reason** | **string** |  | [optional] [default to undefined]
**deviation_justification** | **string** |  | [optional] [default to undefined]
**focus_attack_positional_pct** | [**FocusAttackPositionalPct**](FocusAttackPositionalPct.md) |  | [optional] [default to undefined]
**focus_defense_positional_pct** | [**FocusDefensePositionalPct**](FocusDefensePositionalPct.md) |  | [optional] [default to undefined]
**focus_transition_offense_pct** | [**FocusTransitionOffensePct**](FocusTransitionOffensePct.md) |  | [optional] [default to undefined]
**focus_transition_defense_pct** | [**FocusTransitionDefensePct**](FocusTransitionDefensePct.md) |  | [optional] [default to undefined]
**focus_attack_technical_pct** | [**FocusAttackTechnicalPct**](FocusAttackTechnicalPct.md) |  | [optional] [default to undefined]
**focus_defense_technical_pct** | [**FocusDefenseTechnicalPct**](FocusDefenseTechnicalPct.md) |  | [optional] [default to undefined]
**focus_physical_pct** | [**FocusPhysicalPct**](FocusPhysicalPct.md) |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingSessionUpdate } from './api';

const instance: TrainingSessionUpdate = {
    session_at,
    session_type,
    main_objective,
    secondary_objective,
    planned_load,
    intensity_target,
    actual_load_avg,
    group_climate,
    duration_planned_minutes,
    duration_actual_minutes,
    location,
    highlight,
    next_corrections,
    execution_outcome,
    delay_minutes,
    cancellation_reason,
    deviation_justification,
    focus_attack_positional_pct,
    focus_defense_positional_pct,
    focus_transition_offense_pct,
    focus_transition_defense_pct,
    focus_attack_technical_pct,
    focus_defense_technical_pct,
    focus_physical_pct,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
