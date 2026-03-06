# Consistency

Métricas de consistência treino → jogo.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**training_load_variability** | **number** | Desvio padrão da carga de treino | [default to undefined]
**game_performance_variability** | **number** | Desvio padrão da eficiência de jogo | [default to undefined]
**consistency_score** | **string** | Score qualitativo: \&#39;alta\&#39; | \&#39;média\&#39; | \&#39;baixa\&#39; | [default to undefined]

## Example

```typescript
import { Consistency } from './api';

const instance: Consistency = {
    training_load_variability,
    game_performance_variability,
    consistency_score,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
