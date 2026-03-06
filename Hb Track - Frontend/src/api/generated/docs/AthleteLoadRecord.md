# AthleteLoadRecord

Registro de carga por atleta.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** |  | [default to undefined]
**athlete_name** | **string** |  | [default to undefined]
**training_load_total** | **number** | Carga total de treinos (RPE × minutos) | [default to undefined]
**training_sessions_count** | **number** | Número de treinos com carga registrada | [default to undefined]
**training_load_avg** | **number** | Carga média por treino | [default to undefined]
**match_load_total** | **number** | Carga total de jogos (minutos) | [default to undefined]
**matches_count** | **number** | Número de jogos | [default to undefined]
**match_load_avg** | **number** | Carga média por jogo | [default to undefined]
**total_load** | **number** | Carga total (treino + jogo) | [default to undefined]
**avg_daily_load** | **number** | Carga média diária no período | [default to undefined]
**is_overloaded** | **boolean** | Acima do limiar de sobrecarga | [optional] [default to false]
**load_trend** | **string** | Tendência: increasing, decreasing, stable | [optional] [default to 'stable']

## Example

```typescript
import { AthleteLoadRecord } from './api';

const instance: AthleteLoadRecord = {
    athlete_id,
    athlete_name,
    training_load_total,
    training_sessions_count,
    training_load_avg,
    match_load_total,
    matches_count,
    match_load_avg,
    total_load,
    avg_daily_load,
    is_overloaded,
    load_trend,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
