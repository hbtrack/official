# AthleteTrainingApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet**](#gettrainingpreviewapiv1athletetrainingsessionssessionidpreviewget) | **GET** /api/v1/athlete/training-sessions/{session_id}/preview | Pré-visualização do treino para atleta com gate de wellness (INV-TRAIN-071)|
|[**getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet_0**](#gettrainingpreviewapiv1athletetrainingsessionssessionidpreviewget_0) | **GET** /api/v1/athlete/training-sessions/{session_id}/preview | Pré-visualização do treino para atleta com gate de wellness (INV-TRAIN-071)|
|[**getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet**](#getwellnesscontentgateapiv1athletewellnesscontentgatesessionidget) | **GET** /api/v1/athlete/wellness-content-gate/{session_id} | Gate de wellness do atleta para acesso a conteúdo (INV-TRAIN-071)|
|[**getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet_0**](#getwellnesscontentgateapiv1athletewellnesscontentgatesessionidget_0) | **GET** /api/v1/athlete/wellness-content-gate/{session_id} | Gate de wellness do atleta para acesso a conteúdo (INV-TRAIN-071)|

# **getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet**
> { [key: string]: any; } getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet()

Retorna dados de pré-visualização do treino para o atleta.  - Se wellness_blocked=True (AccessGated): retorna info mínima + flag - Se wellness_blocked=False (AccessGranted): retorna info completa com exercícios  INV-TRAIN-071: conteúdo completo (exercícios + mídia) apenas se wellness em dia.

### Example

```typescript
import {
    AthleteTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthleteTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet(
    sessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dados de preview (conteúdo completo ou mínimo segundo wellness_blocked) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas atleta da sessão) |  -  |
|**404** | Sessão ou atleta não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet_0**
> { [key: string]: any; } getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet_0()

Retorna dados de pré-visualização do treino para o atleta.  - Se wellness_blocked=True (AccessGated): retorna info mínima + flag - Se wellness_blocked=False (AccessGranted): retorna info completa com exercícios  INV-TRAIN-071: conteúdo completo (exercícios + mídia) apenas se wellness em dia.

### Example

```typescript
import {
    AthleteTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthleteTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingPreviewApiV1AthleteTrainingSessionsSessionIdPreviewGet_0(
    sessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dados de preview (conteúdo completo ou mínimo segundo wellness_blocked) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas atleta da sessão) |  -  |
|**404** | Sessão ou atleta não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet**
> { [key: string]: any; } getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet()

Verifica se o atleta autenticado tem wellness em dia e pode ver conteúdo completo.  INV-TRAIN-071: sem wellness = conteúdo completo bloqueado. INV-TRAIN-076: athlete_id inferido do JWT — NUNCA de query param (self-only).  Response: - has_wellness: bool — True se wellness diário completo - can_see_full_content: bool — True se acesso liberado - blocked_reason: str | null — razão do bloqueio quando has_wellness=False

### Example

```typescript
import {
    AthleteTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthleteTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet(
    sessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Estado do gate de wellness (has_wellness, can_see_full_content) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas o próprio atleta) |  -  |
|**404** | Atleta não encontrado para o usuário autenticado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet_0**
> { [key: string]: any; } getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet_0()

Verifica se o atleta autenticado tem wellness em dia e pode ver conteúdo completo.  INV-TRAIN-071: sem wellness = conteúdo completo bloqueado. INV-TRAIN-076: athlete_id inferido do JWT — NUNCA de query param (self-only).  Response: - has_wellness: bool — True se wellness diário completo - can_see_full_content: bool — True se acesso liberado - blocked_reason: str | null — razão do bloqueio quando has_wellness=False

### Example

```typescript
import {
    AthleteTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AthleteTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessContentGateApiV1AthleteWellnessContentGateSessionIdGet_0(
    sessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Estado do gate de wellness (has_wellness, can_see_full_content) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas o próprio atleta) |  -  |
|**404** | Atleta não encontrado para o usuário autenticado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

