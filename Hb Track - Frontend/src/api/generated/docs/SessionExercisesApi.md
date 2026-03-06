# SessionExercisesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost**](#addexercisetosessionapiv1trainingsessionssessionidexercisespost) | **POST** /api/v1/training-sessions/{session_id}/exercises | Adicionar exercício à sessão|
|[**addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost_0**](#addexercisetosessionapiv1trainingsessionssessionidexercisespost_0) | **POST** /api/v1/training-sessions/{session_id}/exercises | Adicionar exercício à sessão|
|[**bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost**](#bulkaddexercisestosessionapiv1trainingsessionssessionidexercisesbulkpost) | **POST** /api/v1/training-sessions/{session_id}/exercises/bulk | Adicionar múltiplos exercícios (bulk)|
|[**bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost_0**](#bulkaddexercisestosessionapiv1trainingsessionssessionidexercisesbulkpost_0) | **POST** /api/v1/training-sessions/{session_id}/exercises/bulk | Adicionar múltiplos exercícios (bulk)|
|[**getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet**](#getsessionexercisesapiv1trainingsessionssessionidexercisesget) | **GET** /api/v1/training-sessions/{session_id}/exercises | Listar exercícios da sessão|
|[**getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet_0**](#getsessionexercisesapiv1trainingsessionssessionidexercisesget_0) | **GET** /api/v1/training-sessions/{session_id}/exercises | Listar exercícios da sessão|
|[**removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete**](#removeexercisefromsessionapiv1trainingsessionsexercisessessionexerciseiddelete) | **DELETE** /api/v1/training-sessions/exercises/{session_exercise_id} | Remover exercício da sessão|
|[**removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete_0**](#removeexercisefromsessionapiv1trainingsessionsexercisessessionexerciseiddelete_0) | **DELETE** /api/v1/training-sessions/exercises/{session_exercise_id} | Remover exercício da sessão|
|[**reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch**](#reordersessionexercisesapiv1trainingsessionssessionidexercisesreorderpatch) | **PATCH** /api/v1/training-sessions/{session_id}/exercises/reorder | Reordenar exercícios (bulk)|
|[**reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch_0**](#reordersessionexercisesapiv1trainingsessionssessionidexercisesreorderpatch_0) | **PATCH** /api/v1/training-sessions/{session_id}/exercises/reorder | Reordenar exercícios (bulk)|
|[**updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch**](#updatesessionexerciseapiv1trainingsessionsexercisessessionexerciseidpatch) | **PATCH** /api/v1/training-sessions/exercises/{session_exercise_id} | Atualizar metadados do exercício|
|[**updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch_0**](#updatesessionexerciseapiv1trainingsessionsexercisessessionexerciseidpatch_0) | **PATCH** /api/v1/training-sessions/exercises/{session_exercise_id} | Atualizar metadados do exercício|

# **addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost**
> SessionExerciseResponse addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost(sessionExerciseCreate)

Adiciona um exercício ao planejamento da sessão de treino. Requer permissão modify_training_session.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let sessionExerciseCreate: SessionExerciseCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost(
    sessionId,
    sessionExerciseCreate,
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
| **sessionExerciseCreate** | **SessionExerciseCreate**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionExerciseResponse**

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

# **addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost_0**
> SessionExerciseResponse addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost_0(sessionExerciseCreate)

Adiciona um exercício ao planejamento da sessão de treino. Requer permissão modify_training_session.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let sessionExerciseCreate: SessionExerciseCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addExerciseToSessionApiV1TrainingSessionsSessionIdExercisesPost_0(
    sessionId,
    sessionExerciseCreate,
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
| **sessionExerciseCreate** | **SessionExerciseCreate**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionExerciseResponse**

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

# **bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost**
> Array<SessionExerciseResponse> bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost(sessionExerciseBulkCreate)

Adiciona múltiplos exercícios de uma vez. Útil para drag-and-drop com seleção múltipla.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseBulkCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let sessionExerciseBulkCreate: SessionExerciseBulkCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost(
    sessionId,
    sessionExerciseBulkCreate,
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
| **sessionExerciseBulkCreate** | **SessionExerciseBulkCreate**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<SessionExerciseResponse>**

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

# **bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost_0**
> Array<SessionExerciseResponse> bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost_0(sessionExerciseBulkCreate)

Adiciona múltiplos exercícios de uma vez. Útil para drag-and-drop com seleção múltipla.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseBulkCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let sessionExerciseBulkCreate: SessionExerciseBulkCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkAddExercisesToSessionApiV1TrainingSessionsSessionIdExercisesBulkPost_0(
    sessionId,
    sessionExerciseBulkCreate,
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
| **sessionExerciseBulkCreate** | **SessionExerciseBulkCreate**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<SessionExerciseResponse>**

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

# **getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet**
> SessionExerciseListResponse getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet()

Retorna todos exercícios da sessão ordenados por order_index. Requer permissão view_training_session.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet(
    sessionId,
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
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionExerciseListResponse**

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

# **getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet_0**
> SessionExerciseListResponse getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet_0()

Retorna todos exercícios da sessão ordenados por order_index. Requer permissão view_training_session.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionExercisesApiV1TrainingSessionsSessionIdExercisesGet_0(
    sessionId,
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
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionExerciseListResponse**

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

# **removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete**
> removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete()

Remove exercício do planejamento da sessão (soft delete).

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionExerciseId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete(
    sessionExerciseId,
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
| **sessionExerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete_0**
> removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete_0()

Remove exercício do planejamento da sessão (soft delete).

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionExerciseId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeExerciseFromSessionApiV1TrainingSessionsExercisesSessionExerciseIdDelete_0(
    sessionExerciseId,
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
| **sessionExerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch**
> any reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch(sessionExerciseReorder)

Reordena múltiplos exercícios de uma vez. Usado após drag-and-drop de reordenação.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseReorder
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let sessionExerciseReorder: SessionExerciseReorder; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch(
    sessionId,
    sessionExerciseReorder,
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
| **sessionExerciseReorder** | **SessionExerciseReorder**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

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

# **reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch_0**
> any reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch_0(sessionExerciseReorder)

Reordena múltiplos exercícios de uma vez. Usado após drag-and-drop de reordenação.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseReorder
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionId: string; // (default to undefined)
let sessionExerciseReorder: SessionExerciseReorder; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.reorderSessionExercisesApiV1TrainingSessionsSessionIdExercisesReorderPatch_0(
    sessionId,
    sessionExerciseReorder,
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
| **sessionExerciseReorder** | **SessionExerciseReorder**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

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

# **updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch**
> SessionExerciseResponse updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch(sessionExerciseUpdate)

Atualiza order_index, duration_minutes ou notes de um exercício já adicionado.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionExerciseId: string; // (default to undefined)
let sessionExerciseUpdate: SessionExerciseUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch(
    sessionExerciseId,
    sessionExerciseUpdate,
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
| **sessionExerciseUpdate** | **SessionExerciseUpdate**|  | |
| **sessionExerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionExerciseResponse**

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

# **updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch_0**
> SessionExerciseResponse updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch_0(sessionExerciseUpdate)

Atualiza order_index, duration_minutes ou notes de um exercício já adicionado.

### Example

```typescript
import {
    SessionExercisesApi,
    Configuration,
    SessionExerciseUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionExercisesApi(configuration);

let sessionExerciseId: string; // (default to undefined)
let sessionExerciseUpdate: SessionExerciseUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSessionExerciseApiV1TrainingSessionsExercisesSessionExerciseIdPatch_0(
    sessionExerciseId,
    sessionExerciseUpdate,
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
| **sessionExerciseUpdate** | **SessionExerciseUpdate**|  | |
| **sessionExerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionExerciseResponse**

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

