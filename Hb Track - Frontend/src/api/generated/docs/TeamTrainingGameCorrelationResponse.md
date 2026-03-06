# TeamTrainingGameCorrelationResponse

Resposta completa do endpoint /reports/team-training-game-correlation.  Estrutura canônica conforme eststisticas_equipes (linhas 1785-1918). Backend entrega dados interpretados; frontend apenas renderiza.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | [**CorrelationContext**](CorrelationContext.md) | Contexto da análise (equipe, temporada, período) | [default to undefined]
**summary** | [**CorrelationSummary**](CorrelationSummary.md) | Resumo executivo da correlação | [default to undefined]
**training_focus_distribution** | [**TrainingFocusDistribution**](TrainingFocusDistribution.md) | Distribuição dos 7 focos de treino (%) | [default to undefined]
**content_translation** | [**{ [key: string]: ContentTranslationMacro; }**](ContentTranslationMacro.md) | Mapeamento treino → jogo por macroblock (attack/defense/physical) | [default to undefined]
**load_vs_performance** | [**LoadVsPerformance**](LoadVsPerformance.md) | Scatter plot carga × eficiência | [default to undefined]
**consistency** | [**Consistency**](Consistency.md) | Métricas de consistência | [default to undefined]
**insights** | [**Insights**](Insights.md) | Insights interpretativos (works/adjust/avoid) | [default to undefined]

## Example

```typescript
import { TeamTrainingGameCorrelationResponse } from './api';

const instance: TeamTrainingGameCorrelationResponse = {
    context,
    summary,
    training_focus_distribution,
    content_translation,
    load_vs_performance,
    consistency,
    insights,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
