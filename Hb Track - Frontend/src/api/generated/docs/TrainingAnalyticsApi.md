# TrainingAnalyticsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet**](#getdeviationanalysisapiv1analyticsteamteamiddeviationanalysisget) | **GET** /api/v1/analytics/team/{team_id}/deviation-analysis | Análise de desvios com threshold dinâmico|
|[**getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet_0**](#getdeviationanalysisapiv1analyticsteamteamiddeviationanalysisget_0) | **GET** /api/v1/analytics/team/{team_id}/deviation-analysis | Análise de desvios com threshold dinâmico|
|[**getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet**](#getpreventioneffectivenessapiv1analyticsteamteamidpreventioneffectivenessget) | **GET** /api/v1/analytics/team/{team_id}/prevention-effectiveness | Eficácia Preventiva - Correlação Alertas→Sugestões→Lesões|
|[**getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet_0**](#getpreventioneffectivenessapiv1analyticsteamteamidpreventioneffectivenessget_0) | **GET** /api/v1/analytics/team/{team_id}/prevention-effectiveness | Eficácia Preventiva - Correlação Alertas→Sugestões→Lesões|
|[**getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet**](#getteamsummaryapiv1analyticsteamteamidsummaryget) | **GET** /api/v1/analytics/team/{team_id}/summary | Métricas agregadas da equipe|
|[**getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet_0**](#getteamsummaryapiv1analyticsteamteamidsummaryget_0) | **GET** /api/v1/analytics/team/{team_id}/summary | Métricas agregadas da equipe|
|[**getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet**](#getweeklyloadapiv1analyticsteamteamidweeklyloadget) | **GET** /api/v1/analytics/team/{team_id}/weekly-load | Carga semanal das últimas N semanas|
|[**getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet_0**](#getweeklyloadapiv1analyticsteamteamidweeklyloadget_0) | **GET** /api/v1/analytics/team/{team_id}/weekly-load | Carga semanal das últimas N semanas|

# **getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet**
> DeviationAnalysisResponse getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet()

Análise de desvios usando `alert_threshold_multiplier` da equipe.  **Como funciona:** 1. Busca configuração `team.alert_threshold_multiplier` (Step 15) 2. Para cada sessão: `desvio = |RPE_real - RPE_planejado| × multiplier` 3. Lista sessões onde `desvio > multiplier`  **Interpretação:** - `threshold_multiplier = 1.5`: Sensível (juvenis) - `threshold_multiplier = 2.0`: Padrão - `threshold_multiplier = 2.5-3.0`: Tolerante (atletas experientes)  **Métricas retornadas:** - Total de sessões analisadas - Quantidade de desvios detectados - Lista detalhada de cada desvio  **Permissões:** - Requer: `view_training_analytics`

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let startDate: string; //Data início (default: início do mês) (optional) (default to undefined)
let endDate: string; //Data fim (default: hoje) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet(
    teamId,
    startDate,
    endDate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **startDate** | [**string**] | Data início (default: início do mês) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data fim (default: hoje) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DeviationAnalysisResponse**

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

# **getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet_0**
> DeviationAnalysisResponse getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet_0()

Análise de desvios usando `alert_threshold_multiplier` da equipe.  **Como funciona:** 1. Busca configuração `team.alert_threshold_multiplier` (Step 15) 2. Para cada sessão: `desvio = |RPE_real - RPE_planejado| × multiplier` 3. Lista sessões onde `desvio > multiplier`  **Interpretação:** - `threshold_multiplier = 1.5`: Sensível (juvenis) - `threshold_multiplier = 2.0`: Padrão - `threshold_multiplier = 2.5-3.0`: Tolerante (atletas experientes)  **Métricas retornadas:** - Total de sessões analisadas - Quantidade de desvios detectados - Lista detalhada de cada desvio  **Permissões:** - Requer: `view_training_analytics`

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let startDate: string; //Data início (default: início do mês) (optional) (default to undefined)
let endDate: string; //Data fim (default: hoje) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDeviationAnalysisApiV1AnalyticsTeamTeamIdDeviationAnalysisGet_0(
    teamId,
    startDate,
    endDate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **startDate** | [**string**] | Data início (default: início do mês) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data fim (default: hoje) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DeviationAnalysisResponse**

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

# **getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet**
> any getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet()

Dashboard de Eficácia Preventiva (Step 22)  Analisa a correlação entre alertas, sugestões e lesões para avaliar se as ações preventivas estão funcionando.  **Lógica:** 1. Busca alertas do período 2. Identifica sugestões geradas por cada alerta 3. Verifica se sugestões foram aplicadas ou rejeitadas 4. Conta lesões em janela de +7 dias após ação 5. Compara taxa de lesões: com sugestão aplicada vs recusada  **Retorna:** - `summary`: Estatísticas gerais (alertas, sugestões, lesões, taxa redução) - `comparison`: Taxa lesões com/sem ação + redução alcançada - `timeline`: Array cronológico de eventos (alertas→sugestões→lesões) - `by_category`: Breakdown por categoria de alerta  **Interpretação:** - `reduction_rate > 0`: Sugestões reduziram lesões (eficaz) - `reduction_rate < 0`: Sugestões não tiveram efeito - `reduction_rate > 50%`: Altamente eficaz  **Permissões:** - Requer: `view_training_analytics`

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let startDate: string; //Data início (default: 60 dias atrás) (optional) (default to undefined)
let endDate: string; //Data fim (default: hoje) (optional) (default to undefined)
let category: string; //Filtrar por categoria de alerta (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet(
    teamId,
    startDate,
    endDate,
    category,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **startDate** | [**string**] | Data início (default: 60 dias atrás) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data fim (default: hoje) | (optional) defaults to undefined|
| **category** | [**string**] | Filtrar por categoria de alerta | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

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

# **getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet_0**
> any getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet_0()

Dashboard de Eficácia Preventiva (Step 22)  Analisa a correlação entre alertas, sugestões e lesões para avaliar se as ações preventivas estão funcionando.  **Lógica:** 1. Busca alertas do período 2. Identifica sugestões geradas por cada alerta 3. Verifica se sugestões foram aplicadas ou rejeitadas 4. Conta lesões em janela de +7 dias após ação 5. Compara taxa de lesões: com sugestão aplicada vs recusada  **Retorna:** - `summary`: Estatísticas gerais (alertas, sugestões, lesões, taxa redução) - `comparison`: Taxa lesões com/sem ação + redução alcançada - `timeline`: Array cronológico de eventos (alertas→sugestões→lesões) - `by_category`: Breakdown por categoria de alerta  **Interpretação:** - `reduction_rate > 0`: Sugestões reduziram lesões (eficaz) - `reduction_rate < 0`: Sugestões não tiveram efeito - `reduction_rate > 50%`: Altamente eficaz  **Permissões:** - Requer: `view_training_analytics`

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let startDate: string; //Data início (default: 60 dias atrás) (optional) (default to undefined)
let endDate: string; //Data fim (default: hoje) (optional) (default to undefined)
let category: string; //Filtrar por categoria de alerta (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPreventionEffectivenessApiV1AnalyticsTeamTeamIdPreventionEffectivenessGet_0(
    teamId,
    startDate,
    endDate,
    category,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **startDate** | [**string**] | Data início (default: 60 dias atrás) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data fim (default: hoje) | (optional) defaults to undefined|
| **category** | [**string**] | Filtrar por categoria de alerta | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

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

# **getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet**
> TeamSummaryResponse getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet()

Retorna métricas agregadas de analytics para uma equipe.  **Estratégia de cache:** - Mês corrente: usa cache weekly (por microciclo) - Meses anteriores: usa cache monthly - Recalcula automaticamente se `cache_dirty=true`  **Métricas incluídas (17):** - Total de sessões - Médias de focos (7 campos) - Carga de treino (RPE, carga interna) - Assiduidade - Wellness response rates (pré e pós) - Atletas com badges - Desvios de threshold  **Permissões:** - Requer: `view_training_analytics` - Papéis: Dirigente, Coordenador, Treinador

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let startDate: string; //Data início (default: início do mês) (optional) (default to undefined)
let endDate: string; //Data fim (default: hoje) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet(
    teamId,
    startDate,
    endDate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **startDate** | [**string**] | Data início (default: início do mês) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data fim (default: hoje) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamSummaryResponse**

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

# **getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet_0**
> TeamSummaryResponse getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet_0()

Retorna métricas agregadas de analytics para uma equipe.  **Estratégia de cache:** - Mês corrente: usa cache weekly (por microciclo) - Meses anteriores: usa cache monthly - Recalcula automaticamente se `cache_dirty=true`  **Métricas incluídas (17):** - Total de sessões - Médias de focos (7 campos) - Carga de treino (RPE, carga interna) - Assiduidade - Wellness response rates (pré e pós) - Atletas com badges - Desvios de threshold  **Permissões:** - Requer: `view_training_analytics` - Papéis: Dirigente, Coordenador, Treinador

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let startDate: string; //Data início (default: início do mês) (optional) (default to undefined)
let endDate: string; //Data fim (default: hoje) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamSummaryApiV1AnalyticsTeamTeamIdSummaryGet_0(
    teamId,
    startDate,
    endDate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **startDate** | [**string**] | Data início (default: início do mês) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data fim (default: hoje) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamSummaryResponse**

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

# **getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet**
> WeeklyLoadResponse getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet()

Retorna carga semanal das últimas N semanas.  **Use case:** - Monitorar progressão de carga ao longo das semanas - Identificar picos ou quedas abruptas - Comparar com planejamento (quando disponível)  **Dados retornados:** - Total de sessões por semana - Carga interna total - RPE médio - Taxa de assiduidade  **Permissões:** - Requer: `view_training_analytics`

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let weeks: number; //Quantidade de semanas (1-52) (optional) (default to 4)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet(
    teamId,
    weeks,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **weeks** | [**number**] | Quantidade de semanas (1-52) | (optional) defaults to 4|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WeeklyLoadResponse**

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

# **getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet_0**
> WeeklyLoadResponse getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet_0()

Retorna carga semanal das últimas N semanas.  **Use case:** - Monitorar progressão de carga ao longo das semanas - Identificar picos ou quedas abruptas - Comparar com planejamento (quando disponível)  **Dados retornados:** - Total de sessões por semana - Carga interna total - RPE médio - Taxa de assiduidade  **Permissões:** - Requer: `view_training_analytics`

### Example

```typescript
import {
    TrainingAnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let weeks: number; //Quantidade de semanas (1-52) (optional) (default to 4)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWeeklyLoadApiV1AnalyticsTeamTeamIdWeeklyLoadGet_0(
    teamId,
    weeks,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **weeks** | [**number**] | Quantidade de semanas (1-52) | (optional) defaults to 4|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WeeklyLoadResponse**

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

