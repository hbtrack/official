# DashboardApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getDashboardSummaryApiV1DashboardSummaryGet**](#getdashboardsummaryapiv1dashboardsummaryget) | **GET** /api/v1/dashboard/summary | Dashboard Agregado|
|[**getDashboardSummaryApiV1DashboardSummaryGet_0**](#getdashboardsummaryapiv1dashboardsummaryget_0) | **GET** /api/v1/dashboard/summary | Dashboard Agregado|
|[**getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet**](#getteamdashboardsummaryapiv1dashboardteamsteamidsummaryget) | **GET** /api/v1/dashboard/teams/{team_id}/summary | Dashboard de Equipe Específica|
|[**getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet_0**](#getteamdashboardsummaryapiv1dashboardteamsteamidsummaryget_0) | **GET** /api/v1/dashboard/teams/{team_id}/summary | Dashboard de Equipe Específica|
|[**invalidateCacheApiV1DashboardInvalidateCachePost**](#invalidatecacheapiv1dashboardinvalidatecachepost) | **POST** /api/v1/dashboard/invalidate-cache | Invalidar Cache do Dashboard|
|[**invalidateCacheApiV1DashboardInvalidateCachePost_0**](#invalidatecacheapiv1dashboardinvalidatecachepost_0) | **POST** /api/v1/dashboard/invalidate-cache | Invalidar Cache do Dashboard|

# **getDashboardSummaryApiV1DashboardSummaryGet**
> DashboardSummaryResponse getDashboardSummaryApiV1DashboardSummaryGet()

**Endpoint otimizado que retorna TODOS os dados do dashboard em uma única requisição.**          ## Performance     - Cache: 120 segundos por team_id + season_id     - Usa materialized views pré-calculadas     - Evita múltiplas requisições ao backend          ## Dados retornados     - **athletes**: total, ativas, lesionadas, dispensadas     - **training**: sessões, média de presença, carga média, últimos treinos     - **training_trends**: tendências por semana (12 semanas)     - **matches**: vitórias, empates, derrotas, gols     - **wellness**: sono, fadiga, estresse, humor, score de prontidão     - **medical**: casos ativos, recuperando, liberados     - **alerts**: até 10 alertas prioritários     - **next_training**: próximo treino agendado     - **next_match**: próximo jogo agendado          ## Headers de Cache     - `X-Cache-TTL`: tempo de vida do cache em segundos     - `X-Generated-At`: timestamp de geração dos dados          ## Uso recomendado     ```javascript     // Frontend - usar staleTime de 60-120s     const { data } = useQuery({       queryKey: [\'dashboard\', teamId, seasonId],       queryFn: () => fetch(\'/api/v1/dashboard/summary?team_id=xxx\'),       staleTime: 60_000, // 60 segundos       keepPreviousData: true,     })     ```

### Example

```typescript
import {
    DashboardApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardApi(configuration);

let teamId: string; //Filtrar por equipe específica (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let skipCache: boolean; //Forçar atualização (ignora cache) (optional) (default to false)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDashboardSummaryApiV1DashboardSummaryGet(
    teamId,
    seasonId,
    skipCache,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | Filtrar por equipe específica | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **skipCache** | [**boolean**] | Forçar atualização (ignora cache) | (optional) defaults to false|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardSummaryResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dashboard completo |  * X-Cache-TTL - Tempo de vida do cache em segundos <br>  * X-Generated-At - Timestamp de geração <br>  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Sem permissão para acessar este time |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getDashboardSummaryApiV1DashboardSummaryGet_0**
> DashboardSummaryResponse getDashboardSummaryApiV1DashboardSummaryGet_0()

**Endpoint otimizado que retorna TODOS os dados do dashboard em uma única requisição.**          ## Performance     - Cache: 120 segundos por team_id + season_id     - Usa materialized views pré-calculadas     - Evita múltiplas requisições ao backend          ## Dados retornados     - **athletes**: total, ativas, lesionadas, dispensadas     - **training**: sessões, média de presença, carga média, últimos treinos     - **training_trends**: tendências por semana (12 semanas)     - **matches**: vitórias, empates, derrotas, gols     - **wellness**: sono, fadiga, estresse, humor, score de prontidão     - **medical**: casos ativos, recuperando, liberados     - **alerts**: até 10 alertas prioritários     - **next_training**: próximo treino agendado     - **next_match**: próximo jogo agendado          ## Headers de Cache     - `X-Cache-TTL`: tempo de vida do cache em segundos     - `X-Generated-At`: timestamp de geração dos dados          ## Uso recomendado     ```javascript     // Frontend - usar staleTime de 60-120s     const { data } = useQuery({       queryKey: [\'dashboard\', teamId, seasonId],       queryFn: () => fetch(\'/api/v1/dashboard/summary?team_id=xxx\'),       staleTime: 60_000, // 60 segundos       keepPreviousData: true,     })     ```

### Example

```typescript
import {
    DashboardApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardApi(configuration);

let teamId: string; //Filtrar por equipe específica (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let skipCache: boolean; //Forçar atualização (ignora cache) (optional) (default to false)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDashboardSummaryApiV1DashboardSummaryGet_0(
    teamId,
    seasonId,
    skipCache,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | Filtrar por equipe específica | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **skipCache** | [**boolean**] | Forçar atualização (ignora cache) | (optional) defaults to false|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardSummaryResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dashboard completo |  * X-Cache-TTL - Tempo de vida do cache em segundos <br>  * X-Generated-At - Timestamp de geração <br>  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Sem permissão para acessar este time |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet**
> DashboardSummaryResponse getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet()

Atalho para `/dashboard/summary?team_id={team_id}`          Útil para URLs mais semânticas no frontend.

### Example

```typescript
import {
    DashboardApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardApi(configuration);

let teamId: string; // (default to undefined)
let seasonId: string; // (optional) (default to undefined)
let skipCache: boolean; // (optional) (default to false)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet(
    teamId,
    seasonId,
    skipCache,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **seasonId** | [**string**] |  | (optional) defaults to undefined|
| **skipCache** | [**boolean**] |  | (optional) defaults to false|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardSummaryResponse**

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

# **getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet_0**
> DashboardSummaryResponse getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet_0()

Atalho para `/dashboard/summary?team_id={team_id}`          Útil para URLs mais semânticas no frontend.

### Example

```typescript
import {
    DashboardApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardApi(configuration);

let teamId: string; // (default to undefined)
let seasonId: string; // (optional) (default to undefined)
let skipCache: boolean; // (optional) (default to false)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamDashboardSummaryApiV1DashboardTeamsTeamIdSummaryGet_0(
    teamId,
    seasonId,
    skipCache,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **seasonId** | [**string**] |  | (optional) defaults to undefined|
| **skipCache** | [**boolean**] |  | (optional) defaults to false|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**DashboardSummaryResponse**

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

# **invalidateCacheApiV1DashboardInvalidateCachePost**
> invalidateCacheApiV1DashboardInvalidateCachePost()

Força a invalidação do cache do dashboard.          **Usar quando:**     - Após salvar um treino     - Após finalizar um jogo     - Após atualizar estado de atleta     - Após registrar wellness          Na maioria dos casos, o cache expira naturalmente em 120s.

### Example

```typescript
import {
    DashboardApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardApi(configuration);

let teamId: string; //Invalidar cache de um time específico (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.invalidateCacheApiV1DashboardInvalidateCachePost(
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | Invalidar cache de um time específico | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **invalidateCacheApiV1DashboardInvalidateCachePost_0**
> invalidateCacheApiV1DashboardInvalidateCachePost_0()

Força a invalidação do cache do dashboard.          **Usar quando:**     - Após salvar um treino     - Após finalizar um jogo     - Após atualizar estado de atleta     - Após registrar wellness          Na maioria dos casos, o cache expira naturalmente em 120s.

### Example

```typescript
import {
    DashboardApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new DashboardApi(configuration);

let teamId: string; //Invalidar cache de um time específico (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.invalidateCacheApiV1DashboardInvalidateCachePost_0(
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | Invalidar cache de um time específico | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

