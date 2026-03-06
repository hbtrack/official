# TrainingSessionsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost**](#closetrainingsessionapiv1trainingsessionstrainingsessionidclosepost) | **POST** /api/v1/training-sessions/{training_session_id}/close | Finaliza revisão operacional e congela a sessão|
|[**closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost_0**](#closetrainingsessionapiv1trainingsessionstrainingsessionidclosepost_0) | **POST** /api/v1/training-sessions/{training_session_id}/close | Finaliza revisão operacional e congela a sessão|
|[**copyWeekSessionsApiV1TrainingSessionsCopyWeekPost**](#copyweeksessionsapiv1trainingsessionscopyweekpost) | **POST** /api/v1/training-sessions/copy-week | Copiar semana de treinos|
|[**copyWeekSessionsApiV1TrainingSessionsCopyWeekPost_0**](#copyweeksessionsapiv1trainingsessionscopyweekpost_0) | **POST** /api/v1/training-sessions/copy-week | Copiar semana de treinos|
|[**createTrainingSessionApiV1TrainingSessionsPost**](#createtrainingsessionapiv1trainingsessionspost) | **POST** /api/v1/training-sessions | Cria sessão de treino|
|[**createTrainingSessionApiV1TrainingSessionsPost_0**](#createtrainingsessionapiv1trainingsessionspost_0) | **POST** /api/v1/training-sessions | Cria sessão de treino|
|[**deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete**](#deletetrainingsessionapiv1trainingsessionstrainingsessioniddelete) | **DELETE** /api/v1/training-sessions/{training_session_id} | Exclui sessão de treino|
|[**deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete_0**](#deletetrainingsessionapiv1trainingsessionstrainingsessioniddelete_0) | **DELETE** /api/v1/training-sessions/{training_session_id} | Exclui sessão de treino|
|[**duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost**](#duplicatetrainingsessionapiv1trainingsessionstrainingsessionidduplicatepost) | **POST** /api/v1/training-sessions/{training_session_id}/duplicate | Duplicar sessão de treino|
|[**duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost_0**](#duplicatetrainingsessionapiv1trainingsessionstrainingsessionidduplicatepost_0) | **POST** /api/v1/training-sessions/{training_session_id}/duplicate | Duplicar sessão de treino|
|[**getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet**](#getsessiondeviationapiv1trainingsessionstrainingsessioniddeviationget) | **GET** /api/v1/training-sessions/{training_session_id}/deviation | Análise de desvio (planejado vs executado)|
|[**getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet_0**](#getsessiondeviationapiv1trainingsessionstrainingsessioniddeviationget_0) | **GET** /api/v1/training-sessions/{training_session_id}/deviation | Análise de desvio (planejado vs executado)|
|[**getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet**](#gettrainingsessionbyidapiv1trainingsessionstrainingsessionidget) | **GET** /api/v1/training-sessions/{training_session_id} | Obtém sessão de treino por ID|
|[**getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet_0**](#gettrainingsessionbyidapiv1trainingsessionstrainingsessionidget_0) | **GET** /api/v1/training-sessions/{training_session_id} | Obtém sessão de treino por ID|
|[**getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet**](#getwellnessstatusapiv1trainingsessionstrainingsessionidwellnessstatusget) | **GET** /api/v1/training-sessions/{training_session_id}/wellness-status | Status de wellness da sessão|
|[**getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet_0**](#getwellnessstatusapiv1trainingsessionstrainingsessionidwellnessstatusget_0) | **GET** /api/v1/training-sessions/{training_session_id}/wellness-status | Status de wellness da sessão|
|[**listTrainingSessionsApiV1TrainingSessionsGet**](#listtrainingsessionsapiv1trainingsessionsget) | **GET** /api/v1/training-sessions | Lista sessões de treino|
|[**listTrainingSessionsApiV1TrainingSessionsGet_0**](#listtrainingsessionsapiv1trainingsessionsget_0) | **GET** /api/v1/training-sessions | Lista sessões de treino|
|[**publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost**](#publishtrainingsessionapiv1trainingsessionstrainingsessionidpublishpost) | **POST** /api/v1/training-sessions/{training_session_id}/publish | Publica sessão completa (draft → scheduled)|
|[**publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost_0**](#publishtrainingsessionapiv1trainingsessionstrainingsessionidpublishpost_0) | **POST** /api/v1/training-sessions/{training_session_id}/publish | Publica sessão completa (draft → scheduled)|
|[**restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost**](#restoretrainingsessionapiv1trainingsessionstrainingsessionidrestorepost) | **POST** /api/v1/training-sessions/{training_session_id}/restore | Restaura sessão de treino|
|[**restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost_0**](#restoretrainingsessionapiv1trainingsessionstrainingsessionidrestorepost_0) | **POST** /api/v1/training-sessions/{training_session_id}/restore | Restaura sessão de treino|
|[**scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost**](#scopedcreatetrainingsessionapiv1teamsteamidtrainingspost) | **POST** /api/v1/teams/{team_id}/trainings | Criar sessao de treino (escopo equipe)|
|[**scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost_0**](#scopedcreatetrainingsessionapiv1teamsteamidtrainingspost_0) | **POST** /api/v1/teams/{team_id}/trainings | Criar sessao de treino (escopo equipe)|
|[**scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete**](#scopeddeletetrainingsessionapiv1teamsteamidtrainingstrainingiddelete) | **DELETE** /api/v1/teams/{team_id}/trainings/{training_id} | Excluir sessao de treino (escopo equipe)|
|[**scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete_0**](#scopeddeletetrainingsessionapiv1teamsteamidtrainingstrainingiddelete_0) | **DELETE** /api/v1/teams/{team_id}/trainings/{training_id} | Excluir sessao de treino (escopo equipe)|
|[**scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet**](#scopedgettrainingsessionapiv1teamsteamidtrainingstrainingidget) | **GET** /api/v1/teams/{team_id}/trainings/{training_id} | Detalhar sessao de treino (escopo equipe)|
|[**scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet_0**](#scopedgettrainingsessionapiv1teamsteamidtrainingstrainingidget_0) | **GET** /api/v1/teams/{team_id}/trainings/{training_id} | Detalhar sessao de treino (escopo equipe)|
|[**scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet**](#scopedlisttrainingsessionsapiv1teamsteamidtrainingsget) | **GET** /api/v1/teams/{team_id}/trainings | Listar sessoes de treino (escopo equipe)|
|[**scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet_0**](#scopedlisttrainingsessionsapiv1teamsteamidtrainingsget_0) | **GET** /api/v1/teams/{team_id}/trainings | Listar sessoes de treino (escopo equipe)|
|[**scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost**](#scopedrestoretrainingsessionapiv1teamsteamidtrainingstrainingidrestorepost) | **POST** /api/v1/teams/{team_id}/trainings/{training_id}/restore | Restaurar sessao de treino (escopo equipe)|
|[**scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost_0**](#scopedrestoretrainingsessionapiv1teamsteamidtrainingstrainingidrestorepost_0) | **POST** /api/v1/teams/{team_id}/trainings/{training_id}/restore | Restaurar sessao de treino (escopo equipe)|
|[**scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch**](#scopedupdatetrainingsessionapiv1teamsteamidtrainingstrainingidpatch) | **PATCH** /api/v1/teams/{team_id}/trainings/{training_id} | Atualizar sessao de treino (escopo equipe)|
|[**scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch_0**](#scopedupdatetrainingsessionapiv1teamsteamidtrainingstrainingidpatch_0) | **PATCH** /api/v1/teams/{team_id}/trainings/{training_id} | Atualizar sessao de treino (escopo equipe)|
|[**updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch**](#updatetrainingsessionapiv1trainingsessionstrainingsessionidpatch) | **PATCH** /api/v1/training-sessions/{training_session_id} | Atualiza sessão de treino|
|[**updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch_0**](#updatetrainingsessionapiv1trainingsessionstrainingsessionidpatch_0) | **PATCH** /api/v1/training-sessions/{training_session_id} | Atualiza sessão de treino|

# **closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost**
> SessionClosureResponse closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost()

Finaliza a revisão operacional (pending_review → readonly) com validações bloqueantes

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost(
    trainingSessionId,
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
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionClosureResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Resposta de fechamento (success&#x3D;True se fechou, False com validation se falhou) |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost_0**
> SessionClosureResponse closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost_0()

Finaliza a revisão operacional (pending_review → readonly) com validações bloqueantes

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.closeTrainingSessionApiV1TrainingSessionsTrainingSessionIdClosePost_0(
    trainingSessionId,
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
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionClosureResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Resposta de fechamento (success&#x3D;True se fechou, False com validation se falhou) |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **copyWeekSessionsApiV1TrainingSessionsCopyWeekPost**
> Array<TrainingSession> copyWeekSessionsApiV1TrainingSessionsCopyWeekPost()

Cria cópias de todas as sessões de uma semana para outra data

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; //ID do time (default to undefined)
let sourceWeekStart: string; //Data inicial da semana de origem (default to undefined)
let targetWeekStart: string; //Data inicial da semana de destino (default to undefined)
let validateFocus: boolean; //Validar soma de focos = 100% (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.copyWeekSessionsApiV1TrainingSessionsCopyWeekPost(
    teamId,
    sourceWeekStart,
    targetWeekStart,
    validateFocus,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID do time | defaults to undefined|
| **sourceWeekStart** | [**string**] | Data inicial da semana de origem | defaults to undefined|
| **targetWeekStart** | [**string**] | Data inicial da semana de destino | defaults to undefined|
| **validateFocus** | [**boolean**] | Validar soma de focos &#x3D; 100% | (optional) defaults to true|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingSession>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Sessões da semana copiadas |  -  |
|**400** | Parâmetros inválidos ou validação de focos falhou |  -  |
|**404** | Sessões não encontradas |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **copyWeekSessionsApiV1TrainingSessionsCopyWeekPost_0**
> Array<TrainingSession> copyWeekSessionsApiV1TrainingSessionsCopyWeekPost_0()

Cria cópias de todas as sessões de uma semana para outra data

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; //ID do time (default to undefined)
let sourceWeekStart: string; //Data inicial da semana de origem (default to undefined)
let targetWeekStart: string; //Data inicial da semana de destino (default to undefined)
let validateFocus: boolean; //Validar soma de focos = 100% (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.copyWeekSessionsApiV1TrainingSessionsCopyWeekPost_0(
    teamId,
    sourceWeekStart,
    targetWeekStart,
    validateFocus,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID do time | defaults to undefined|
| **sourceWeekStart** | [**string**] | Data inicial da semana de origem | defaults to undefined|
| **targetWeekStart** | [**string**] | Data inicial da semana de destino | defaults to undefined|
| **validateFocus** | [**boolean**] | Validar soma de focos &#x3D; 100% | (optional) defaults to true|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingSession>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Sessões da semana copiadas |  -  |
|**400** | Parâmetros inválidos ou validação de focos falhou |  -  |
|**404** | Sessões não encontradas |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createTrainingSessionApiV1TrainingSessionsPost**
> TrainingSession createTrainingSessionApiV1TrainingSessionsPost(trainingSessionCreate)

Cria uma nova sessão de treino (evento operacional).  **Regras**: - R18: Treinos são eventos operacionais. - R22: Métricas operacionais, não substituem estatísticas de jogo. - R25/R26: Permissões por papel e escopo. - Step 2: Validação de permissão can_create_training

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    TrainingSessionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionCreate: TrainingSessionCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTrainingSessionApiV1TrainingSessionsPost(
    trainingSessionCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionCreate** | **TrainingSessionCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Sessão criada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Time não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createTrainingSessionApiV1TrainingSessionsPost_0**
> TrainingSession createTrainingSessionApiV1TrainingSessionsPost_0(trainingSessionCreate)

Cria uma nova sessão de treino (evento operacional).  **Regras**: - R18: Treinos são eventos operacionais. - R22: Métricas operacionais, não substituem estatísticas de jogo. - R25/R26: Permissões por papel e escopo. - Step 2: Validação de permissão can_create_training

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    TrainingSessionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionCreate: TrainingSessionCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTrainingSessionApiV1TrainingSessionsPost_0(
    trainingSessionCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionCreate** | **TrainingSessionCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Sessão criada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Time não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete**
> TrainingSession deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete()

Soft delete de sessão de treino.  **Regras**: - R29/R33: Sem DELETE físico, histórico com rastro - RDB3: Soft delete com deleted_at e deleted_reason

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete(
    trainingSessionId,
    reason,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão excluída (soft delete) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete_0**
> TrainingSession deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete_0()

Soft delete de sessão de treino.  **Regras**: - R29/R33: Sem DELETE físico, histórico com rastro - RDB3: Soft delete com deleted_at e deleted_reason

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTrainingSessionApiV1TrainingSessionsTrainingSessionIdDelete_0(
    trainingSessionId,
    reason,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão excluída (soft delete) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost**
> TrainingSession duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost()

Cria uma cópia de uma sessão existente com status draft

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Sessão duplicada criada |  -  |
|**400** | Sessão muito antiga (&gt;60 dias) ou já deletada |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost_0**
> TrainingSession duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost_0()

Cria uma cópia de uma sessão existente com status draft

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.duplicateTrainingSessionApiV1TrainingSessionsTrainingSessionIdDuplicatePost_0(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Sessão duplicada criada |  -  |
|**400** | Sessão muito antiga (&gt;60 dias) ou já deletada |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet**
> { [key: string]: any; } getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet()

Calcula desvio entre focos planejados (microciclo) e executados (sessão)

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet(
    trainingSessionId,
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
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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
|**200** | Análise de desvio |  -  |
|**404** | Sessão não encontrada ou sem microciclo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet_0**
> { [key: string]: any; } getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet_0()

Calcula desvio entre focos planejados (microciclo) e executados (sessão)

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionDeviationApiV1TrainingSessionsTrainingSessionIdDeviationGet_0(
    trainingSessionId,
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
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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
|**200** | Análise de desvio |  -  |
|**404** | Sessão não encontrada ou sem microciclo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet**
> TrainingSession getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet()

Retorna detalhes de uma sessão de treino específica.  **Regras**: R25/R26 (permissões por papel e escopo).

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes da sessão |  -  |
|**401** | Token inválido ou ausente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet_0**
> TrainingSession getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet_0()

Retorna detalhes de uma sessão de treino específica.  **Regras**: R25/R26 (permissões por papel e escopo).

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingSessionByIdApiV1TrainingSessionsTrainingSessionIdGet_0(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes da sessão |  -  |
|**401** | Token inválido ou ausente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet**
> WellnessStatusResponse getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet()

Retorna status de wellness de todos atletas da sessão para dashboard do treinador

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessStatusResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Status de wellness da sessão |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet_0**
> WellnessStatusResponse getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet_0()

Retorna status de wellness de todos atletas da sessão para dashboard do treinador

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessStatusApiV1TrainingSessionsTrainingSessionIdWellnessStatusGet_0(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessStatusResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Status de wellness da sessão |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listTrainingSessionsApiV1TrainingSessionsGet**
> TrainingSessionPaginatedResponse listTrainingSessionsApiV1TrainingSessionsGet()

Lista paginada de sessões de treino.  **Regras**: R25/R26 (permissões por papel) - Ref: RDB14 - Paginação padrão  **Filtros disponíveis:** - team_id: Filtrar por time - season_id: Filtrar por temporada - start_date/end_date: Filtros de data

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; //Filtrar por time (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTrainingSessionsApiV1TrainingSessionsGet(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | Filtrar por time | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSessionPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de sessões |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listTrainingSessionsApiV1TrainingSessionsGet_0**
> TrainingSessionPaginatedResponse listTrainingSessionsApiV1TrainingSessionsGet_0()

Lista paginada de sessões de treino.  **Regras**: R25/R26 (permissões por papel) - Ref: RDB14 - Paginação padrão  **Filtros disponíveis:** - team_id: Filtrar por time - season_id: Filtrar por temporada - start_date/end_date: Filtros de data

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; //Filtrar por time (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTrainingSessionsApiV1TrainingSessionsGet_0(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | Filtrar por time | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSessionPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de sessões |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost**
> TrainingSession publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost()

Valida campos mínimos e publica a sessão para execução automática

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost(
    trainingSessionId,
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
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão publicada com sucesso |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Dados incompletos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost_0**
> TrainingSession publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost_0()

Valida campos mínimos e publica a sessão para execução automática

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.publishTrainingSessionApiV1TrainingSessionsTrainingSessionIdPublishPost_0(
    trainingSessionId,
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
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão publicada com sucesso |  -  |
|**404** | Sessão não encontrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Dados incompletos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost**
> TrainingSession restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost()

Restaura sessão de treino excluída.  **Regras**: RDB3 - Restore via nullify de deleted_at

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão restaurada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Sessão não está excluída |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost_0**
> TrainingSession restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost_0()

Restaura sessão de treino excluída.  **Regras**: RDB3 - Restore via nullify de deleted_at

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.restoreTrainingSessionApiV1TrainingSessionsTrainingSessionIdRestorePost_0(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão restaurada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Sessão não está excluída |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost**
> TrainingSession scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost(scopedTrainingSessionCreate)


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    ScopedTrainingSessionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let scopedTrainingSessionCreate: ScopedTrainingSessionCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost(
    teamId,
    scopedTrainingSessionCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scopedTrainingSessionCreate** | **ScopedTrainingSessionCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost_0**
> TrainingSession scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost_0(scopedTrainingSessionCreate)


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    ScopedTrainingSessionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let scopedTrainingSessionCreate: ScopedTrainingSessionCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedCreateTrainingSessionApiV1TeamsTeamIdTrainingsPost_0(
    teamId,
    scopedTrainingSessionCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scopedTrainingSessionCreate** | **ScopedTrainingSessionCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete**
> TrainingSession scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let reason: string; //Motivo da exclusao (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete(
    teamId,
    trainingId,
    reason,
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
| **trainingId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusao | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete_0**
> TrainingSession scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete_0()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let reason: string; //Motivo da exclusao (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdDelete_0(
    teamId,
    trainingId,
    reason,
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
| **trainingId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusao | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet**
> TrainingSession scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet(
    teamId,
    trainingId,
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
| **trainingId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet_0**
> TrainingSession scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet_0()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdGet_0(
    teamId,
    trainingId,
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
| **trainingId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet**
> TrainingSessionPaginatedResponse scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Numero da pagina (optional) (default to 1)
let limit: number; //Itens por pagina (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet(
    teamId,
    seasonId,
    startDate,
    endDate,
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
| **teamId** | [**string**] |  | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Numero da pagina | (optional) defaults to 1|
| **limit** | [**number**] | Itens por pagina | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSessionPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet_0**
> TrainingSessionPaginatedResponse scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet_0()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Numero da pagina (optional) (default to 1)
let limit: number; //Itens por pagina (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListTrainingSessionsApiV1TeamsTeamIdTrainingsGet_0(
    teamId,
    seasonId,
    startDate,
    endDate,
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
| **teamId** | [**string**] |  | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Numero da pagina | (optional) defaults to 1|
| **limit** | [**number**] | Itens por pagina | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSessionPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost**
> TrainingSession scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost(
    teamId,
    trainingId,
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
| **trainingId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost_0**
> TrainingSession scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost_0()


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedRestoreTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdRestorePost_0(
    teamId,
    trainingId,
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
| **trainingId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch**
> TrainingSession scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch(trainingSessionUpdate)


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    TrainingSessionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let trainingSessionUpdate: TrainingSessionUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch(
    teamId,
    trainingId,
    trainingSessionUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionUpdate** | **TrainingSessionUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **trainingId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch_0**
> TrainingSession scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch_0(trainingSessionUpdate)


### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    TrainingSessionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let teamId: string; // (default to undefined)
let trainingId: string; // (default to undefined)
let trainingSessionUpdate: TrainingSessionUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateTrainingSessionApiV1TeamsTeamIdTrainingsTrainingIdPatch_0(
    teamId,
    trainingId,
    trainingSessionUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionUpdate** | **TrainingSessionUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **trainingId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**403** | Forbidden |  -  |
|**404** | Not Found |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch**
> TrainingSession updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch(trainingSessionUpdate)

Atualiza campos editáveis de uma sessão de treino.  **Regras de edição (R40)**: - ≤10 minutos: autor pode editar livremente. - >10 min e ≤24h: exige perfil superior (admin/coordinator). - >24h: exige admin_note obrigatório para justificar edição tardia.  **Outras regras**: - R25/R26: Permissões por papel e escopo.

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    TrainingSessionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let trainingSessionUpdate: TrainingSessionUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch(
    trainingSessionId,
    trainingSessionUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionUpdate** | **TrainingSessionUpdate**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão atualizada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Janela de edição expirada (R40) |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch_0**
> TrainingSession updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch_0(trainingSessionUpdate)

Atualiza campos editáveis de uma sessão de treino.  **Regras de edição (R40)**: - ≤10 minutos: autor pode editar livremente. - >10 min e ≤24h: exige perfil superior (admin/coordinator). - >24h: exige admin_note obrigatório para justificar edição tardia.  **Outras regras**: - R25/R26: Permissões por papel e escopo.

### Example

```typescript
import {
    TrainingSessionsApi,
    Configuration,
    TrainingSessionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingSessionsApi(configuration);

let trainingSessionId: string; // (default to undefined)
let trainingSessionUpdate: TrainingSessionUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTrainingSessionApiV1TrainingSessionsTrainingSessionIdPatch_0(
    trainingSessionId,
    trainingSessionUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionUpdate** | **TrainingSessionUpdate**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingSession**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão atualizada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Janela de edição expirada (R40) |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

