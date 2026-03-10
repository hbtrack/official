# WellnessPreApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addWellnessPreToSessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPrePost**](#addwellnesspretosessionapiv1wellnesspretrainingsessionstrainingsessionidwellnessprepost) | **POST** /api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre | Registra wellness pré-treino|
|[**getWellnessPreByIdApiV1WellnessPreWellnessPreWellnessPreIdGet**](#getwellnessprebyidapiv1wellnessprewellnessprewellnesspreidget) | **GET** /api/v1/wellness-pre/wellness_pre/{wellness_pre_id} | Obtém wellness pré-treino por ID|
|[**getWellnessPreStatusApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreStatusGet**](#getwellnessprestatusapiv1wellnesspretrainingsessionstrainingsessionidwellnessprestatusget) | **GET** /api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre/status | Status de preenchimento do wellness pré|
|[**listWellnessPreBySessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreGet**](#listwellnessprebysessionapiv1wellnesspretrainingsessionstrainingsessionidwellnesspreget) | **GET** /api/v1/wellness-pre/training_sessions/{training_session_id}/wellness_pre | Lista wellness pré-treino da sessão|
|[**requestWellnessUnlockApiV1WellnessPreWellnessPreWellnessPreIdRequestUnlockPost**](#requestwellnessunlockapiv1wellnessprewellnessprewellnesspreidrequestunlockpost) | **POST** /api/v1/wellness-pre/wellness_pre/{wellness_pre_id}/request-unlock | Solicita desbloqueio de wellness pré após deadline|
|[**updateWellnessPreApiV1WellnessPreWellnessPreWellnessPreIdPatch**](#updatewellnesspreapiv1wellnessprewellnessprewellnesspreidpatch) | **PATCH** /api/v1/wellness-pre/wellness_pre/{wellness_pre_id} | Atualiza wellness pré-treino|

# **addWellnessPreToSessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPrePost**
> WellnessPre addWellnessPreToSessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPrePost(wellnessPreCreate)

Cria registro de wellness pré-treino para um atleta (1 por atleta por sessão).  **Regras**: - R22: Métricas operacionais. - RF5.2: Temporada interrompida bloqueia criação. - R25/R26: Permissões por papel e escopo.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada. - 409 conflict_unique: Wellness pré já registrado para este atleta nesta sessão. - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido ou FK inválida.

### Example

```typescript
import {
    WellnessPreApi,
    Configuration,
    WellnessPreCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPreApi(configuration);

let trainingSessionId: string; // (default to undefined)
let wellnessPreCreate: WellnessPreCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addWellnessPreToSessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPrePost(
    trainingSessionId,
    wellnessPreCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wellnessPreCreate** | **WellnessPreCreate**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessPre**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Wellness pré-treino registrado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**409** | Conflito (duplicidade ou temporada bloqueada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessPreByIdApiV1WellnessPreWellnessPreWellnessPreIdGet**
> WellnessPre getWellnessPreByIdApiV1WellnessPreWellnessPreWellnessPreIdGet()

Retorna detalhes de um registro de wellness pré-treino específico.  **Regras**: R25/R26 (permissões por papel e escopo).  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Wellness pré-treino não encontrado.

### Example

```typescript
import {
    WellnessPreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPreApi(configuration);

let wellnessPreId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessPreByIdApiV1WellnessPreWellnessPreWellnessPreIdGet(
    wellnessPreId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wellnessPreId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessPre**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes do wellness pré-treino |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Wellness pré-treino não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellnessPreStatusApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreStatusGet**
> { [key: string]: any; } getWellnessPreStatusApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreStatusGet()

Retorna status de preenchimento do wellness pré-treino.  **Resposta**: {     \"total_athletes\": 20,     \"responded_pre\": 15,     \"pending\": [athlete_id1, athlete_id2, ...],     \"response_rate\": 75.0 }

### Example

```typescript
import {
    WellnessPreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPreApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessPreStatusApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreStatusGet(
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

# **listWellnessPreBySessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreGet**
> Array<WellnessPre> listWellnessPreBySessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreGet()

Retorna lista de registros de wellness pré-treino para uma sessão.  **Regras**: R22 (métricas operacionais), R25/R26 (permissões).  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada.

### Example

```typescript
import {
    WellnessPreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPreApi(configuration);

let trainingSessionId: string; // (default to undefined)
let athleteId: string; //Filtrar por atleta (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listWellnessPreBySessionApiV1WellnessPreTrainingSessionsTrainingSessionIdWellnessPreGet(
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

**Array<WellnessPre>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de wellness pré-treino |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **requestWellnessUnlockApiV1WellnessPreWellnessPreWellnessPreIdRequestUnlockPost**
> { [key: string]: any; } requestWellnessUnlockApiV1WellnessPreWellnessPreWellnessPreIdRequestUnlockPost()

Atleta solicita desbloqueio de wellness pré após deadline.  Cria uma notificação para o staff (treinador/coordenador) com a solicitação. O staff pode então decidir se desbloqueia o wellness para edição.  **Regras**: - R40: Solicitação apenas após deadline (session_at - 2h) - Apenas o próprio atleta pode solicitar - Notificação enviada para staff da equipe  **Payload**: - reason: Motivo da solicitação (10-500 caracteres)  **Erros mapeados**: - 403 permission_denied: Não é o próprio atleta ou deadline não expirado - 404 not_found: Wellness pré-treino não encontrado - 422 validation_error: Razão inválida

### Example

```typescript
import {
    WellnessPreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPreApi(configuration);

let wellnessPreId: string; // (default to undefined)
let reason: string; //Motivo da solicitação (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.requestWellnessUnlockApiV1WellnessPreWellnessPreWellnessPreIdRequestUnlockPost(
    wellnessPreId,
    reason,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wellnessPreId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da solicitação | defaults to undefined|
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
|**200** | Solicitação enviada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Wellness pré-treino não encontrado |  -  |
|**422** | Erro de validação (razão obrigatória) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateWellnessPreApiV1WellnessPreWellnessPreWellnessPreIdPatch**
> WellnessPre updateWellnessPreApiV1WellnessPreWellnessPreWellnessPreIdPatch(wellnessPreUpdate)

Atualiza campos de wellness pré-treino. Não é possível alterar session_id, athlete_id, organization_id ou created_by_membership_id.  **Regras de edição (R40)**: - ≤10 minutos: autor pode editar livremente. - >10 min e ≤24h: exige perfil superior ou aprovação → 403 permission_denied. - >24h: somente leitura → 409 edit_window_expired.  **Outras regras**: - R41: Conflito de edição simultânea → 409 edit_conflict. - RF5.2/R37: Temporada bloqueada → 409 season_locked. - R25/R26: Permissões por papel e escopo.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente ou edição >10min sem perfil superior. - 404 not_found: Wellness pré-treino não encontrado. - 409 edit_window_expired: Janela de edição expirada (>24h). - 409 edit_conflict: Conflito de edição simultânea (R41). - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido.

### Example

```typescript
import {
    WellnessPreApi,
    Configuration,
    WellnessPreUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new WellnessPreApi(configuration);

let wellnessPreId: string; // (default to undefined)
let wellnessPreUpdate: WellnessPreUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateWellnessPreApiV1WellnessPreWellnessPreWellnessPreIdPatch(
    wellnessPreId,
    wellnessPreUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **wellnessPreUpdate** | **WellnessPreUpdate**|  | |
| **wellnessPreId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessPre**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Wellness pré-treino atualizado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Wellness pré-treino não encontrado |  -  |
|**409** | Janela de edição expirada (R40) ou conflito (R41) ou temporada bloqueada (RF5.2) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

