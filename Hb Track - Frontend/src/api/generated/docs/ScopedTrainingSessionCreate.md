# ScopedTrainingSessionCreate

Payload para criação de sessão de treino em rotas scoped (organization_id inferido do team).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **string** |  | [optional] [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**session_at** | **string** | Data/hora da sessão de treino | [default to undefined]
**session_type** | [**SessionTypeEnum**](SessionTypeEnum.md) | Tipo de sessão: quadra, fisico, video, reuniao, teste | [optional] [default to undefined]
**main_objective** | **string** |  | [optional] [default to undefined]
**planned_load** | **number** |  | [optional] [default to undefined]
**group_climate** | **number** |  | [optional] [default to undefined]
**highlight** | **string** |  | [optional] [default to undefined]
**next_corrections** | **string** |  | [optional] [default to undefined]
**focus_attack_positional_pct** | [**FocusAttackPositionalPct**](FocusAttackPositionalPct.md) |  | [optional] [default to undefined]
**focus_defense_positional_pct** | [**FocusDefensePositionalPct**](FocusDefensePositionalPct.md) |  | [optional] [default to undefined]
**focus_transition_offense_pct** | [**FocusTransitionOffensePct**](FocusTransitionOffensePct.md) |  | [optional] [default to undefined]
**focus_transition_defense_pct** | [**FocusTransitionDefensePct**](FocusTransitionDefensePct.md) |  | [optional] [default to undefined]
**focus_attack_technical_pct** | [**FocusAttackTechnicalPct**](FocusAttackTechnicalPct.md) |  | [optional] [default to undefined]
**focus_defense_technical_pct** | [**FocusDefenseTechnicalPct**](FocusDefenseTechnicalPct.md) |  | [optional] [default to undefined]
**focus_physical_pct** | [**FocusPhysicalPct**](FocusPhysicalPct.md) |  | [optional] [default to undefined]

## Example

```typescript
import { ScopedTrainingSessionCreate } from './api';

const instance: ScopedTrainingSessionCreate = {
    organization_id,
    season_id,
    session_at,
    session_type,
    main_objective,
    planned_load,
    group_climate,
    highlight,
    next_corrections,
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
