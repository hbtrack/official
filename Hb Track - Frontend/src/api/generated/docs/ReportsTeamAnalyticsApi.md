# ReportsTeamAnalyticsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet**](#getteamtraininggamecorrelationapiv1reportsteamtraininggamecorrelationget) | **GET** /api/v1/reports/team-training-game-correlation | Correlação Treino → Jogo por Equipe|

# **getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet**
> TeamTrainingGameCorrelationResponse getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet()

Análise estratégica de correlação entre focos de treino e performance em jogos.          **Pergunta estratégica respondida:**     \"O que do treino está (ou não) se traduzindo em performance de jogo?\"          **Estrutura da resposta:**     - `context`: Contexto da análise (equipe, temporada, competição, período)     - `summary`: Resumo executivo (total de jogos/treinos, médias, força de correlação)     - `training_focus_distribution`: Distribuição dos 7 focos de treino (%)     - `content_translation`: Mapeamento treino → jogo por macroblock (attack/defense/physical)     - `load_vs_performance`: Scatter plot carga × eficiência     - `consistency`: Métricas de variabilidade treino/jogo     - `insights`: Arrays interpretativos (works/adjust/avoid)          **Referências RAG:**     - Especificação: eststisticas_equipes (2,199 linhas)     - RAG/IMPLEMENTACAO_FOCOS_TREINO.md     - R26: Permissões por papel (coordenador, treinador)     - Domínio: /statistics/teams (análise estratégica, não operacional)          **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes     - Dirigente: acesso às equipes da organização

### Example

```typescript
import {
    ReportsTeamAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsTeamAnalyticsApi(configuration);

let teamId: string; //ID da equipe (default to undefined)
let seasonId: string; //ID da temporada (default to undefined)
let competitionId: string; //ID da competição (opcional) (optional) (default to undefined)
let periodGames: number; //Número de jogos recentes a analisar (optional) (default to 5)
let trainingWindowDays: number; //Janela de treino pré-jogo (dias) (optional) (default to 7)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet(
    teamId,
    seasonId,
    competitionId,
    periodGames,
    trainingWindowDays,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe | defaults to undefined|
| **seasonId** | [**string**] | ID da temporada | defaults to undefined|
| **competitionId** | [**string**] | ID da competição (opcional) | (optional) defaults to undefined|
| **periodGames** | [**number**] | Número de jogos recentes a analisar | (optional) defaults to 5|
| **trainingWindowDays** | [**number**] | Janela de treino pré-jogo (dias) | (optional) defaults to 7|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamTrainingGameCorrelationResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

