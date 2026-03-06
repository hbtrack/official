# MatchTeamsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost**](#addteamtomatchapiv1matchesmatchesmatchidteamspost) | **POST** /api/v1/matches/matches/{match_id}/teams | Adicionar equipe ao jogo|
|[**addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost_0**](#addteamtomatchapiv1matchesmatchesmatchidteamspost_0) | **POST** /api/v1/matches/matches/{match_id}/teams | Adicionar equipe ao jogo|
|[**listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet**](#listmatchteamsapiv1matchesmatchesmatchidteamsget) | **GET** /api/v1/matches/matches/{match_id}/teams | Listar equipes do jogo|
|[**listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet_0**](#listmatchteamsapiv1matchesmatchesmatchidteamsget_0) | **GET** /api/v1/matches/matches/{match_id}/teams | Listar equipes do jogo|
|[**scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost**](#scopedaddteamtomatchapiv1teamsteamidmatchesmatchidteamspost) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/teams | Adicionar equipe ao jogo (escopo equipe)|
|[**scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost_0**](#scopedaddteamtomatchapiv1teamsteamidmatchesmatchidteamspost_0) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/teams | Adicionar equipe ao jogo (escopo equipe)|
|[**scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet**](#scopedlistmatchteamsapiv1teamsteamidmatchesmatchidteamsget) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/teams | Listar equipes do jogo (escopo equipe)|
|[**scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet_0**](#scopedlistmatchteamsapiv1teamsteamidmatchesmatchidteamsget_0) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/teams | Listar equipes do jogo (escopo equipe)|
|[**scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch**](#scopedupdatematchteamapiv1teamsteamidmatchesmatchidteamssidepatch) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id}/teams/{side} | Atualizar equipe do jogo por lado (escopo equipe)|
|[**scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch_0**](#scopedupdatematchteamapiv1teamsteamidmatchesmatchidteamssidepatch_0) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id}/teams/{side} | Atualizar equipe do jogo por lado (escopo equipe)|
|[**updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch**](#updatematchteamapiv1matchesmatchteamsmatchteamidpatch) | **PATCH** /api/v1/matches/match_teams/{match_team_id} | Atualizar equipe do jogo|
|[**updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch_0**](#updatematchteamapiv1matchesmatchteamsmatchteamidpatch_0) | **PATCH** /api/v1/matches/match_teams/{match_team_id} | Atualizar equipe do jogo|

# **addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost**
> MatchTeam addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost(matchTeamCreate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let matchId: string; // (default to undefined)
let matchTeamCreate: MatchTeamCreate; //

const { status, data } = await apiInstance.addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost(
    matchId,
    matchTeamCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamCreate** | **MatchTeamCreate**|  | |
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**MatchTeam**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost_0**
> MatchTeam addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost_0(matchTeamCreate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let matchId: string; // (default to undefined)
let matchTeamCreate: MatchTeamCreate; //

const { status, data } = await apiInstance.addTeamToMatchApiV1MatchesMatchesMatchIdTeamsPost_0(
    matchId,
    matchTeamCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamCreate** | **MatchTeamCreate**|  | |
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**MatchTeam**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet**
> Array<MatchTeam> listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet()


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let matchId: string; // (default to undefined)

const { status, data } = await apiInstance.listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet(
    matchId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**Array<MatchTeam>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de equipes do jogo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet_0**
> Array<MatchTeam> listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet_0()


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let matchId: string; // (default to undefined)

const { status, data } = await apiInstance.listMatchTeamsApiV1MatchesMatchesMatchIdTeamsGet_0(
    matchId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**Array<MatchTeam>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de equipes do jogo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost**
> MatchTeam scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost(matchTeamCreate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchTeamCreate: MatchTeamCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost(
    teamId,
    matchId,
    matchTeamCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamCreate** | **MatchTeamCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchTeam**

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

# **scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost_0**
> MatchTeam scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost_0(matchTeamCreate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchTeamCreate: MatchTeamCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedAddTeamToMatchApiV1TeamsTeamIdMatchesMatchIdTeamsPost_0(
    teamId,
    matchId,
    matchTeamCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamCreate** | **MatchTeamCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchTeam**

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

# **scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet**
> Array<MatchTeam> scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet()


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet(
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

**Array<MatchTeam>**

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

# **scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet_0**
> Array<MatchTeam> scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet_0()


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchTeamsApiV1TeamsTeamIdMatchesMatchIdTeamsGet_0(
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

**Array<MatchTeam>**

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

# **scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch**
> MatchTeam scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch(matchTeamUpdate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let side: string; // (default to undefined)
let matchTeamUpdate: MatchTeamUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch(
    teamId,
    matchId,
    side,
    matchTeamUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamUpdate** | **MatchTeamUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **side** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchTeam**

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

# **scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch_0**
> MatchTeam scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch_0(matchTeamUpdate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let side: string; // (default to undefined)
let matchTeamUpdate: MatchTeamUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchTeamApiV1TeamsTeamIdMatchesMatchIdTeamsSidePatch_0(
    teamId,
    matchId,
    side,
    matchTeamUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamUpdate** | **MatchTeamUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **side** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchTeam**

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

# **updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch**
> MatchTeam updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch(matchTeamUpdate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let matchTeamId: string; // (default to undefined)
let matchTeamUpdate: MatchTeamUpdate; //

const { status, data } = await apiInstance.updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch(
    matchTeamId,
    matchTeamUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamUpdate** | **MatchTeamUpdate**|  | |
| **matchTeamId** | [**string**] |  | defaults to undefined|


### Return type

**MatchTeam**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch_0**
> MatchTeam updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch_0(matchTeamUpdate)


### Example

```typescript
import {
    MatchTeamsApi,
    Configuration,
    MatchTeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchTeamsApi(configuration);

let matchTeamId: string; // (default to undefined)
let matchTeamUpdate: MatchTeamUpdate; //

const { status, data } = await apiInstance.updateMatchTeamApiV1MatchesMatchTeamsMatchTeamIdPatch_0(
    matchTeamId,
    matchTeamUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchTeamUpdate** | **MatchTeamUpdate**|  | |
| **matchTeamId** | [**string**] |  | defaults to undefined|


### Return type

**MatchTeam**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

