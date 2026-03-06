# CompetitionSeasonsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createCompetitionSeasonForCompetition**](#createcompetitionseasonforcompetition) | **POST** /api/v1/competitions/{competition_id}/seasons | Criar vínculo competição ↔ temporada|
|[**createCompetitionSeasonForCompetition_0**](#createcompetitionseasonforcompetition_0) | **POST** /api/v1/competitions/{competition_id}/seasons | Criar vínculo competição ↔ temporada|
|[**getCompetitionSeasonById**](#getcompetitionseasonbyid) | **GET** /api/v1/competition_seasons/{competition_season_id} | Obter competition_season por ID|
|[**getCompetitionSeasonById_0**](#getcompetitionseasonbyid_0) | **GET** /api/v1/competition_seasons/{competition_season_id} | Obter competition_season por ID|
|[**listCompetitionSeasons**](#listcompetitionseasons) | **GET** /api/v1/competition_seasons | Listar competition_seasons (admin)|
|[**listCompetitionSeasonsByCompetition**](#listcompetitionseasonsbycompetition) | **GET** /api/v1/competitions/{competition_id}/seasons | Listar seasons de uma competição|
|[**listCompetitionSeasonsByCompetition_0**](#listcompetitionseasonsbycompetition_0) | **GET** /api/v1/competitions/{competition_id}/seasons | Listar seasons de uma competição|
|[**listCompetitionSeasons_0**](#listcompetitionseasons_0) | **GET** /api/v1/competition_seasons | Listar competition_seasons (admin)|
|[**updateCompetitionSeason**](#updatecompetitionseason) | **PATCH** /api/v1/competition_seasons/{competition_season_id} | Atualizar competition_season|
|[**updateCompetitionSeason_0**](#updatecompetitionseason_0) | **PATCH** /api/v1/competition_seasons/{competition_season_id} | Atualizar competition_season|

# **createCompetitionSeasonForCompetition**
> CompetitionSeason createCompetitionSeasonForCompetition(competitionSeasonCreate)

Cria um novo vínculo entre competição e temporada.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - RF4: Referência a temporadas (competition_seasons dependem de seasons válidas) - R29: Exclusão lógica (sem delete físico)  **Constraint:** UNIQUE (competition_id, season_id) - Violação retorna 409 conflict_unique  **Campos obrigatórios:** - season_id: UUID da temporada a vincular  **Erros possíveis:** - 404 not_found: Competição ou temporada não existe - 409 conflict_unique: Vínculo já existe para este par competition_id + season_id

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration,
    CompetitionSeasonCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionId: string; // (default to undefined)
let competitionSeasonCreate: CompetitionSeasonCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionSeasonForCompetition(
    competitionId,
    competitionSeasonCreate,
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
| **competitionSeasonCreate** | **CompetitionSeasonCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeason**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Vínculo criado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição ou temporada não encontrada |  -  |
|**409** | Violação de unicidade (competition_id + season_id) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createCompetitionSeasonForCompetition_0**
> CompetitionSeason createCompetitionSeasonForCompetition_0(competitionSeasonCreate)

Cria um novo vínculo entre competição e temporada.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - RF4: Referência a temporadas (competition_seasons dependem de seasons válidas) - R29: Exclusão lógica (sem delete físico)  **Constraint:** UNIQUE (competition_id, season_id) - Violação retorna 409 conflict_unique  **Campos obrigatórios:** - season_id: UUID da temporada a vincular  **Erros possíveis:** - 404 not_found: Competição ou temporada não existe - 409 conflict_unique: Vínculo já existe para este par competition_id + season_id

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration,
    CompetitionSeasonCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionId: string; // (default to undefined)
let competitionSeasonCreate: CompetitionSeasonCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionSeasonForCompetition_0(
    competitionId,
    competitionSeasonCreate,
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
| **competitionSeasonCreate** | **CompetitionSeasonCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeason**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Vínculo criado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição ou temporada não encontrada |  -  |
|**409** | Violação de unicidade (competition_id + season_id) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCompetitionSeasonById**
> CompetitionSeason getCompetitionSeasonById()

Retorna os detalhes de um vínculo competição ↔ temporada específico.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionSeasonId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionSeasonById(
    competitionSeasonId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionSeasonId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeason**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes do vínculo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Vínculo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCompetitionSeasonById_0**
> CompetitionSeason getCompetitionSeasonById_0()

Retorna os detalhes de um vínculo competição ↔ temporada específico.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionSeasonId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionSeasonById_0(
    competitionSeasonId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionSeasonId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeason**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Detalhes do vínculo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Vínculo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCompetitionSeasons**
> CompetitionSeasonPaginatedResponse listCompetitionSeasons()

Lista paginada de todos os vínculos competição ↔ temporada. Acesso administrativo (Coordenador/Dirigente).  **Regras aplicáveis:** - R25/R26: Permissões (somente Coordenador e Dirigente)  **Filtros disponíveis:** - competition_id: Filtrar por competição específica - season_id: Filtrar por temporada específica  **Paginação:** - page: Número da página (1-indexed) - limit: Itens por página (1-100, padrão 50)  **Envelope de resposta:** {items, page, limit, total}

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let competitionId: string; //Filtrar por competição (UUID) (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (UUID) (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionSeasons(
    page,
    limit,
    competitionId,
    seasonId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **competitionId** | [**string**] | Filtrar por competição (UUID) | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada (UUID) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeasonPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de vínculos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCompetitionSeasonsByCompetition**
> Array<CompetitionSeason> listCompetitionSeasonsByCompetition()

Lista temporadas vinculadas a uma competição específica.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - RF4: Referência a temporadas (criação de temporadas)  **Filtros disponíveis:** - season_id: Filtrar por temporada específica

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionId: string; // (default to undefined)
let seasonId: string; //Filtrar por temporada específica (UUID) (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionSeasonsByCompetition(
    competitionId,
    seasonId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada específica (UUID) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionSeason>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de temporadas da competição |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCompetitionSeasonsByCompetition_0**
> Array<CompetitionSeason> listCompetitionSeasonsByCompetition_0()

Lista temporadas vinculadas a uma competição específica.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - RF4: Referência a temporadas (criação de temporadas)  **Filtros disponíveis:** - season_id: Filtrar por temporada específica

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionId: string; // (default to undefined)
let seasonId: string; //Filtrar por temporada específica (UUID) (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionSeasonsByCompetition_0(
    competitionId,
    seasonId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada específica (UUID) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionSeason>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de temporadas da competição |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCompetitionSeasons_0**
> CompetitionSeasonPaginatedResponse listCompetitionSeasons_0()

Lista paginada de todos os vínculos competição ↔ temporada. Acesso administrativo (Coordenador/Dirigente).  **Regras aplicáveis:** - R25/R26: Permissões (somente Coordenador e Dirigente)  **Filtros disponíveis:** - competition_id: Filtrar por competição específica - season_id: Filtrar por temporada específica  **Paginação:** - page: Número da página (1-indexed) - limit: Itens por página (1-100, padrão 50)  **Envelope de resposta:** {items, page, limit, total}

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let competitionId: string; //Filtrar por competição (UUID) (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (UUID) (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionSeasons_0(
    page,
    limit,
    competitionId,
    seasonId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **competitionId** | [**string**] | Filtrar por competição (UUID) | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada (UUID) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeasonPaginatedResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de vínculos |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateCompetitionSeason**
> CompetitionSeason updateCompetitionSeason(competitionSeasonUpdate)

Atualiza campos permitidos de um vínculo competição ↔ temporada.  **Campos editáveis:** - name: Nome/descrição do vínculo  **Campos NÃO editáveis:** - competition_id (imutável) - season_id (imutável)  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R29: Exclusão lógica (sem delete físico)

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration,
    CompetitionSeasonUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionSeasonId: string; // (default to undefined)
let competitionSeasonUpdate: CompetitionSeasonUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCompetitionSeason(
    competitionSeasonId,
    competitionSeasonUpdate,
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
| **competitionSeasonUpdate** | **CompetitionSeasonUpdate**|  | |
| **competitionSeasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeason**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Vínculo atualizado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Vínculo não encontrado |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateCompetitionSeason_0**
> CompetitionSeason updateCompetitionSeason_0(competitionSeasonUpdate)

Atualiza campos permitidos de um vínculo competição ↔ temporada.  **Campos editáveis:** - name: Nome/descrição do vínculo  **Campos NÃO editáveis:** - competition_id (imutável) - season_id (imutável)  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - R29: Exclusão lógica (sem delete físico)

### Example

```typescript
import {
    CompetitionSeasonsApi,
    Configuration,
    CompetitionSeasonUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionSeasonsApi(configuration);

let competitionSeasonId: string; // (default to undefined)
let competitionSeasonUpdate: CompetitionSeasonUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCompetitionSeason_0(
    competitionSeasonId,
    competitionSeasonUpdate,
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
| **competitionSeasonUpdate** | **CompetitionSeasonUpdate**|  | |
| **competitionSeasonId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionSeason**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Vínculo atualizado com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Vínculo não encontrado |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

