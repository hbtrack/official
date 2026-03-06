# TrainingSession

Resposta completa de sessão de treino.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **string** | ID da organização | [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**created_by_user_id** | **string** |  | [optional] [default to undefined]
**session_at** | **string** | Data/hora da sessão de treino | [default to undefined]
**session_type** | [**SessionTypeEnum**](SessionTypeEnum.md) | Tipo de sessão: quadra, fisico, video, reuniao, teste | [default to undefined]
**main_objective** | **string** |  | [optional] [default to undefined]
**secondary_objective** | **string** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]
**planned_load** | **number** |  | [optional] [default to undefined]
**group_climate** | **number** |  | [optional] [default to undefined]
**intensity_target** | **number** |  | [optional] [default to undefined]
**duration_planned_minutes** | **number** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**id** | **string** | ID da sessão de treino | [default to undefined]
**status** | **string** | Estado: draft, scheduled, in_progress, pending_review, readonly | [default to undefined]
**started_at** | **string** |  | [optional] [default to undefined]
**ended_at** | **string** |  | [optional] [default to undefined]
**duration_actual_minutes** | **number** |  | [optional] [default to undefined]
**execution_outcome** | [**TrainingExecutionOutcome**](TrainingExecutionOutcome.md) | Resultado da execução real (on_time, delayed, canceled, shortened, extended) | [default to undefined]
**delay_minutes** | **number** |  | [optional] [default to undefined]
**cancellation_reason** | **string** |  | [optional] [default to undefined]
**post_review_completed_at** | **string** |  | [optional] [default to undefined]
**post_review_completed_by_user_id** | **string** |  | [optional] [default to undefined]
**post_review_deadline_at** | **string** |  | [optional] [default to undefined]
**closed_at** | **string** |  | [optional] [default to undefined]
**closed_by_user_id** | **string** |  | [optional] [default to undefined]
**exercises_count** | **number** |  | [optional] [default to undefined]
**attendance_present_count** | **number** |  | [optional] [default to undefined]
**attendance_total_count** | **number** |  | [optional] [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]
**deleted_at** | **string** |  | [optional] [default to undefined]
**deleted_reason** | **string** |  | [optional] [default to undefined]
**focus_attack_positional_pct** | **string** |  | [optional] [default to undefined]
**focus_defense_positional_pct** | **string** |  | [optional] [default to undefined]
**focus_transition_offense_pct** | **string** |  | [optional] [default to undefined]
**focus_transition_defense_pct** | **string** |  | [optional] [default to undefined]
**focus_attack_technical_pct** | **string** |  | [optional] [default to undefined]
**focus_defense_technical_pct** | **string** |  | [optional] [default to undefined]
**focus_physical_pct** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TrainingSession } from './api';

const instance: TrainingSession = {
    organization_id,
    team_id,
    season_id,
    created_by_user_id,
    session_at,
    session_type,
    main_objective,
    secondary_objective,
    notes,
    planned_load,
    group_climate,
    intensity_target,
    duration_planned_minutes,
    location,
    id,
    status,
    started_at,
    ended_at,
    duration_actual_minutes,
    execution_outcome,
    delay_minutes,
    cancellation_reason,
    post_review_completed_at,
    post_review_completed_by_user_id,
    post_review_deadline_at,
    closed_at,
    closed_by_user_id,
    exercises_count,
    attendance_present_count,
    attendance_total_count,
    created_at,
    updated_at,
    deleted_at,
    deleted_reason,
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
