# TrainingMicrocyclesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createTrainingMicrocycleApiV1TrainingMicrocyclesPost**](#createtrainingmicrocycleapiv1trainingmicrocyclespost) | **POST** /api/v1/training-microcycles | Cria novo microciclo de treinamento|
|[**createTrainingMicrocycleApiV1TrainingMicrocyclesPost_0**](#createtrainingmicrocycleapiv1trainingmicrocyclespost_0) | **POST** /api/v1/training-microcycles | Cria novo microciclo de treinamento|
|[**deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete**](#deletetrainingmicrocycleapiv1trainingmicrocyclesmicrocycleiddelete) | **DELETE** /api/v1/training-microcycles/{microcycle_id} | Remove microciclo de treinamento (soft delete)|
|[**deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete_0**](#deletetrainingmicrocycleapiv1trainingmicrocyclesmicrocycleiddelete_0) | **DELETE** /api/v1/training-microcycles/{microcycle_id} | Remove microciclo de treinamento (soft delete)|
|[**getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet**](#getcurrentmicrocycleapiv1trainingmicrocyclesteamsteamidcurrentget) | **GET** /api/v1/training-microcycles/teams/{team_id}/current | Busca microciclo da semana atual|
|[**getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet_0**](#getcurrentmicrocycleapiv1trainingmicrocyclesteamsteamidcurrentget_0) | **GET** /api/v1/training-microcycles/teams/{team_id}/current | Busca microciclo da semana atual|
|[**getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet**](#getmicrocyclesummaryapiv1trainingmicrocyclesmicrocycleidsummaryget) | **GET** /api/v1/training-microcycles/{microcycle_id}/summary | Resumo de execução do microciclo|
|[**getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet_0**](#getmicrocyclesummaryapiv1trainingmicrocyclesmicrocycleidsummaryget_0) | **GET** /api/v1/training-microcycles/{microcycle_id}/summary | Resumo de execução do microciclo|
|[**getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet**](#gettrainingmicrocycleapiv1trainingmicrocyclesmicrocycleidget) | **GET** /api/v1/training-microcycles/{microcycle_id} | Busca microciclo por ID|
|[**getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet_0**](#gettrainingmicrocycleapiv1trainingmicrocyclesmicrocycleidget_0) | **GET** /api/v1/training-microcycles/{microcycle_id} | Busca microciclo por ID|
|[**listTrainingMicrocyclesApiV1TrainingMicrocyclesGet**](#listtrainingmicrocyclesapiv1trainingmicrocyclesget) | **GET** /api/v1/training-microcycles | Lista microciclos de treinamento|
|[**listTrainingMicrocyclesApiV1TrainingMicrocyclesGet_0**](#listtrainingmicrocyclesapiv1trainingmicrocyclesget_0) | **GET** /api/v1/training-microcycles | Lista microciclos de treinamento|
|[**updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch**](#updatetrainingmicrocycleapiv1trainingmicrocyclesmicrocycleidpatch) | **PATCH** /api/v1/training-microcycles/{microcycle_id} | Atualiza microciclo de treinamento|
|[**updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch_0**](#updatetrainingmicrocycleapiv1trainingmicrocyclesmicrocycleidpatch_0) | **PATCH** /api/v1/training-microcycles/{microcycle_id} | Atualiza microciclo de treinamento|

# **createTrainingMicrocycleApiV1TrainingMicrocyclesPost**
> TrainingMicrocycleResponse createTrainingMicrocycleApiV1TrainingMicrocyclesPost(trainingMicrocycleCreate)

Cria um microciclo (planejamento semanal) com focos planejados

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration,
    TrainingMicrocycleCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let trainingMicrocycleCreate: TrainingMicrocycleCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTrainingMicrocycleApiV1TrainingMicrocyclesPost(
    trainingMicrocycleCreate,
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
| **trainingMicrocycleCreate** | **TrainingMicrocycleCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Microciclo criado com sucesso |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createTrainingMicrocycleApiV1TrainingMicrocyclesPost_0**
> TrainingMicrocycleResponse createTrainingMicrocycleApiV1TrainingMicrocyclesPost_0(trainingMicrocycleCreate)

Cria um microciclo (planejamento semanal) com focos planejados

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration,
    TrainingMicrocycleCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let trainingMicrocycleCreate: TrainingMicrocycleCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTrainingMicrocycleApiV1TrainingMicrocyclesPost_0(
    trainingMicrocycleCreate,
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
| **trainingMicrocycleCreate** | **TrainingMicrocycleCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Microciclo criado com sucesso |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete**
> deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete()

Marca microciclo como deletado sem remover do banco (soft delete)

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete(
    microcycleId,
    reason,
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
| **microcycleId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
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
|**204** | Microciclo deletado com sucesso |  -  |
|**404** | Microciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete_0**
> deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete_0()

Marca microciclo como deletado sem remover do banco (soft delete)

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdDelete_0(
    microcycleId,
    reason,
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
| **microcycleId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
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
|**204** | Microciclo deletado com sucesso |  -  |
|**404** | Microciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet**
> TrainingMicrocycleResponse getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet()

Retorna o microciclo ativo na semana atual de uma equipe

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let teamId: string; // (default to undefined)
let atDate: string; //Data de referência (YYYY-MM-DD). Default: hoje (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet(
    teamId,
    atDate,
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
| **atDate** | [**string**] | Data de referência (YYYY-MM-DD). Default: hoje | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Microciclo da semana atual |  -  |
|**404** | Nenhum microciclo ativo na semana |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet_0**
> TrainingMicrocycleResponse getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet_0()

Retorna o microciclo ativo na semana atual de uma equipe

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let teamId: string; // (default to undefined)
let atDate: string; //Data de referência (YYYY-MM-DD). Default: hoje (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCurrentMicrocycleApiV1TrainingMicrocyclesTeamsTeamIdCurrentGet_0(
    teamId,
    atDate,
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
| **atDate** | [**string**] | Data de referência (YYYY-MM-DD). Default: hoje | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Microciclo da semana atual |  -  |
|**404** | Nenhum microciclo ativo na semana |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet**
> { [key: string]: any; } getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet()

Retorna resumo analítico de planejado vs executado do microciclo

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet(
    microcycleId,
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
| **microcycleId** | [**string**] |  | defaults to undefined|
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
|**200** | Resumo de execução |  -  |
|**404** | Microciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet_0**
> { [key: string]: any; } getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet_0()

Retorna resumo analítico de planejado vs executado do microciclo

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMicrocycleSummaryApiV1TrainingMicrocyclesMicrocycleIdSummaryGet_0(
    microcycleId,
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
| **microcycleId** | [**string**] |  | defaults to undefined|
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
|**200** | Resumo de execução |  -  |
|**404** | Microciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet**
> TrainingMicrocycleWithSessions getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet()

Retorna detalhes de um microciclo específico com sessões relacionadas

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet(
    microcycleId,
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
| **microcycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleWithSessions**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Microciclo encontrado |  -  |
|**404** | Microciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet_0**
> TrainingMicrocycleWithSessions getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet_0()

Retorna detalhes de um microciclo específico com sessões relacionadas

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdGet_0(
    microcycleId,
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
| **microcycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleWithSessions**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Microciclo encontrado |  -  |
|**404** | Microciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listTrainingMicrocyclesApiV1TrainingMicrocyclesGet**
> Array<TrainingMicrocycleResponse> listTrainingMicrocyclesApiV1TrainingMicrocyclesGet()

Lista microciclos (planejamento semanal) de uma equipe com filtros opcionais

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let teamId: string; //ID da equipe (default to undefined)
let cycleId: string; //Filtro por mesociclo (optional) (default to undefined)
let startDate: string; //Data inicial do intervalo (YYYY-MM-DD) (optional) (default to undefined)
let endDate: string; //Data final do intervalo (YYYY-MM-DD) (optional) (default to undefined)
let includeDeleted: boolean; //Incluir microciclos deletados (optional) (default to false)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTrainingMicrocyclesApiV1TrainingMicrocyclesGet(
    teamId,
    cycleId,
    startDate,
    endDate,
    includeDeleted,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe | defaults to undefined|
| **cycleId** | [**string**] | Filtro por mesociclo | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial do intervalo (YYYY-MM-DD) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final do intervalo (YYYY-MM-DD) | (optional) defaults to undefined|
| **includeDeleted** | [**boolean**] | Incluir microciclos deletados | (optional) defaults to false|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingMicrocycleResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de microciclos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listTrainingMicrocyclesApiV1TrainingMicrocyclesGet_0**
> Array<TrainingMicrocycleResponse> listTrainingMicrocyclesApiV1TrainingMicrocyclesGet_0()

Lista microciclos (planejamento semanal) de uma equipe com filtros opcionais

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let teamId: string; //ID da equipe (default to undefined)
let cycleId: string; //Filtro por mesociclo (optional) (default to undefined)
let startDate: string; //Data inicial do intervalo (YYYY-MM-DD) (optional) (default to undefined)
let endDate: string; //Data final do intervalo (YYYY-MM-DD) (optional) (default to undefined)
let includeDeleted: boolean; //Incluir microciclos deletados (optional) (default to false)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTrainingMicrocyclesApiV1TrainingMicrocyclesGet_0(
    teamId,
    cycleId,
    startDate,
    endDate,
    includeDeleted,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe | defaults to undefined|
| **cycleId** | [**string**] | Filtro por mesociclo | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial do intervalo (YYYY-MM-DD) | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final do intervalo (YYYY-MM-DD) | (optional) defaults to undefined|
| **includeDeleted** | [**boolean**] | Incluir microciclos deletados | (optional) defaults to false|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingMicrocycleResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de microciclos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch**
> TrainingMicrocycleResponse updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch(trainingMicrocycleUpdate)

Atualiza campos específicos de um microciclo (atualização parcial)

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration,
    TrainingMicrocycleUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let trainingMicrocycleUpdate: TrainingMicrocycleUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch(
    microcycleId,
    trainingMicrocycleUpdate,
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
| **trainingMicrocycleUpdate** | **TrainingMicrocycleUpdate**|  | |
| **microcycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Microciclo atualizado com sucesso |  -  |
|**404** | Microciclo não encontrado |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch_0**
> TrainingMicrocycleResponse updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch_0(trainingMicrocycleUpdate)

Atualiza campos específicos de um microciclo (atualização parcial)

### Example

```typescript
import {
    TrainingMicrocyclesApi,
    Configuration,
    TrainingMicrocycleUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingMicrocyclesApi(configuration);

let microcycleId: string; // (default to undefined)
let trainingMicrocycleUpdate: TrainingMicrocycleUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTrainingMicrocycleApiV1TrainingMicrocyclesMicrocycleIdPatch_0(
    microcycleId,
    trainingMicrocycleUpdate,
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
| **trainingMicrocycleUpdate** | **TrainingMicrocycleUpdate**|  | |
| **microcycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingMicrocycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Microciclo atualizado com sucesso |  -  |
|**404** | Microciclo não encontrado |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

