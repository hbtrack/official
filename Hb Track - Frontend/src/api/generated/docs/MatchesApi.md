# MatchesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**scopedCreateMatchApiV1TeamsTeamIdMatchesPost**](#scopedcreatematchapiv1teamsteamidmatchespost) | **POST** /api/v1/teams/{team_id}/matches | Criar partida (escopo equipe)|
|[**scopedCreateMatchApiV1TeamsTeamIdMatchesPost_0**](#scopedcreatematchapiv1teamsteamidmatchespost_0) | **POST** /api/v1/teams/{team_id}/matches | Criar partida (escopo equipe)|
|[**scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete**](#scopeddeletematchapiv1teamsteamidmatchesmatchiddelete) | **DELETE** /api/v1/teams/{team_id}/matches/{match_id} | Excluir partida (escopo equipe)|
|[**scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete_0**](#scopeddeletematchapiv1teamsteamidmatchesmatchiddelete_0) | **DELETE** /api/v1/teams/{team_id}/matches/{match_id} | Excluir partida (escopo equipe)|
|[**scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet**](#scopedgetmatchapiv1teamsteamidmatchesmatchidget) | **GET** /api/v1/teams/{team_id}/matches/{match_id} | Obter partida (escopo equipe)|
|[**scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet_0**](#scopedgetmatchapiv1teamsteamidmatchesmatchidget_0) | **GET** /api/v1/teams/{team_id}/matches/{match_id} | Obter partida (escopo equipe)|
|[**scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet**](#scopedgetmatchwitheventsapiv1teamsteamidmatchesmatchidwitheventsget) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/with-events | Obter partida com eventos (escopo equipe)|
|[**scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet_0**](#scopedgetmatchwitheventsapiv1teamsteamidmatchesmatchidwitheventsget_0) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/with-events | Obter partida com eventos (escopo equipe)|
|[**scopedListMatchesApiV1TeamsTeamIdMatchesGet**](#scopedlistmatchesapiv1teamsteamidmatchesget) | **GET** /api/v1/teams/{team_id}/matches | Listar partidas por equipe|
|[**scopedListMatchesApiV1TeamsTeamIdMatchesGet_0**](#scopedlistmatchesapiv1teamsteamidmatchesget_0) | **GET** /api/v1/teams/{team_id}/matches | Listar partidas por equipe|
|[**scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost**](#scopedrestorematchapiv1teamsteamidmatchesmatchidrestorepost) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/restore | Restaurar partida (escopo equipe)|
|[**scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost_0**](#scopedrestorematchapiv1teamsteamidmatchesmatchidrestorepost_0) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/restore | Restaurar partida (escopo equipe)|
|[**scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch**](#scopedupdatematchapiv1teamsteamidmatchesmatchidpatch) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id} | Atualizar partida (escopo equipe)|
|[**scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch_0**](#scopedupdatematchapiv1teamsteamidmatchesmatchidpatch_0) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id} | Atualizar partida (escopo equipe)|
|[**scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost**](#scopedupdatematchstatusapiv1teamsteamidmatchesmatchidstatuspost) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/status | Alterar status da partida (escopo equipe)|
|[**scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost_0**](#scopedupdatematchstatusapiv1teamsteamidmatchesmatchidstatuspost_0) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/status | Alterar status da partida (escopo equipe)|

# **scopedCreateMatchApiV1TeamsTeamIdMatchesPost**
> MatchResponse scopedCreateMatchApiV1TeamsTeamIdMatchesPost(matchCreate)


### Example

```typescript
import {
    MatchesApi,
    Configuration,
    MatchCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchCreate: MatchCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedCreateMatchApiV1TeamsTeamIdMatchesPost(
    teamId,
    matchCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchCreate** | **MatchCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**404** | Time não encontrado |  -  |
|**403** | Sem permissão |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedCreateMatchApiV1TeamsTeamIdMatchesPost_0**
> MatchResponse scopedCreateMatchApiV1TeamsTeamIdMatchesPost_0(matchCreate)


### Example

```typescript
import {
    MatchesApi,
    Configuration,
    MatchCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchCreate: MatchCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedCreateMatchApiV1TeamsTeamIdMatchesPost_0(
    teamId,
    matchCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchCreate** | **MatchCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**404** | Time não encontrado |  -  |
|**403** | Sem permissão |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete**
> MatchResponse scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**403** | Partida finalizada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete_0**
> MatchResponse scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete_0()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteMatchApiV1TeamsTeamIdMatchesMatchIdDelete_0(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**403** | Partida finalizada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet**
> MatchResponse scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet_0**
> MatchResponse scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet_0()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetMatchApiV1TeamsTeamIdMatchesMatchIdGet_0(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet**
> MatchWithEvents scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchWithEvents**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet_0**
> MatchWithEvents scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet_0()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetMatchWithEventsApiV1TeamsTeamIdMatchesMatchIdWithEventsGet_0(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchWithEvents**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedListMatchesApiV1TeamsTeamIdMatchesGet**
> MatchList scopedListMatchesApiV1TeamsTeamIdMatchesGet()

Lista partidas de uma equipe com filtros e paginação.

### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let status: AppModelsMatchMatchStatus; //Filtrar por status (optional) (default to undefined)
let page: number; //Página (optional) (default to 1)
let size: number; //Itens por página (optional) (default to 20)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchesApiV1TeamsTeamIdMatchesGet(
    teamId,
    seasonId,
    status,
    page,
    size,
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
| **status** | **AppModelsMatchMatchStatus** | Filtrar por status | (optional) defaults to undefined|
| **page** | [**number**] | Página | (optional) defaults to 1|
| **size** | [**number**] | Itens por página | (optional) defaults to 20|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchList**

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

# **scopedListMatchesApiV1TeamsTeamIdMatchesGet_0**
> MatchList scopedListMatchesApiV1TeamsTeamIdMatchesGet_0()

Lista partidas de uma equipe com filtros e paginação.

### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let status: AppModelsMatchMatchStatus; //Filtrar por status (optional) (default to undefined)
let page: number; //Página (optional) (default to 1)
let size: number; //Itens por página (optional) (default to 20)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchesApiV1TeamsTeamIdMatchesGet_0(
    teamId,
    seasonId,
    status,
    page,
    size,
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
| **status** | **AppModelsMatchMatchStatus** | Filtrar por status | (optional) defaults to undefined|
| **page** | [**number**] | Página | (optional) defaults to 1|
| **size** | [**number**] | Itens por página | (optional) defaults to 20|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchList**

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

# **scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost**
> MatchResponse scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**422** | Partida não está excluída |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost_0**
> MatchResponse scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost_0()


### Example

```typescript
import {
    MatchesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedRestoreMatchApiV1TeamsTeamIdMatchesMatchIdRestorePost_0(
    teamId,
    matchId,
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
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**422** | Partida não está excluída |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch**
> MatchResponse scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch(matchUpdate)


### Example

```typescript
import {
    MatchesApi,
    Configuration,
    MatchUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchUpdate: MatchUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch(
    teamId,
    matchId,
    matchUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchUpdate** | **MatchUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**403** | Partida finalizada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch_0**
> MatchResponse scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch_0(matchUpdate)


### Example

```typescript
import {
    MatchesApi,
    Configuration,
    MatchUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchUpdate: MatchUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchApiV1TeamsTeamIdMatchesMatchIdPatch_0(
    teamId,
    matchId,
    matchUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchUpdate** | **MatchUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**403** | Partida finalizada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost**
> MatchResponse scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost(matchStatusUpdate)


### Example

```typescript
import {
    MatchesApi,
    Configuration,
    MatchStatusUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchStatusUpdate: MatchStatusUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost(
    teamId,
    matchId,
    matchStatusUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchStatusUpdate** | **MatchStatusUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**403** | Transição não permitida |  -  |
|**422** | Dados inválidos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost_0**
> MatchResponse scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost_0(matchStatusUpdate)


### Example

```typescript
import {
    MatchesApi,
    Configuration,
    MatchStatusUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchesApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchStatusUpdate: MatchStatusUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchStatusApiV1TeamsTeamIdMatchesMatchIdStatusPost_0(
    teamId,
    matchId,
    matchStatusUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchStatusUpdate** | **MatchStatusUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**404** | Partida não encontrada |  -  |
|**403** | Transição não permitida |  -  |
|**422** | Dados inválidos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

