# TeamRegistrationsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost**](#createteamregistrationapiv1teamsteamidregistrationsathleteidpost) | **POST** /api/v1/teams/{team_id}/registrations/{athlete_id} | Criar inscrição atleta–equipe|
|[**createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost_0**](#createteamregistrationapiv1teamsteamidregistrationsathleteidpost_0) | **POST** /api/v1/teams/{team_id}/registrations/{athlete_id} | Criar inscrição atleta–equipe|
|[**getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet**](#getteamregistrationapiv1teamsteamidregistrationsregistrationidget) | **GET** /api/v1/teams/{team_id}/registrations/{registration_id} | Obter inscrição por ID|
|[**getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet_0**](#getteamregistrationapiv1teamsteamidregistrationsregistrationidget_0) | **GET** /api/v1/teams/{team_id}/registrations/{registration_id} | Obter inscrição por ID|
|[**listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet**](#listteamregistrationsapiv1teamsteamidregistrationsget) | **GET** /api/v1/teams/{team_id}/registrations | Listar inscrições de uma equipe|
|[**listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet_0**](#listteamregistrationsapiv1teamsteamidregistrationsget_0) | **GET** /api/v1/teams/{team_id}/registrations | Listar inscrições de uma equipe|
|[**updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch**](#updateteamregistrationapiv1teamsteamidregistrationsregistrationidpatch) | **PATCH** /api/v1/teams/{team_id}/registrations/{registration_id} | Atualizar inscrição|
|[**updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch_0**](#updateteamregistrationapiv1teamsteamidregistrationsregistrationidpatch_0) | **PATCH** /api/v1/teams/{team_id}/registrations/{registration_id} | Atualizar inscrição|

# **createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost**
> TeamRegistration createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost(teamRegistrationCreate)


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration,
    TeamRegistrationCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let teamRegistrationCreate: TeamRegistrationCreate; //
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost(
    teamId,
    athleteId,
    teamRegistrationCreate,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamRegistrationCreate** | **TeamRegistrationCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Inscrição criada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Atleta ou equipe não encontrada |  -  |
|**409** | Período sobreposto (RDB10) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost_0**
> TeamRegistration createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost_0(teamRegistrationCreate)


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration,
    TeamRegistrationCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let teamRegistrationCreate: TeamRegistrationCreate; //
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTeamRegistrationApiV1TeamsTeamIdRegistrationsAthleteIdPost_0(
    teamId,
    athleteId,
    teamRegistrationCreate,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamRegistrationCreate** | **TeamRegistrationCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Inscrição criada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Atleta ou equipe não encontrada |  -  |
|**409** | Período sobreposto (RDB10) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet**
> TeamRegistration getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet()


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let registrationId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet(
    teamId,
    registrationId,
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
| **registrationId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

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

# **getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet_0**
> TeamRegistration getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet_0()


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let registrationId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdGet_0(
    teamId,
    registrationId,
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
| **registrationId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

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

# **listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet**
> TeamRegistrationPaginatedResponse listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet()


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let activeOnly: boolean; //Apenas inscrições ativas (optional) (default to false)
let page: number; //Página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet(
    teamId,
    athleteId,
    seasonId,
    activeOnly,
    page,
    limit,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **activeOnly** | [**boolean**] | Apenas inscrições ativas | (optional) defaults to false|
| **page** | [**number**] | Página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistrationPaginatedResponse**

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

# **listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet_0**
> TeamRegistrationPaginatedResponse listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet_0()


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let activeOnly: boolean; //Apenas inscrições ativas (optional) (default to false)
let page: number; //Página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTeamRegistrationsApiV1TeamsTeamIdRegistrationsGet_0(
    teamId,
    athleteId,
    seasonId,
    activeOnly,
    page,
    limit,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **activeOnly** | [**boolean**] | Apenas inscrições ativas | (optional) defaults to false|
| **page** | [**number**] | Página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistrationPaginatedResponse**

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

# **updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch**
> TeamRegistration updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch(teamRegistrationUpdate)


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration,
    TeamRegistrationUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let registrationId: string; // (default to undefined)
let teamRegistrationUpdate: TeamRegistrationUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch(
    teamId,
    registrationId,
    teamRegistrationUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamRegistrationUpdate** | **TeamRegistrationUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **registrationId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

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

# **updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch_0**
> TeamRegistration updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch_0(teamRegistrationUpdate)


### Example

```typescript
import {
    TeamRegistrationsApi,
    Configuration,
    TeamRegistrationUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamRegistrationsApi(configuration);

let teamId: string; // (default to undefined)
let registrationId: string; // (default to undefined)
let teamRegistrationUpdate: TeamRegistrationUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTeamRegistrationApiV1TeamsTeamIdRegistrationsRegistrationIdPatch_0(
    teamId,
    registrationId,
    teamRegistrationUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamRegistrationUpdate** | **TeamRegistrationUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **registrationId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

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

