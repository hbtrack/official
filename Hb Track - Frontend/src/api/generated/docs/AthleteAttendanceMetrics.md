# AthleteAttendanceMetrics

Métricas de presença (RP5)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_sessions** | **number** | Total de treinos | [default to undefined]
**sessions_presente** | **number** | Treinos presentes | [default to undefined]
**sessions_ausente** | **number** | Treinos ausentes (RP5: carga &#x3D; 0) | [default to undefined]
**sessions_dm** | **number** | Treinos em DM | [default to undefined]
**sessions_lesionada** | **number** | Treinos lesionada (R13) | [default to undefined]
**attendance_rate** | **number** | Taxa de assiduidade (%) | [default to undefined]

## Example

```typescript
import { AthleteAttendanceMetrics } from './api';

const instance: AthleteAttendanceMetrics = {
    total_sessions,
    sessions_presente,
    sessions_ausente,
    sessions_dm,
    sessions_lesionada,
    attendance_rate,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
