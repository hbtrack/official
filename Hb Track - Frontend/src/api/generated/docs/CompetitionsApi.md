# CompetitionsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createCompetition**](#createcompetition) | **POST** /api/v1/competitions | Criar competição|
|[**createCompetition_0**](#createcompetition_0) | **POST** /api/v1/competitions | Criar competição|
|[**getCompetitionById**](#getcompetitionbyid) | **GET** /api/v1/competitions/{competition_id} | Obter competição por ID|
|[**getCompetitionById_0**](#getcompetitionbyid_0) | **GET** /api/v1/competitions/{competition_id} | Obter competição por ID|
|[**listCompetitions**](#listcompetitions) | **GET** /api/v1/competitions | Listar competições|
|[**listCompetitions_0**](#listcompetitions_0) | **GET** /api/v1/competitions | Listar competições|
|[**updateCompetition**](#updatecompetition) | **PATCH** /api/v1/competitions/{competition_id} | Atualizar competição|
|[**updateCompetition_0**](#updatecompetition_0) | **PATCH** /api/v1/competitions/{competition_id} | Atualizar competição|

# **createCompetition**
> Competition createCompetition(competitionCreate)

Cria uma nova competição (registro base).  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R29: Exclusão lógica (sem delete físico) - R34: Clube único na V1 (organization_id do contexto)  **Campos obrigatórios:** - name: Nome da competição  **Campo kind:** Texto livre. Exemplos: \"official\", \"friendly\", \"training-game\"  **Nota:** A organização é determinada automaticamente pelo token de autenticação.

### Example

```typescript
import {
    CompetitionsApi,
    Configuration,
    CompetitionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let competitionCreate: CompetitionCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetition(
    competitionCreate,
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
| **competitionCreate** | **CompetitionCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Competition**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Competição criada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createCompetition_0**
> Competition createCompetition_0(competitionCreate)

Cria uma nova competição (registro base).  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R29: Exclusão lógica (sem delete físico) - R34: Clube único na V1 (organization_id do contexto)  **Campos obrigatórios:** - name: Nome da competição  **Campo kind:** Texto livre. Exemplos: \"official\", \"friendly\", \"training-game\"  **Nota:** A organização é determinada automaticamente pelo token de autenticação.

### Example

```typescript
import {
    CompetitionsApi,
    Configuration,
    CompetitionCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let competitionCreate: CompetitionCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetition_0(
    competitionCreate,
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
| **competitionCreate** | **CompetitionCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Competition**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Competição criada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCompetitionById**
> Competition getCompetitionById()

Retorna os detalhes de uma competição específica.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo

### Example

```typescript
import {
    CompetitionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let competitionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionById(
    competitionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Competition**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes da competição |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCompetitionById_0**
> Competition getCompetitionById_0()

Retorna os detalhes de uma competição específica.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo

### Example

```typescript
import {
    CompetitionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let competitionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionById_0(
    competitionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Competition**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes da competição |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCompetitions**
> CompetitionPaginatedResponse listCompetitions()

Lista paginada de competições da organização.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R34: Clube único na V1 (contexto implícito do token) - R42: Modo somente leitura sem vínculo ativo  **Filtros disponíveis:** - name: filtro por nome (case-insensitive, ilike) - kind: filtro por tipo de competição  **Ordenação:** - order_by: created_at (padrão), name, updated_at - order_dir: desc (padrão), asc  **Paginação:** - page: Número da página (1-indexed) - limit: Itens por página (1-100, padrão 50)  **Envelope de resposta:** {items, page, limit, total}

### Example

```typescript
import {
    CompetitionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let orderBy: string; //Campo para ordenação (optional) (default to 'created_at')
let orderDir: string; //Direção da ordenação (optional) (default to 'desc')
let name: string; //Filtro por nome (case-insensitive) (optional) (default to undefined)
let kind: string; //Filtro por tipo de competição (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitions(
    page,
    limit,
    orderBy,
    orderDir,
    name,
    kind,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **orderBy** | [**string**] | Campo para ordenação | (optional) defaults to 'created_at'|
| **orderDir** | [**string**] | Direção da ordenação | (optional) defaults to 'desc'|
| **name** | [**string**] | Filtro por nome (case-insensitive) | (optional) defaults to undefined|
| **kind** | [**string**] | Filtro por tipo de competição | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de competições |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCompetitions_0**
> CompetitionPaginatedResponse listCompetitions_0()

Lista paginada de competições da organização.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R34: Clube único na V1 (contexto implícito do token) - R42: Modo somente leitura sem vínculo ativo  **Filtros disponíveis:** - name: filtro por nome (case-insensitive, ilike) - kind: filtro por tipo de competição  **Ordenação:** - order_by: created_at (padrão), name, updated_at - order_dir: desc (padrão), asc  **Paginação:** - page: Número da página (1-indexed) - limit: Itens por página (1-100, padrão 50)  **Envelope de resposta:** {items, page, limit, total}

### Example

```typescript
import {
    CompetitionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let orderBy: string; //Campo para ordenação (optional) (default to 'created_at')
let orderDir: string; //Direção da ordenação (optional) (default to 'desc')
let name: string; //Filtro por nome (case-insensitive) (optional) (default to undefined)
let kind: string; //Filtro por tipo de competição (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitions_0(
    page,
    limit,
    orderBy,
    orderDir,
    name,
    kind,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **orderBy** | [**string**] | Campo para ordenação | (optional) defaults to 'created_at'|
| **orderDir** | [**string**] | Direção da ordenação | (optional) defaults to 'desc'|
| **name** | [**string**] | Filtro por nome (case-insensitive) | (optional) defaults to undefined|
| **kind** | [**string**] | Filtro por tipo de competição | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de competições |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateCompetition**
> Competition updateCompetition(competitionUpdate)

Atualiza campos permitidos de uma competição existente.  **Campos editáveis:** - name: Nome da competição - kind: Tipo da competição  **Campos NÃO editáveis:** - organization_id (imutável após criação)  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R29: Exclusão lógica (sem delete físico)

### Example

```typescript
import {
    CompetitionsApi,
    Configuration,
    CompetitionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let competitionId: string; // (default to undefined)
let competitionUpdate: CompetitionUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCompetition(
    competitionId,
    competitionUpdate,
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
| **competitionUpdate** | **CompetitionUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Competition**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Competição atualizada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateCompetition_0**
> Competition updateCompetition_0(competitionUpdate)

Atualiza campos permitidos de uma competição existente.  **Campos editáveis:** - name: Nome da competição - kind: Tipo da competição  **Campos NÃO editáveis:** - organization_id (imutável após criação)  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R29: Exclusão lógica (sem delete físico)

### Example

```typescript
import {
    CompetitionsApi,
    Configuration,
    CompetitionUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsApi(configuration);

let competitionId: string; // (default to undefined)
let competitionUpdate: CompetitionUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCompetition_0(
    competitionId,
    competitionUpdate,
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
| **competitionUpdate** | **CompetitionUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Competition**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Competição atualizada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

