# TrainingSessionCreate

Payload para criação de sessão de treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **string** | ID da organização | [default to undefined]
**team_id** | **string** | ID do time | [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**session_at** | **string** | Data/hora da sessão de treino | [default to undefined]
**session_type** | [**SessionTypeEnum**](SessionTypeEnum.md) | Tipo de sessão: quadra, fisico, video, reuniao, teste | [optional] [default to undefined]
**main_objective** | **string** |  | [optional] [default to undefined]
**duration_planned_minutes** | **number** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**planned_load** | **number** |  | [optional] [default to undefined]
**group_climate** | **number** |  | [optional] [default to undefined]
**intensity_target** | **number** |  | [optional] [default to undefined]
**highlight** | **string** |  | [optional] [default to undefined]
**next_corrections** | **string** |  | [optional] [default to undefined]
**microcycle_id** | **string** |  | [optional] [default to undefined]
**focus_attack_positional_pct** | [**FocusAttackPositionalPct**](FocusAttackPositionalPct.md) |  | [optional] [default to undefined]
**focus_defense_positional_pct** | [**FocusDefensePositionalPct**](FocusDefensePositionalPct.md) |  | [optional] [default to undefined]
**focus_transition_offense_pct** | [**FocusTransitionOffensePct**](FocusTransitionOffensePct.md) |  | [optional] [default to undefined]
**focus_transition_defense_pct** | [**FocusTransitionDefensePct**](FocusTransitionDefensePct.md) |  | [optional] [default to undefined]
**focus_attack_technical_pct** | [**FocusAttackTechnicalPct**](FocusAttackTechnicalPct.md) |  | [optional] [default to undefined]
**focus_defense_technical_pct** | [**FocusDefenseTechnicalPct**](FocusDefenseTechnicalPct.md) |  | [optional] [default to undefined]
**focus_physical_pct** | [**FocusPhysicalPct**](FocusPhysicalPct.md) |  | [optional] [default to undefined]
**deviation_justification** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingSessionCreate } from './api';

const instance: TrainingSessionCreate = {
    organization_id,
    team_id,
    season_id,
    session_at,
    session_type,
    main_objective,
    duration_planned_minutes,
    location,
    notes,
    planned_load,
    group_climate,
    intensity_target,
    highlight,
    next_corrections,
    microcycle_id,
    focus_attack_positional_pct,
    focus_defense_positional_pct,
    focus_transition_offense_pct,
    focus_transition_defense_pct,
    focus_attack_technical_pct,
    focus_defense_technical_pct,
    focus_physical_pct,
    deviation_justification,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
