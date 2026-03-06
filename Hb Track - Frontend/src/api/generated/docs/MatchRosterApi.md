# MatchRosterApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost**](#addathletetomatchapiv1matchesmatchesmatchidrosterpost) | **POST** /api/v1/matches/matches/{match_id}/roster | Adicionar atleta ao roster|
|[**addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost_0**](#addathletetomatchapiv1matchesmatchesmatchidrosterpost_0) | **POST** /api/v1/matches/matches/{match_id}/roster | Adicionar atleta ao roster|
|[**listMatchRosterApiV1MatchesMatchesMatchIdRosterGet**](#listmatchrosterapiv1matchesmatchesmatchidrosterget) | **GET** /api/v1/matches/matches/{match_id}/roster | Listar roster do jogo|
|[**listMatchRosterApiV1MatchesMatchesMatchIdRosterGet_0**](#listmatchrosterapiv1matchesmatchesmatchidrosterget_0) | **GET** /api/v1/matches/matches/{match_id}/roster | Listar roster do jogo|
|[**scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost**](#scopedaddathletetomatchapiv1teamsteamidmatchesmatchidrosterpost) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/roster | Adicionar atleta ao roster (escopo equipe)|
|[**scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost_0**](#scopedaddathletetomatchapiv1teamsteamidmatchesmatchidrosterpost_0) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/roster | Adicionar atleta ao roster (escopo equipe)|
|[**scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete**](#scopeddeletefromrosterapiv1teamsteamidmatchesmatchidrosterathleteiddelete) | **DELETE** /api/v1/teams/{team_id}/matches/{match_id}/roster/{athlete_id} | Remover atleta do roster (escopo equipe)|
|[**scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete_0**](#scopeddeletefromrosterapiv1teamsteamidmatchesmatchidrosterathleteiddelete_0) | **DELETE** /api/v1/teams/{team_id}/matches/{match_id}/roster/{athlete_id} | Remover atleta do roster (escopo equipe)|
|[**scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet**](#scopedlistmatchrosterapiv1teamsteamidmatchesmatchidrosterget) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/roster | Listar roster do jogo (escopo equipe)|
|[**scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet_0**](#scopedlistmatchrosterapiv1teamsteamidmatchesmatchidrosterget_0) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/roster | Listar roster do jogo (escopo equipe)|
|[**scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch**](#scopedupdatematchrosterapiv1teamsteamidmatchesmatchidrosterrosteridpatch) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id}/roster/{roster_id} | Atualizar entrada do roster (escopo equipe)|
|[**scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch_0**](#scopedupdatematchrosterapiv1teamsteamidmatchesmatchidrosterrosteridpatch_0) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id}/roster/{roster_id} | Atualizar entrada do roster (escopo equipe)|
|[**updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch**](#updatematchrosterapiv1matchesmatchrostermatchrosteridpatch) | **PATCH** /api/v1/matches/match_roster/{match_roster_id} | Atualizar entrada do roster|
|[**updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch_0**](#updatematchrosterapiv1matchesmatchrostermatchrosteridpatch_0) | **PATCH** /api/v1/matches/match_roster/{match_roster_id} | Atualizar entrada do roster|

# **addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost**
> MatchRoster addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost(matchRosterCreate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let matchId: string; // (default to undefined)
let matchRosterCreate: MatchRosterCreate; //

const { status, data } = await apiInstance.addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost(
    matchId,
    matchRosterCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterCreate** | **MatchRosterCreate**|  | |
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**MatchRoster**

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

# **addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost_0**
> MatchRoster addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost_0(matchRosterCreate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let matchId: string; // (default to undefined)
let matchRosterCreate: MatchRosterCreate; //

const { status, data } = await apiInstance.addAthleteToMatchApiV1MatchesMatchesMatchIdRosterPost_0(
    matchId,
    matchRosterCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterCreate** | **MatchRosterCreate**|  | |
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**MatchRoster**

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

# **listMatchRosterApiV1MatchesMatchesMatchIdRosterGet**
> Array<MatchRoster> listMatchRosterApiV1MatchesMatchesMatchIdRosterGet()


### Example

```typescript
import {
    MatchRosterApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let matchId: string; // (default to undefined)

const { status, data } = await apiInstance.listMatchRosterApiV1MatchesMatchesMatchIdRosterGet(
    matchId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**Array<MatchRoster>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de atletas do jogo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listMatchRosterApiV1MatchesMatchesMatchIdRosterGet_0**
> Array<MatchRoster> listMatchRosterApiV1MatchesMatchesMatchIdRosterGet_0()


### Example

```typescript
import {
    MatchRosterApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let matchId: string; // (default to undefined)

const { status, data } = await apiInstance.listMatchRosterApiV1MatchesMatchesMatchIdRosterGet_0(
    matchId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|


### Return type

**Array<MatchRoster>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de atletas do jogo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost**
> MatchRoster scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost(matchRosterCreate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchRosterCreate: MatchRosterCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost(
    teamId,
    matchId,
    matchRosterCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterCreate** | **MatchRosterCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchRoster**

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

# **scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost_0**
> MatchRoster scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost_0(matchRosterCreate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchRosterCreate: MatchRosterCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedAddAthleteToMatchApiV1TeamsTeamIdMatchesMatchIdRosterPost_0(
    teamId,
    matchId,
    matchRosterCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterCreate** | **MatchRosterCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchRoster**

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

# **scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete**
> { [key: string]: any; } scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete()


### Example

```typescript
import {
    MatchRosterApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete(
    teamId,
    matchId,
    athleteId,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
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
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete_0**
> { [key: string]: any; } scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete_0()


### Example

```typescript
import {
    MatchRosterApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteFromRosterApiV1TeamsTeamIdMatchesMatchIdRosterAthleteIdDelete_0(
    teamId,
    matchId,
    athleteId,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
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
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet**
> Array<MatchRoster> scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet()


### Example

```typescript
import {
    MatchRosterApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet(
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

**Array<MatchRoster>**

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

# **scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet_0**
> Array<MatchRoster> scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet_0()


### Example

```typescript
import {
    MatchRosterApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterGet_0(
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

**Array<MatchRoster>**

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

# **scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch**
> MatchRoster scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch(matchRosterUpdate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let rosterId: string; // (default to undefined)
let matchRosterUpdate: MatchRosterUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch(
    teamId,
    matchId,
    rosterId,
    matchRosterUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterUpdate** | **MatchRosterUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **rosterId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchRoster**

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

# **scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch_0**
> MatchRoster scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch_0(matchRosterUpdate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let rosterId: string; // (default to undefined)
let matchRosterUpdate: MatchRosterUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchRosterApiV1TeamsTeamIdMatchesMatchIdRosterRosterIdPatch_0(
    teamId,
    matchId,
    rosterId,
    matchRosterUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterUpdate** | **MatchRosterUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **rosterId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchRoster**

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

# **updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch**
> MatchRoster updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch(matchRosterUpdate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let matchRosterId: string; // (default to undefined)
let matchRosterUpdate: MatchRosterUpdate; //

const { status, data } = await apiInstance.updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch(
    matchRosterId,
    matchRosterUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterUpdate** | **MatchRosterUpdate**|  | |
| **matchRosterId** | [**string**] |  | defaults to undefined|


### Return type

**MatchRoster**

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

# **updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch_0**
> MatchRoster updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch_0(matchRosterUpdate)


### Example

```typescript
import {
    MatchRosterApi,
    Configuration,
    MatchRosterUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchRosterApi(configuration);

let matchRosterId: string; // (default to undefined)
let matchRosterUpdate: MatchRosterUpdate; //

const { status, data } = await apiInstance.updateMatchRosterApiV1MatchesMatchRosterMatchRosterIdPatch_0(
    matchRosterId,
    matchRosterUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchRosterUpdate** | **MatchRosterUpdate**|  | |
| **matchRosterId** | [**string**] |  | defaults to undefined|


### Return type

**MatchRoster**

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

