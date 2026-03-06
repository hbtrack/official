# TrainingCyclesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createTrainingCycleApiV1TrainingCyclesPost**](#createtrainingcycleapiv1trainingcyclespost) | **POST** /api/v1/training-cycles | Cria novo ciclo de treinamento|
|[**createTrainingCycleApiV1TrainingCyclesPost_0**](#createtrainingcycleapiv1trainingcyclespost_0) | **POST** /api/v1/training-cycles | Cria novo ciclo de treinamento|
|[**deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete**](#deletetrainingcycleapiv1trainingcyclescycleiddelete) | **DELETE** /api/v1/training-cycles/{cycle_id} | Remove ciclo de treinamento (soft delete)|
|[**deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete_0**](#deletetrainingcycleapiv1trainingcyclescycleiddelete_0) | **DELETE** /api/v1/training-cycles/{cycle_id} | Remove ciclo de treinamento (soft delete)|
|[**getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet**](#getactivecyclesapiv1trainingcyclesteamsteamidactiveget) | **GET** /api/v1/training-cycles/teams/{team_id}/active | Busca ciclos ativos de uma equipe|
|[**getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet_0**](#getactivecyclesapiv1trainingcyclesteamsteamidactiveget_0) | **GET** /api/v1/training-cycles/teams/{team_id}/active | Busca ciclos ativos de uma equipe|
|[**getTrainingCycleApiV1TrainingCyclesCycleIdGet**](#gettrainingcycleapiv1trainingcyclescycleidget) | **GET** /api/v1/training-cycles/{cycle_id} | Busca ciclo por ID|
|[**getTrainingCycleApiV1TrainingCyclesCycleIdGet_0**](#gettrainingcycleapiv1trainingcyclescycleidget_0) | **GET** /api/v1/training-cycles/{cycle_id} | Busca ciclo por ID|
|[**listTrainingCyclesApiV1TrainingCyclesGet**](#listtrainingcyclesapiv1trainingcyclesget) | **GET** /api/v1/training-cycles | Lista ciclos de treinamento|
|[**listTrainingCyclesApiV1TrainingCyclesGet_0**](#listtrainingcyclesapiv1trainingcyclesget_0) | **GET** /api/v1/training-cycles | Lista ciclos de treinamento|
|[**updateTrainingCycleApiV1TrainingCyclesCycleIdPatch**](#updatetrainingcycleapiv1trainingcyclescycleidpatch) | **PATCH** /api/v1/training-cycles/{cycle_id} | Atualiza ciclo de treinamento|
|[**updateTrainingCycleApiV1TrainingCyclesCycleIdPatch_0**](#updatetrainingcycleapiv1trainingcyclescycleidpatch_0) | **PATCH** /api/v1/training-cycles/{cycle_id} | Atualiza ciclo de treinamento|

# **createTrainingCycleApiV1TrainingCyclesPost**
> TrainingCycleResponse createTrainingCycleApiV1TrainingCyclesPost(trainingCycleCreate)

Cria um macrociclo ou mesociclo com validações de hierarquia e datas

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration,
    TrainingCycleCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let trainingCycleCreate: TrainingCycleCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTrainingCycleApiV1TrainingCyclesPost(
    trainingCycleCreate,
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
| **trainingCycleCreate** | **TrainingCycleCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingCycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Ciclo criado com sucesso |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createTrainingCycleApiV1TrainingCyclesPost_0**
> TrainingCycleResponse createTrainingCycleApiV1TrainingCyclesPost_0(trainingCycleCreate)

Cria um macrociclo ou mesociclo com validações de hierarquia e datas

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration,
    TrainingCycleCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let trainingCycleCreate: TrainingCycleCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTrainingCycleApiV1TrainingCyclesPost_0(
    trainingCycleCreate,
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
| **trainingCycleCreate** | **TrainingCycleCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingCycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Ciclo criado com sucesso |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete**
> deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete()

Marca ciclo como deletado sem remover do banco (soft delete)

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let cycleId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete(
    cycleId,
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
| **cycleId** | [**string**] |  | defaults to undefined|
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
|**204** | Ciclo deletado com sucesso |  -  |
|**404** | Ciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete_0**
> deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete_0()

Marca ciclo como deletado sem remover do banco (soft delete)

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let cycleId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete_0(
    cycleId,
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
| **cycleId** | [**string**] |  | defaults to undefined|
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
|**204** | Ciclo deletado com sucesso |  -  |
|**404** | Ciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet**
> Array<TrainingCycleResponse> getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet()

Retorna ciclos ativos em uma data específica (default: hoje)

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let teamId: string; // (default to undefined)
let atDate: string; //Data de referência (YYYY-MM-DD) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet(
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
| **atDate** | [**string**] | Data de referência (YYYY-MM-DD) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingCycleResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de ciclos ativos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet_0**
> Array<TrainingCycleResponse> getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet_0()

Retorna ciclos ativos em uma data específica (default: hoje)

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let teamId: string; // (default to undefined)
let atDate: string; //Data de referência (YYYY-MM-DD) (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet_0(
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
| **atDate** | [**string**] | Data de referência (YYYY-MM-DD) | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingCycleResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de ciclos ativos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTrainingCycleApiV1TrainingCyclesCycleIdGet**
> TrainingCycleWithMicrocycles getTrainingCycleApiV1TrainingCyclesCycleIdGet()

Retorna detalhes de um ciclo específico com microciclos relacionados

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let cycleId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingCycleApiV1TrainingCyclesCycleIdGet(
    cycleId,
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
| **cycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingCycleWithMicrocycles**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Ciclo encontrado |  -  |
|**404** | Ciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTrainingCycleApiV1TrainingCyclesCycleIdGet_0**
> TrainingCycleWithMicrocycles getTrainingCycleApiV1TrainingCyclesCycleIdGet_0()

Retorna detalhes de um ciclo específico com microciclos relacionados

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let cycleId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingCycleApiV1TrainingCyclesCycleIdGet_0(
    cycleId,
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
| **cycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingCycleWithMicrocycles**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Ciclo encontrado |  -  |
|**404** | Ciclo não encontrado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listTrainingCyclesApiV1TrainingCyclesGet**
> Array<TrainingCycleResponse> listTrainingCyclesApiV1TrainingCyclesGet()

Lista macrociclos e mesociclos de uma equipe com filtros opcionais

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let teamId: string; // (optional) (default to undefined)
let cycleType: string; //Filtro por tipo: \'macro\' ou \'meso\' (optional) (default to undefined)
let status: string; //Filtro por status: \'active\', \'completed\', \'cancelled\' (optional) (default to undefined)
let includeDeleted: boolean; //Incluir ciclos deletados (optional) (default to false)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTrainingCyclesApiV1TrainingCyclesGet(
    teamId,
    cycleType,
    status,
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
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **cycleType** | [**string**] | Filtro por tipo: \&#39;macro\&#39; ou \&#39;meso\&#39; | (optional) defaults to undefined|
| **status** | [**string**] | Filtro por status: \&#39;active\&#39;, \&#39;completed\&#39;, \&#39;cancelled\&#39; | (optional) defaults to undefined|
| **includeDeleted** | [**boolean**] | Incluir ciclos deletados | (optional) defaults to false|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingCycleResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de ciclos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listTrainingCyclesApiV1TrainingCyclesGet_0**
> Array<TrainingCycleResponse> listTrainingCyclesApiV1TrainingCyclesGet_0()

Lista macrociclos e mesociclos de uma equipe com filtros opcionais

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let teamId: string; // (optional) (default to undefined)
let cycleType: string; //Filtro por tipo: \'macro\' ou \'meso\' (optional) (default to undefined)
let status: string; //Filtro por status: \'active\', \'completed\', \'cancelled\' (optional) (default to undefined)
let includeDeleted: boolean; //Incluir ciclos deletados (optional) (default to false)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTrainingCyclesApiV1TrainingCyclesGet_0(
    teamId,
    cycleType,
    status,
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
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **cycleType** | [**string**] | Filtro por tipo: \&#39;macro\&#39; ou \&#39;meso\&#39; | (optional) defaults to undefined|
| **status** | [**string**] | Filtro por status: \&#39;active\&#39;, \&#39;completed\&#39;, \&#39;cancelled\&#39; | (optional) defaults to undefined|
| **includeDeleted** | [**boolean**] | Incluir ciclos deletados | (optional) defaults to false|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingCycleResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de ciclos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateTrainingCycleApiV1TrainingCyclesCycleIdPatch**
> TrainingCycleResponse updateTrainingCycleApiV1TrainingCyclesCycleIdPatch(trainingCycleUpdate)

Atualiza campos específicos de um ciclo (atualização parcial)

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration,
    TrainingCycleUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let cycleId: string; // (default to undefined)
let trainingCycleUpdate: TrainingCycleUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTrainingCycleApiV1TrainingCyclesCycleIdPatch(
    cycleId,
    trainingCycleUpdate,
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
| **trainingCycleUpdate** | **TrainingCycleUpdate**|  | |
| **cycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingCycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Ciclo atualizado com sucesso |  -  |
|**404** | Ciclo não encontrado |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateTrainingCycleApiV1TrainingCyclesCycleIdPatch_0**
> TrainingCycleResponse updateTrainingCycleApiV1TrainingCyclesCycleIdPatch_0(trainingCycleUpdate)

Atualiza campos específicos de um ciclo (atualização parcial)

### Example

```typescript
import {
    TrainingCyclesApi,
    Configuration,
    TrainingCycleUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingCyclesApi(configuration);

let cycleId: string; // (default to undefined)
let trainingCycleUpdate: TrainingCycleUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTrainingCycleApiV1TrainingCyclesCycleIdPatch_0(
    cycleId,
    trainingCycleUpdate,
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
| **trainingCycleUpdate** | **TrainingCycleUpdate**|  | |
| **cycleId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TrainingCycleResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Ciclo atualizado com sucesso |  -  |
|**404** | Ciclo não encontrado |  -  |
|**400** | Dados inválidos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

