# AthleteIndividualReport

Relatório individual completo de atleta (R12, R13, R14)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** |  | [default to undefined]
**person_id** | **string** |  | [default to undefined]
**full_name** | **string** |  | [default to undefined]
**nickname** | **string** |  | [optional] [default to undefined]
**birth_date** | **string** |  | [optional] [default to undefined]
**position** | **string** |  | [optional] [default to undefined]
**current_age** | **number** |  | [optional] [default to undefined]
**expected_category_code** | **string** |  | [optional] [default to undefined]
**current_state** | **string** | Estado atual (R13: ativa, lesionada, dispensada) | [default to undefined]
**current_season_id** | **string** |  | [optional] [default to undefined]
**current_team_id** | **string** |  | [optional] [default to undefined]
**organization_id** | **string** |  | [default to undefined]
**readiness** | [**AthleteReadinessMetrics**](AthleteReadinessMetrics.md) |  | [default to undefined]
**training_load** | [**AthleteTrainingLoadMetrics**](AthleteTrainingLoadMetrics.md) |  | [default to undefined]
**attendance** | [**AthleteAttendanceMetrics**](AthleteAttendanceMetrics.md) |  | [default to undefined]
**wellness** | [**AthleteWellnessMetrics**](AthleteWellnessMetrics.md) |  | [default to undefined]
**active_medical_cases** | **number** | Casos médicos ativos (R13) | [default to undefined]
**last_session_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { AthleteIndividualReport } from './api';

const instance: AthleteIndividualReport = {
    athlete_id,
    person_id,
    full_name,
    nickname,
    birth_date,
    position,
    current_age,
    expected_category_code,
    current_state,
    current_season_id,
    current_team_id,
    organization_id,
    readiness,
    training_load,
    attendance,
    wellness,
    active_medical_cases,
    last_session_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
