# CorrelationContext

Contexto da análise de correlação.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** | ID da equipe analisada | [default to undefined]
**team_name** | **string** | Nome da equipe | [default to undefined]
**season_id** | **string** | ID da temporada | [default to undefined]
**season_name** | **string** | Nome da temporada | [default to undefined]
**competition_id** | **string** |  | [optional] [default to undefined]
**competition_name** | **string** |  | [optional] [default to undefined]
**period** | **string** | Período analisado (ex: \&#39;últimos 5 jogos\&#39;) | [default to undefined]
**training_window_days** | **number** | Janela de treino pré-jogo (dias) | [default to undefined]
**analysis_date** | **string** | Data da análise | [default to undefined]

## Example

```typescript
import { CorrelationContext } from './api';

const instance: CorrelationContext = {
    team_id,
    team_name,
    season_id,
    season_name,
    competition_id,
    competition_name,
    period,
    training_window_days,
    analysis_date,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
