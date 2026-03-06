# CorrelationSummary

Resumo executivo da correlação.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_games** | **number** | Total de jogos analisados | [default to undefined]
**total_training_sessions** | **number** | Total de treinos na janela | [default to undefined]
**avg_training_load** | **number** | Carga média de treino (0-10) | [default to undefined]
**avg_game_efficiency** | **number** | Eficiência média em jogos (%) | [default to undefined]
**correlation_strength** | **string** | Força da correlação: \&#39;forte\&#39; | \&#39;moderada\&#39; | \&#39;fraca\&#39; | \&#39;insuficiente\&#39; | [default to undefined]

## Example

```typescript
import { CorrelationSummary } from './api';

const instance: CorrelationSummary = {
    total_games,
    total_training_sessions,
    avg_training_load,
    avg_game_efficiency,
    correlation_strength,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
