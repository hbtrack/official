# WellnessPostApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addWellnessPostToSessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostPost**](#addwellnessposttosessionapiv1wellnessposttrainingsessionstrainingsessionidwellnesspostpost) | **POST** /api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post | Registra wellness pós-treino|
|[**getWellnessPostByIdApiV1WellnessPostWellnessPostWellnessPostIdGet**](#getwellnesspostbyidapiv1wellnesspostwellnesspostwellnesspostidget) | **GET** /api/v1/wellness-post/wellness_post/{wellness_post_id} | Obtém wellness pós-treino por ID|
|[**getWellnessPostStatusApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostStatusGet**](#getwellnesspoststatusapiv1wellnessposttrainingsessionstrainingsessionidwellnesspoststatusget) | **GET** /api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post/status | Status de preenchimento do wellness pós|
|[**listWellnessPostBySessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostGet**](#listwellnesspostbysessionapiv1wellnessposttrainingsessionstrainingsessionidwellnesspostget) | **GET** /api/v1/wellness-post/training_sessions/{training_session_id}/wellness_post | Lista wellness pós-treino da sessão|
|[**updateWellnessPostApiV1WellnessPostWellnessPostWellnessPostIdPatch**](#updatewellnesspostapiv1wellnesspostwellnesspostwellnesspostidpatch) | **PATCH** /api/v1/wellness-post/wellness_post/{wellness_post_id} | Atualiza wellness pós-treino|

# **addWellnessPostToSessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostPost**
> WellnessPost addWellnessPostToSessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostPost(wellnessPostCreate)

Cria registro de wellness pós-treino para um atleta. O campo `internal_load` é calculado automaticamente: `minutes_effective × session_rpe`.  **Regras**: - R22: Métricas operacionais. - RF5.2: Temporada interrompida bloqueia criação. - R25/R26: Permissões por papel e escopo.  **Regra técnica**: O trigger `tr_calculate_internal_load` calcula `internal_load = minutes_effective * session_rpe` automaticamente no INSERT/UPDATE.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada. - 409 conflict_unique: Wellness pós já registrado para este atleta nesta sessão. - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido ou FK inválida.

### Example

```typescript
import {
    WellnessPostApi,
    Configuration,
    WellnessPostCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPostApi(configuration);

let trainingSessionId: string; // (default to undefined)
let wellnessPostCreate: WellnessPostCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addWellnessPostToSessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostPost(
    trainingSessionId,
    wellnessPostCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wellnessPostCreate** | **WellnessPostCreate**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessPost**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Wellness pós-treino registrado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**409** | Conflito (duplicidade ou temporada bloqueada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessPostByIdApiV1WellnessPostWellnessPostWellnessPostIdGet**
> WellnessPost getWellnessPostByIdApiV1WellnessPostWellnessPostWellnessPostIdGet()

Retorna detalhes de um registro de wellness pós-treino específico.  **Regras**: R25/R26 (permissões por papel e escopo).  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Wellness pós-treino não encontrado.

### Example

```typescript
import {
    WellnessPostApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPostApi(configuration);

let wellnessPostId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessPostByIdApiV1WellnessPostWellnessPostWellnessPostIdGet(
    wellnessPostId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wellnessPostId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessPost**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes do wellness pós-treino |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Wellness pós-treino não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessPostStatusApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostStatusGet**
> { [key: string]: any; } getWellnessPostStatusApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostStatusGet()

Retorna status de preenchimento do wellness pós-treino.

### Example

```typescript
import {
    WellnessPostApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPostApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessPostStatusApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostStatusGet(
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

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Status de preenchimento |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas treinadores) |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listWellnessPostBySessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostGet**
> Array<WellnessPost> listWellnessPostBySessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostGet()

Retorna lista de registros de wellness pós-treino para uma sessão.  **Regras**: R22 (métricas operacionais), R25/R26 (permissões).  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada.

### Example

```typescript
import {
    WellnessPostApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPostApi(configuration);

let trainingSessionId: string; // (default to undefined)
let athleteId: string; //Filtrar por atleta (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWellnessPostBySessionApiV1WellnessPostTrainingSessionsTrainingSessionIdWellnessPostGet(
    trainingSessionId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] | Filtrar por atleta | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<WellnessPost>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de wellness pós-treino |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateWellnessPostApiV1WellnessPostWellnessPostWellnessPostIdPatch**
> WellnessPost updateWellnessPostApiV1WellnessPostWellnessPostWellnessPostIdPatch(wellnessPostUpdate)

Atualiza campos de wellness pós-treino. O campo `internal_load` é recalculado automaticamente quando `minutes_effective` ou `session_rpe` são alterados. Não é possível alterar session_id, athlete_id, organization_id ou created_by_membership_id.  **Regra técnica**: O trigger `tr_calculate_internal_load` recalcula `internal_load = minutes_effective * session_rpe` automaticamente no UPDATE.  **Regras de edição (R40)**: - ≤10 minutos: autor pode editar livremente. - >10 min e ≤24h: exige perfil superior ou aprovação → 403 permission_denied. - >24h: somente leitura → 409 edit_window_expired.  **Outras regras**: - R41: Conflito de edição simultânea → 409 edit_conflict. - RF5.2/R37: Temporada bloqueada → 409 season_locked. - R25/R26: Permissões por papel e escopo.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente ou edição >10min sem perfil superior. - 404 not_found: Wellness pós-treino não encontrado. - 409 edit_window_expired: Janela de edição expirada (>24h). - 409 edit_conflict: Conflito de edição simultânea (R41). - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido.

### Example

```typescript
import {
    WellnessPostApi,
    Configuration,
    WellnessPostUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPostApi(configuration);

let wellnessPostId: string; // (default to undefined)
let wellnessPostUpdate: WellnessPostUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWellnessPostApiV1WellnessPostWellnessPostWellnessPostIdPatch(
    wellnessPostId,
    wellnessPostUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wellnessPostUpdate** | **WellnessPostUpdate**|  | |
| **wellnessPostId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessPost**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Wellness pós-treino atualizado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Wellness pós-treino não encontrado |  -  |
|**409** | Janela de edição expirada (R40) ou conflito (R41) ou temporada bloqueada (RF5.2) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

