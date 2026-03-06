# AnalyticsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost**](#calculaterankingsmanuallyapiv1analyticswellnessrankingscalculatepost) | **POST** /api/v1/analytics/wellness-rankings/calculate | Calculate Rankings Manually|
|[**calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost_0**](#calculaterankingsmanuallyapiv1analyticswellnessrankingscalculatepost_0) | **POST** /api/v1/analytics/wellness-rankings/calculate | Calculate Rankings Manually|
|[**getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet**](#getteamathletes90plusapiv1analyticswellnessrankingsteamidathletes90plusget) | **GET** /api/v1/analytics/wellness-rankings/{team_id}/athletes-90plus | Get Team Athletes 90Plus|
|[**getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet_0**](#getteamathletes90plusapiv1analyticswellnessrankingsteamidathletes90plusget_0) | **GET** /api/v1/analytics/wellness-rankings/{team_id}/athletes-90plus | Get Team Athletes 90Plus|
|[**getWellnessRankingsApiV1AnalyticsWellnessRankingsGet**](#getwellnessrankingsapiv1analyticswellnessrankingsget) | **GET** /api/v1/analytics/wellness-rankings | Get Wellness Rankings|
|[**getWellnessRankingsApiV1AnalyticsWellnessRankingsGet_0**](#getwellnessrankingsapiv1analyticswellnessrankingsget_0) | **GET** /api/v1/analytics/wellness-rankings | Get Wellness Rankings|

# **calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost**
> RankingCalculateResponse calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost()

Calcular rankings de wellness manualmente (apenas dirigentes)  Normalmente executado via scheduled job no dia 1 de cada mês. Este endpoint permite recalcular manualmente para testes ou correções.  Args:     month: Mês específico (YYYY-MM) ou None para mês anterior      Returns:     {         \"month_reference\": \"2026-01\",         \"teams_processed\": 16,         \"rankings_created\": 16,         \"top_team\": {\"id\": 5, \"name\": \"Sub-20\", \"avg_rate\": 95.5},         \"executed_at\": \"2026-02-01T00:00:00\"     }

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let month: string; //Mês de referência (YYYY-MM) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost(
    month,
    organizationId,
    teamId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **month** | [**string**] | Mês de referência (YYYY-MM) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**RankingCalculateResponse**

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

# **calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost_0**
> RankingCalculateResponse calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost_0()

Calcular rankings de wellness manualmente (apenas dirigentes)  Normalmente executado via scheduled job no dia 1 de cada mês. Este endpoint permite recalcular manualmente para testes ou correções.  Args:     month: Mês específico (YYYY-MM) ou None para mês anterior      Returns:     {         \"month_reference\": \"2026-01\",         \"teams_processed\": 16,         \"rankings_created\": 16,         \"top_team\": {\"id\": 5, \"name\": \"Sub-20\", \"avg_rate\": 95.5},         \"executed_at\": \"2026-02-01T00:00:00\"     }

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let month: string; //Mês de referência (YYYY-MM) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.calculateRankingsManuallyApiV1AnalyticsWellnessRankingsCalculatePost_0(
    month,
    organizationId,
    teamId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **month** | [**string**] | Mês de referência (YYYY-MM) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**RankingCalculateResponse**

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

# **getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet**
> Array<Athlete90PlusItemResponse> getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet()

Retorna lista de atletas com response_rate >= 90% em um team  Drill-down do ranking: mostra quais atletas específicos atingiram a meta.  Args:     team_id: ID do team     month: Mês de referência (YYYY-MM)      Returns:     [         {             \"athlete_id\": 10,             \"athlete_name\": \"João Silva\",             \"response_rate\": 95.5,             \"badge_earned\": true         }     ]  Ordenação: Por response_rate DESC  Acesso: - Dirigente: Qualquer team da organização - Coordenador/Treinador: Apenas teams que coordena/treina

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let month: string; //Mês de referência (YYYY-MM) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet(
    teamId,
    month,
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
| **month** | [**string**] | Mês de referência (YYYY-MM) | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<Athlete90PlusItemResponse>**

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

# **getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet_0**
> Array<Athlete90PlusItemResponse> getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet_0()

Retorna lista de atletas com response_rate >= 90% em um team  Drill-down do ranking: mostra quais atletas específicos atingiram a meta.  Args:     team_id: ID do team     month: Mês de referência (YYYY-MM)      Returns:     [         {             \"athlete_id\": 10,             \"athlete_name\": \"João Silva\",             \"response_rate\": 95.5,             \"badge_earned\": true         }     ]  Ordenação: Por response_rate DESC  Acesso: - Dirigente: Qualquer team da organização - Coordenador/Treinador: Apenas teams que coordena/treina

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let teamId: string; // (default to undefined)
let month: string; //Mês de referência (YYYY-MM) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamAthletes90plusApiV1AnalyticsWellnessRankingsTeamIdAthletes90plusGet_0(
    teamId,
    month,
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
| **month** | [**string**] | Mês de referência (YYYY-MM) | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<Athlete90PlusItemResponse>**

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

# **getWellnessRankingsApiV1AnalyticsWellnessRankingsGet**
> Array<WellnessRankingItemResponse> getWellnessRankingsApiV1AnalyticsWellnessRankingsGet()

Retorna ranking de equipes por taxa de resposta de wellness  Métricas calculadas: - response_rate_pre: Taxa de resposta wellness pré-treino - response_rate_post: Taxa de resposta wellness pós-treino - avg_rate: Média (pre + post) / 2 - rank: Posição no ranking (1º, 2º, 3º, ...) - athletes_90plus: Quantidade de atletas com rate >= 90%  Ordenação: Por avg_rate DESC  Args:     month: Mês específico (YYYY-MM) ou None para mês anterior     limit: Limite de resultados      Returns:     [         {             \"team_id\": 5,             \"team_name\": \"Sub-20\",             \"response_rate_pre\": 85.5,             \"response_rate_post\": 75.2,             \"avg_rate\": 80.35,             \"rank\": 1,             \"athletes_90plus\": 12,             \"calculated_at\": \"2026-02-01T00:00:00\"         }     ]  Acesso: - Dirigente: Todos os teams da organização - Coordenador/Treinador: Apenas teams que coordena/treina

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let month: string; //Mês de referência (YYYY-MM) (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessRankingsApiV1AnalyticsWellnessRankingsGet(
    month,
    limit,
    organizationId,
    teamId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **month** | [**string**] | Mês de referência (YYYY-MM) | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<WellnessRankingItemResponse>**

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

# **getWellnessRankingsApiV1AnalyticsWellnessRankingsGet_0**
> Array<WellnessRankingItemResponse> getWellnessRankingsApiV1AnalyticsWellnessRankingsGet_0()

Retorna ranking de equipes por taxa de resposta de wellness  Métricas calculadas: - response_rate_pre: Taxa de resposta wellness pré-treino - response_rate_post: Taxa de resposta wellness pós-treino - avg_rate: Média (pre + post) / 2 - rank: Posição no ranking (1º, 2º, 3º, ...) - athletes_90plus: Quantidade de atletas com rate >= 90%  Ordenação: Por avg_rate DESC  Args:     month: Mês específico (YYYY-MM) ou None para mês anterior     limit: Limite de resultados      Returns:     [         {             \"team_id\": 5,             \"team_name\": \"Sub-20\",             \"response_rate_pre\": 85.5,             \"response_rate_post\": 75.2,             \"avg_rate\": 80.35,             \"rank\": 1,             \"athletes_90plus\": 12,             \"calculated_at\": \"2026-02-01T00:00:00\"         }     ]  Acesso: - Dirigente: Todos os teams da organização - Coordenador/Treinador: Apenas teams que coordena/treina

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let month: string; //Mês de referência (YYYY-MM) (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessRankingsApiV1AnalyticsWellnessRankingsGet_0(
    month,
    limit,
    organizationId,
    teamId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **month** | [**string**] | Mês de referência (YYYY-MM) | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<WellnessRankingItemResponse>**

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

