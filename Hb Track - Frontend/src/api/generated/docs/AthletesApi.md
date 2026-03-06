# AthletesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createAthleteApiV1AthletesPost**](#createathleteapiv1athletespost) | **POST** /api/v1/athletes | Create Athlete|
|[**createAthleteApiV1AthletesPost_0**](#createathleteapiv1athletespost_0) | **POST** /api/v1/athletes | Create Athlete|
|[**deleteAthleteApiV1AthletesAthleteIdDelete**](#deleteathleteapiv1athletesathleteiddelete) | **DELETE** /api/v1/athletes/{athlete_id} | Delete Athlete|
|[**deleteAthleteApiV1AthletesAthleteIdDelete_0**](#deleteathleteapiv1athletesathleteiddelete_0) | **DELETE** /api/v1/athletes/{athlete_id} | Delete Athlete|
|[**getAthleteApiV1AthletesAthleteIdGet**](#getathleteapiv1athletesathleteidget) | **GET** /api/v1/athletes/{athlete_id} | Get Athlete|
|[**getAthleteApiV1AthletesAthleteIdGet_0**](#getathleteapiv1athletesathleteidget_0) | **GET** /api/v1/athletes/{athlete_id} | Get Athlete|
|[**getAthleteBadgesApiV1AthletesAthleteIdBadgesGet**](#getathletebadgesapiv1athletesathleteidbadgesget) | **GET** /api/v1/athletes/{athlete_id}/badges | Get Athlete Badges|
|[**getAthleteBadgesApiV1AthletesAthleteIdBadgesGet_0**](#getathletebadgesapiv1athletesathleteidbadgesget_0) | **GET** /api/v1/athletes/{athlete_id}/badges | Get Athlete Badges|
|[**getAthleteHistoryApiV1AthletesAthleteIdHistoryGet**](#getathletehistoryapiv1athletesathleteidhistoryget) | **GET** /api/v1/athletes/{athlete_id}/history | Get Athlete History|
|[**getAthleteHistoryApiV1AthletesAthleteIdHistoryGet_0**](#getathletehistoryapiv1athletesathleteidhistoryget_0) | **GET** /api/v1/athletes/{athlete_id}/history | Get Athlete History|
|[**getAthleteStatsApiV1AthletesStatsGet**](#getathletestatsapiv1athletesstatsget) | **GET** /api/v1/athletes/stats | Get Athlete Stats|
|[**getAthleteStatsApiV1AthletesStatsGet_0**](#getathletestatsapiv1athletesstatsget_0) | **GET** /api/v1/athletes/stats | Get Athlete Stats|
|[**getAvailableTodayApiV1AthletesAvailableTodayGet**](#getavailabletodayapiv1athletesavailabletodayget) | **GET** /api/v1/athletes/available-today | Get Available Today|
|[**getAvailableTodayApiV1AthletesAvailableTodayGet_0**](#getavailabletodayapiv1athletesavailabletodayget_0) | **GET** /api/v1/athletes/available-today | Get Available Today|
|[**listAthletesApiV1AthletesGet**](#listathletesapiv1athletesget) | **GET** /api/v1/athletes | List Athletes|
|[**listAthletesApiV1AthletesGet_0**](#listathletesapiv1athletesget_0) | **GET** /api/v1/athletes | List Athletes|
|[**updateAthleteApiV1AthletesAthleteIdPatch**](#updateathleteapiv1athletesathleteidpatch) | **PATCH** /api/v1/athletes/{athlete_id} | Update Athlete|
|[**updateAthleteApiV1AthletesAthleteIdPatch_0**](#updateathleteapiv1athletesathleteidpatch_0) | **PATCH** /api/v1/athletes/{athlete_id} | Update Athlete|

# **createAthleteApiV1AthletesPost**
> AthleteResponse createAthleteApiV1AthletesPost(appSchemasAthletesV2AthleteCreate)

Cria atleta.  RF1.1: Vínculo com equipe é OPCIONAL no cadastro. RD13: Goleiras não podem ter posição ofensiva.

### Example

```typescript
import {
    AthletesApi,
    Configuration,
    AppSchemasAthletesV2AthleteCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let appSchemasAthletesV2AthleteCreate: AppSchemasAthletesV2AthleteCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createAthleteApiV1AthletesPost(
    appSchemasAthletesV2AthleteCreate,
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
| **appSchemasAthletesV2AthleteCreate** | **AppSchemasAthletesV2AthleteCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createAthleteApiV1AthletesPost_0**
> AthleteResponse createAthleteApiV1AthletesPost_0(appSchemasAthletesV2AthleteCreate)

Cria atleta.  RF1.1: Vínculo com equipe é OPCIONAL no cadastro. RD13: Goleiras não podem ter posição ofensiva.

### Example

```typescript
import {
    AthletesApi,
    Configuration,
    AppSchemasAthletesV2AthleteCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let appSchemasAthletesV2AthleteCreate: AppSchemasAthletesV2AthleteCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createAthleteApiV1AthletesPost_0(
    appSchemasAthletesV2AthleteCreate,
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
| **appSchemasAthletesV2AthleteCreate** | **AppSchemasAthletesV2AthleteCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteAthleteApiV1AthletesAthleteIdDelete**
> deleteAthleteApiV1AthletesAthleteIdDelete()

Exclui atleta (soft delete - RDB4).  Comportamento: - Soft delete: marca deleted_at e deleted_reason - Encerra todos os team_registrations ativos

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (optional) (default to 'Exclusão manual')
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteAthleteApiV1AthletesAthleteIdDelete(
    athleteId,
    reason,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | (optional) defaults to 'Exclusão manual'|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **deleteAthleteApiV1AthletesAthleteIdDelete_0**
> deleteAthleteApiV1AthletesAthleteIdDelete_0()

Exclui atleta (soft delete - RDB4).  Comportamento: - Soft delete: marca deleted_at e deleted_reason - Encerra todos os team_registrations ativos

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (optional) (default to 'Exclusão manual')
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteAthleteApiV1AthletesAthleteIdDelete_0(
    athleteId,
    reason,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | (optional) defaults to 'Exclusão manual'|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **getAthleteApiV1AthletesAthleteIdGet**
> AthleteResponse getAthleteApiV1AthletesAthleteIdGet()

Retorna atleta por ID.

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteApiV1AthletesAthleteIdGet(
    athleteId,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteResponse**

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

# **getAthleteApiV1AthletesAthleteIdGet_0**
> AthleteResponse getAthleteApiV1AthletesAthleteIdGet_0()

Retorna atleta por ID.

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteApiV1AthletesAthleteIdGet_0(
    athleteId,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteResponse**

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

# **getAthleteBadgesApiV1AthletesAthleteIdBadgesGet**
> any getAthleteBadgesApiV1AthletesAthleteIdBadgesGet()

Retorna badges conquistados pelo atleta (Sistema de Gamificação).  Badges disponíveis: - wellness_champion_monthly: Taxa de resposta >= 90% no mês - wellness_streak_3months: 3 meses consecutivos com badge monthly  Resposta: [     {         \"id\": 1,         \"badge_type\": \"wellness_champion_monthly\",         \"month_reference\": \"2026-01\",         \"response_rate\": 95.0,         \"earned_at\": \"2026-02-01T00:00:00\"     } ]  Regras: - Atleta pode ver apenas próprios badges - Staff pode ver badges de qualquer atleta do time

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteBadgesApiV1AthletesAthleteIdBadgesGet(
    athleteId,
    limit,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **getAthleteBadgesApiV1AthletesAthleteIdBadgesGet_0**
> any getAthleteBadgesApiV1AthletesAthleteIdBadgesGet_0()

Retorna badges conquistados pelo atleta (Sistema de Gamificação).  Badges disponíveis: - wellness_champion_monthly: Taxa de resposta >= 90% no mês - wellness_streak_3months: 3 meses consecutivos com badge monthly  Resposta: [     {         \"id\": 1,         \"badge_type\": \"wellness_champion_monthly\",         \"month_reference\": \"2026-01\",         \"response_rate\": 95.0,         \"earned_at\": \"2026-02-01T00:00:00\"     } ]  Regras: - Atleta pode ver apenas próprios badges - Staff pode ver badges de qualquer atleta do time

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteBadgesApiV1AthletesAthleteIdBadgesGet_0(
    athleteId,
    limit,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **getAthleteHistoryApiV1AthletesAthleteIdHistoryGet**
> any getAthleteHistoryApiV1AthletesAthleteIdHistoryGet()

Retorna histórico de eventos da atleta (FASE 5.4 - Timeline).  Busca eventos de: - audit_logs (ações auditadas) - team_registrations (vínculos) - medical_cases (casos médicos - se existir)  Regras RAG: - R30: Ações críticas auditáveis - R31: Log obrigatório (actor_id, timestamp, action, context, old_value, new_value) - R34: Imutabilidade dos logs

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let eventType: string; //Filtrar por tipo de evento (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteHistoryApiV1AthletesAthleteIdHistoryGet(
    athleteId,
    eventType,
    limit,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **eventType** | [**string**] | Filtrar por tipo de evento | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **getAthleteHistoryApiV1AthletesAthleteIdHistoryGet_0**
> any getAthleteHistoryApiV1AthletesAthleteIdHistoryGet_0()

Retorna histórico de eventos da atleta (FASE 5.4 - Timeline).  Busca eventos de: - audit_logs (ações auditadas) - team_registrations (vínculos) - medical_cases (casos médicos - se existir)  Regras RAG: - R30: Ações críticas auditáveis - R31: Log obrigatório (actor_id, timestamp, action, context, old_value, new_value) - R34: Imutabilidade dos logs

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let eventType: string; //Filtrar por tipo de evento (optional) (default to undefined)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteHistoryApiV1AthletesAthleteIdHistoryGet_0(
    athleteId,
    eventType,
    limit,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **eventType** | [**string**] | Filtrar por tipo de evento | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **getAthleteStatsApiV1AthletesStatsGet**
> AthleteStatsResponse getAthleteStatsApiV1AthletesStatsGet()

Retorna estatísticas de atletas para dashboard (FASE 2).  KPIs: - Total de atletas - Em captação (sem team_registration ativo) - Lesionadas (injured=true) - Suspensas (suspended_until >= hoje) - Por estado (ativa, dispensada, arquivada) - Por categoria

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteStatsApiV1AthletesStatsGet(
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
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteStatsResponse**

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

# **getAthleteStatsApiV1AthletesStatsGet_0**
> AthleteStatsResponse getAthleteStatsApiV1AthletesStatsGet_0()

Retorna estatísticas de atletas para dashboard (FASE 2).  KPIs: - Total de atletas - Em captação (sem team_registration ativo) - Lesionadas (injured=true) - Suspensas (suspended_until >= hoje) - Por estado (ativa, dispensada, arquivada) - Por categoria

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteStatsApiV1AthletesStatsGet_0(
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
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteStatsResponse**

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

# **getAvailableTodayApiV1AthletesAvailableTodayGet**
> any getAvailableTodayApiV1AthletesAvailableTodayGet()

Retorna atletas disponíveis para jogar hoje (FASE 5.5).  Critérios de disponibilidade: - state = \'ativa\' - injured = false - suspended_until IS NULL OR suspended_until < hoje - Tem team_registration ativo  Regras RAG: - R12: Estado \'ativa\' é obrigatório - R13: injured=true e suspended_until bloqueiam participação em jogos

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let teamId: string; // (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAvailableTodayApiV1AthletesAvailableTodayGet(
    teamId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **getAvailableTodayApiV1AthletesAvailableTodayGet_0**
> any getAvailableTodayApiV1AthletesAvailableTodayGet_0()

Retorna atletas disponíveis para jogar hoje (FASE 5.5).  Critérios de disponibilidade: - state = \'ativa\' - injured = false - suspended_until IS NULL OR suspended_until < hoje - Tem team_registration ativo  Regras RAG: - R12: Estado \'ativa\' é obrigatório - R13: injured=true e suspended_until bloqueiam participação em jogos

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let teamId: string; // (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAvailableTodayApiV1AthletesAvailableTodayGet_0(
    teamId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

# **listAthletesApiV1AthletesGet**
> AthletePaginatedResponse listAthletesApiV1AthletesGet()

Lista atletas da organização.  V1.2 (Opção B - REGRAS.md): - Por padrão mostra TODAS as atletas da organização (com ou sem equipe) - Filtro has_team:   - true: apenas atletas COM team_registration ativo   - false: apenas atletas SEM team_registration ativo   - null/omitido: todas as atletas - RF1.1: Atleta pode existir sem equipe - R32: Atleta sem equipe não opera, mas aparece na lista

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let state: AthleteStateEnum; // (optional) (default to undefined)
let search: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let hasTeam: boolean; //Filtrar: true=com equipe, false=sem equipe, null=todas (optional) (default to undefined)
let page: number; // (optional) (default to 1)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAthletesApiV1AthletesGet(
    state,
    search,
    teamId,
    hasTeam,
    page,
    limit,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **state** | **AthleteStateEnum** |  | (optional) defaults to undefined|
| **search** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **hasTeam** | [**boolean**] | Filtrar: true&#x3D;com equipe, false&#x3D;sem equipe, null&#x3D;todas | (optional) defaults to undefined|
| **page** | [**number**] |  | (optional) defaults to 1|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthletePaginatedResponse**

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

# **listAthletesApiV1AthletesGet_0**
> AthletePaginatedResponse listAthletesApiV1AthletesGet_0()

Lista atletas da organização.  V1.2 (Opção B - REGRAS.md): - Por padrão mostra TODAS as atletas da organização (com ou sem equipe) - Filtro has_team:   - true: apenas atletas COM team_registration ativo   - false: apenas atletas SEM team_registration ativo   - null/omitido: todas as atletas - RF1.1: Atleta pode existir sem equipe - R32: Atleta sem equipe não opera, mas aparece na lista

### Example

```typescript
import {
    AthletesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let state: AthleteStateEnum; // (optional) (default to undefined)
let search: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let hasTeam: boolean; //Filtrar: true=com equipe, false=sem equipe, null=todas (optional) (default to undefined)
let page: number; // (optional) (default to 1)
let limit: number; // (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAthletesApiV1AthletesGet_0(
    state,
    search,
    teamId,
    hasTeam,
    page,
    limit,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **state** | **AthleteStateEnum** |  | (optional) defaults to undefined|
| **search** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **hasTeam** | [**boolean**] | Filtrar: true&#x3D;com equipe, false&#x3D;sem equipe, null&#x3D;todas | (optional) defaults to undefined|
| **page** | [**number**] |  | (optional) defaults to 1|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthletePaginatedResponse**

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

# **updateAthleteApiV1AthletesAthleteIdPatch**
> AthleteResponse updateAthleteApiV1AthletesAthleteIdPatch(athleteUpdate)

Atualiza atleta.

### Example

```typescript
import {
    AthletesApi,
    Configuration,
    AthleteUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let athleteUpdate: AthleteUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateAthleteApiV1AthletesAthleteIdPatch(
    athleteId,
    athleteUpdate,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteUpdate** | **AthleteUpdate**|  | |
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateAthleteApiV1AthletesAthleteIdPatch_0**
> AthleteResponse updateAthleteApiV1AthletesAthleteIdPatch_0(athleteUpdate)

Atualiza atleta.

### Example

```typescript
import {
    AthletesApi,
    Configuration,
    AthleteUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new AthletesApi(configuration);

let athleteId: string; // (default to undefined)
let athleteUpdate: AthleteUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateAthleteApiV1AthletesAthleteIdPatch_0(
    athleteId,
    athleteUpdate,
    organizationId,
    teamId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteUpdate** | **AthleteUpdate**|  | |
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

