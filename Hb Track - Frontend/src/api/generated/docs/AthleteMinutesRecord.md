# AthleteMinutesRecord

Registro de minutos jogados por atleta.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** |  | [default to undefined]
**athlete_name** | **string** |  | [default to undefined]
**total_matches** | **number** | Total de jogos convocado | [default to undefined]
**matches_played** | **number** | Jogos em que efetivamente jogou | [default to undefined]
**matches_started** | **number** | Jogos em que foi titular | [default to undefined]
**total_minutes_played** | **number** | Total de minutos jogados | [default to undefined]
**avg_minutes_per_match** | **number** | Média de minutos por jogo jogado | [default to undefined]
**total_training_sessions** | **number** | Total de treinos presentes | [default to undefined]
**total_training_minutes** | **number** | Minutos efetivos de treino | [default to undefined]
**avg_training_minutes** | **number** | Média de minutos por treino | [default to undefined]
**total_activity_minutes** | **number** | Total de minutos (jogo + treino) | [default to undefined]

## Example

```typescript
import { AthleteMinutesRecord } from './api';

const instance: AthleteMinutesRecord = {
    athlete_id,
    athlete_name,
    total_matches,
    matches_played,
    matches_started,
    total_minutes_played,
    avg_minutes_per_match,
    total_training_sessions,
    total_training_minutes,
    avg_training_minutes,
    total_activity_minutes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
