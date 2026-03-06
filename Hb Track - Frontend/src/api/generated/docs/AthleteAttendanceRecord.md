# AthleteAttendanceRecord

Registro de assiduidade por atleta.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** |  | [default to undefined]
**athlete_name** | **string** |  | [default to undefined]
**total_training_sessions** | **number** | Total de treinos no período | [default to undefined]
**training_sessions_present** | **number** | Treinos presentes | [default to undefined]
**training_sessions_absent** | **number** | Treinos ausentes | [default to undefined]
**training_attendance_rate** | **number** | Taxa de presença em treinos (%) | [default to undefined]
**total_matches** | **number** | Total de jogos no período | [default to undefined]
**matches_played** | **number** | Jogos jogados | [default to undefined]
**matches_not_played** | **number** | Jogos não jogados (roster mas não jogou) | [default to undefined]
**match_participation_rate** | **number** | Taxa de participação em jogos (%) | [default to undefined]
**combined_attendance_rate** | **number** | Taxa de assiduidade combinada (%) | [default to undefined]

## Example

```typescript
import { AthleteAttendanceRecord } from './api';

const instance: AthleteAttendanceRecord = {
    athlete_id,
    athlete_name,
    total_training_sessions,
    training_sessions_present,
    training_sessions_absent,
    training_attendance_rate,
    total_matches,
    matches_played,
    matches_not_played,
    match_participation_rate,
    combined_attendance_rate,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
