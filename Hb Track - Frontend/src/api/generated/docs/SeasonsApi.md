# SeasonsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**cancelSeason**](#cancelseason) | **POST** /api/v1/seasons/{season_id}/cancel | Cancelar temporada|
|[**cancelSeason_0**](#cancelseason_0) | **POST** /api/v1/seasons/{season_id}/cancel | Cancelar temporada|
|[**createSeason**](#createseason) | **POST** /api/v1/seasons | Criar temporada|
|[**createSeason_0**](#createseason_0) | **POST** /api/v1/seasons | Criar temporada|
|[**deleteSeason**](#deleteseason) | **DELETE** /api/v1/seasons/{season_id} | Excluir temporada (soft delete)|
|[**deleteSeason_0**](#deleteseason_0) | **DELETE** /api/v1/seasons/{season_id} | Excluir temporada (soft delete)|
|[**getSeason**](#getseason) | **GET** /api/v1/seasons/{season_id} | Obter temporada|
|[**getSeason_0**](#getseason_0) | **GET** /api/v1/seasons/{season_id} | Obter temporada|
|[**interruptSeason**](#interruptseason) | **POST** /api/v1/seasons/{season_id}/interrupt | Interromper temporada|
|[**interruptSeason_0**](#interruptseason_0) | **POST** /api/v1/seasons/{season_id}/interrupt | Interromper temporada|
|[**updateSeason**](#updateseason) | **PATCH** /api/v1/seasons/{season_id} | Atualizar temporada|
|[**updateSeason_0**](#updateseason_0) | **PATCH** /api/v1/seasons/{season_id} | Atualizar temporada|

# **cancelSeason**
> AppSchemasSeasonsSeasonResponse cancelSeason(reasonRequest)

Cancela uma temporada antes do início.  **Regras:** - RF5.1: Cancelamento permitido apenas se a temporada não possuir dados vinculados - 6.1.1: Status muda para \"cancelada\"  **Pré-condições:** - Temporada deve estar em status \"planejada\" (antes de start_date) - Não pode haver dados vinculados (equipes, jogos, treinos, etc.)  **Payload obrigatório:** { \"reason\": \"...\" }

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    ReasonRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let reasonRequest: ReasonRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelSeason(
    seasonId,
    reasonRequest,
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
| **reasonRequest** | **ReasonRequest**|  | |
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Temporada cancelada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**409** | Conflito - temporada não pode ser cancelada |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancelSeason_0**
> AppSchemasSeasonsSeasonResponse cancelSeason_0(reasonRequest)

Cancela uma temporada antes do início.  **Regras:** - RF5.1: Cancelamento permitido apenas se a temporada não possuir dados vinculados - 6.1.1: Status muda para \"cancelada\"  **Pré-condições:** - Temporada deve estar em status \"planejada\" (antes de start_date) - Não pode haver dados vinculados (equipes, jogos, treinos, etc.)  **Payload obrigatório:** { \"reason\": \"...\" }

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    ReasonRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let reasonRequest: ReasonRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelSeason_0(
    seasonId,
    reasonRequest,
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
| **reasonRequest** | **ReasonRequest**|  | |
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Temporada cancelada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**409** | Conflito - temporada não pode ser cancelada |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createSeason**
> AppSchemasSeasonsSeasonResponse createSeason(seasonCreate)

Cria uma nova temporada.  **Regras:** - RF4: Dirigentes, Coordenadores e Treinadores podem criar temporadas - R25/R26: Permissões por papel - RDB8: start_date < end_date (validado pelo DB) - 6.1.1: Status inicial será \"planejada\" (se start_date > hoje)

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    SeasonCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonCreate: SeasonCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSeason(
    seasonCreate,
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
| **seasonCreate** | **SeasonCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Temporada criada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createSeason_0**
> AppSchemasSeasonsSeasonResponse createSeason_0(seasonCreate)

Cria uma nova temporada.  **Regras:** - RF4: Dirigentes, Coordenadores e Treinadores podem criar temporadas - R25/R26: Permissões por papel - RDB8: start_date < end_date (validado pelo DB) - 6.1.1: Status inicial será \"planejada\" (se start_date > hoje)

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    SeasonCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonCreate: SeasonCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSeason_0(
    seasonCreate,
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
| **seasonCreate** | **SeasonCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Temporada criada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteSeason**
> deleteSeason()

Cancela uma temporada planejada (RF5.1).  **Regras:** - RF5.1: Apenas temporada planejada e sem dados vinculados - R25/R26: Permissões por papel

### Example

```typescript
import {
    SeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSeason(
    seasonId,
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
| **seasonId** | [**string**] |  | defaults to undefined|
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
|**204** | Temporada excluída |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteSeason_0**
> deleteSeason_0()

Cancela uma temporada planejada (RF5.1).  **Regras:** - RF5.1: Apenas temporada planejada e sem dados vinculados - R25/R26: Permissões por papel

### Example

```typescript
import {
    SeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSeason_0(
    seasonId,
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
| **seasonId** | [**string**] |  | defaults to undefined|
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
|**204** | Temporada excluída |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSeason**
> AppSchemasSeasonsSeasonResponse getSeason()

Retorna detalhes de uma temporada específica.  **Regras:** R25/R26 (permissões por papel)  **Response inclui:** - status derivado conforme 6.1.1 - deleted_at/deleted_reason se soft-deleted (RDB4)

### Example

```typescript
import {
    SeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSeason(
    seasonId,
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
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes da temporada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSeason_0**
> AppSchemasSeasonsSeasonResponse getSeason_0()

Retorna detalhes de uma temporada específica.  **Regras:** R25/R26 (permissões por papel)  **Response inclui:** - status derivado conforme 6.1.1 - deleted_at/deleted_reason se soft-deleted (RDB4)

### Example

```typescript
import {
    SeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSeason_0(
    seasonId,
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
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes da temporada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **interruptSeason**
> AppSchemasSeasonsSeasonResponse interruptSeason(reasonRequest)

Interrompe uma temporada ativa por força maior.  **Regras:** - RF5.2: Interrupção após início (força maior) - R37: Bloqueia criação/edição de novos eventos após interrupção - 6.1.1: Status muda para \"interrompida\"  **Pré-condições:** - Temporada deve estar em status \"ativa\"  **Payload obrigatório:** { \"reason\": \"...\" }

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    ReasonRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let reasonRequest: ReasonRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.interruptSeason(
    seasonId,
    reasonRequest,
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
| **reasonRequest** | **ReasonRequest**|  | |
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Temporada interrompida |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**409** | invalid_state_transition - Temporada não está ativa |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **interruptSeason_0**
> AppSchemasSeasonsSeasonResponse interruptSeason_0(reasonRequest)

Interrompe uma temporada ativa por força maior.  **Regras:** - RF5.2: Interrupção após início (força maior) - R37: Bloqueia criação/edição de novos eventos após interrupção - 6.1.1: Status muda para \"interrompida\"  **Pré-condições:** - Temporada deve estar em status \"ativa\"  **Payload obrigatório:** { \"reason\": \"...\" }

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    ReasonRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let reasonRequest: ReasonRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.interruptSeason_0(
    seasonId,
    reasonRequest,
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
| **reasonRequest** | **ReasonRequest**|  | |
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Temporada interrompida |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**409** | invalid_state_transition - Temporada não está ativa |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateSeason**
> AppSchemasSeasonsSeasonResponse updateSeason(seasonUpdate)

Atualiza parcialmente uma temporada.  **Regras:** - RF5: Não permite encerramento manual após início - RF5.2: NÃO editar se interrompida - R37: Após encerramento, edição só via ação administrativa auditada - RDB4: Soft delete via deleted_at/deleted_reason (não DELETE físico) - 6.1.1: Status é derivado, não editável diretamente

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    SeasonUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let seasonUpdate: SeasonUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSeason(
    seasonId,
    seasonUpdate,
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
| **seasonUpdate** | **SeasonUpdate**|  | |
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Temporada atualizada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**409** | season_locked - Temporada interrompida (RF5.2/R37) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateSeason_0**
> AppSchemasSeasonsSeasonResponse updateSeason_0(seasonUpdate)

Atualiza parcialmente uma temporada.  **Regras:** - RF5: Não permite encerramento manual após início - RF5.2: NÃO editar se interrompida - R37: Após encerramento, edição só via ação administrativa auditada - RDB4: Soft delete via deleted_at/deleted_reason (não DELETE físico) - 6.1.1: Status é derivado, não editável diretamente

### Example

```typescript
import {
    SeasonsApi,
    Configuration,
    SeasonUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new SeasonsApi(configuration);

let seasonId: string; // (default to undefined)
let seasonUpdate: SeasonUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSeason_0(
    seasonId,
    seasonUpdate,
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
| **seasonUpdate** | **SeasonUpdate**|  | |
| **seasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasSeasonsSeasonResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Temporada atualizada |  -  |
|**401** | Credencial ausente ou inválida |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Temporada não encontrada |  -  |
|**409** | season_locked - Temporada interrompida (RF5.2/R37) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

