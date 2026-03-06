# ExercisesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**copyExerciseToOrgApiV1ExercisesExerciseIdCopyToOrgPost**](#copyexercisetoorgapiv1exercisesexerciseidcopytoorgpost) | **POST** /api/v1/exercises/{exercise_id}/copy-to-org | Copiar exercício SYSTEM para ORG|
|[**createExerciseApiV1ExercisesPost**](#createexerciseapiv1exercisespost) | **POST** /api/v1/exercises | Criar exercício|
|[**getExerciseApiV1ExercisesExerciseIdGet**](#getexerciseapiv1exercisesexerciseidget) | **GET** /api/v1/exercises/{exercise_id} | Buscar exercício por ID|
|[**grantExerciseAclApiV1ExercisesExerciseIdAclPost**](#grantexerciseaclapiv1exercisesexerciseidaclpost) | **POST** /api/v1/exercises/{exercise_id}/acl | Conceder acesso ao exercício|
|[**listExerciseAclApiV1ExercisesExerciseIdAclGet**](#listexerciseaclapiv1exercisesexerciseidaclget) | **GET** /api/v1/exercises/{exercise_id}/acl | Listar ACL do exercício|
|[**listExercisesApiV1ExercisesGet**](#listexercisesapiv1exercisesget) | **GET** /api/v1/exercises | Listar exercícios|
|[**revokeExerciseAclApiV1ExercisesExerciseIdAclUserIdDelete**](#revokeexerciseaclapiv1exercisesexerciseidacluseriddelete) | **DELETE** /api/v1/exercises/{exercise_id}/acl/{user_id} | Revogar acesso ao exercício|
|[**updateExerciseApiV1ExercisesExerciseIdPatch**](#updateexerciseapiv1exercisesexerciseidpatch) | **PATCH** /api/v1/exercises/{exercise_id} | Atualizar exercício|
|[**updateExerciseVisibilityApiV1ExercisesExerciseIdVisibilityPatch**](#updateexercisevisibilityapiv1exercisesexerciseidvisibilitypatch) | **PATCH** /api/v1/exercises/{exercise_id}/visibility | Alterar visibilidade do exercício|

# **copyExerciseToOrgApiV1ExercisesExerciseIdCopyToOrgPost**
> ExerciseResponse copyExerciseToOrgApiV1ExercisesExerciseIdCopyToOrgPost()

Cria cópia editável de um exercício SYSTEM na organização do usuário.

### Example

```typescript
import {
    ExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.copyExerciseToOrgApiV1ExercisesExerciseIdCopyToOrgPost(
    exerciseId,
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
| **exerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createExerciseApiV1ExercisesPost**
> ExerciseResponse createExerciseApiV1ExercisesPost(exerciseCreate)

Cria novo exercício. Valida tag_ids.

### Example

```typescript
import {
    ExercisesApi,
    Configuration,
    ExerciseCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseCreate: ExerciseCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createExerciseApiV1ExercisesPost(
    exerciseCreate,
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
| **exerciseCreate** | **ExerciseCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseResponse**

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

# **getExerciseApiV1ExercisesExerciseIdGet**
> ExerciseResponse getExerciseApiV1ExercisesExerciseIdGet()

Retorna um exercício específico.

### Example

```typescript
import {
    ExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExerciseApiV1ExercisesExerciseIdGet(
    exerciseId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exerciseId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseResponse**

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

# **grantExerciseAclApiV1ExercisesExerciseIdAclPost**
> ExerciseACLResponse grantExerciseAclApiV1ExercisesExerciseIdAclPost(exerciseACLGrantRequest)

Adiciona usuário à ACL do exercício restricted. Apenas o criador pode conceder.

### Example

```typescript
import {
    ExercisesApi,
    Configuration,
    ExerciseACLGrantRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseId: string; // (default to undefined)
let exerciseACLGrantRequest: ExerciseACLGrantRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.grantExerciseAclApiV1ExercisesExerciseIdAclPost(
    exerciseId,
    exerciseACLGrantRequest,
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
| **exerciseACLGrantRequest** | **ExerciseACLGrantRequest**|  | |
| **exerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseACLResponse**

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

# **listExerciseAclApiV1ExercisesExerciseIdAclGet**
> Array<ExerciseACLResponse> listExerciseAclApiV1ExercisesExerciseIdAclGet()

Lista usuários com acesso ao exercício restricted. Apenas o criador pode ver.

### Example

```typescript
import {
    ExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listExerciseAclApiV1ExercisesExerciseIdAclGet(
    exerciseId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exerciseId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ExerciseACLResponse>**

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

# **listExercisesApiV1ExercisesGet**
> ExerciseListResponse listExercisesApiV1ExercisesGet()

Lista exercícios da organização do usuário com paginação.

### Example

```typescript
import {
    ExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let page: number; // (optional) (default to 1)
let perPage: number; // (optional) (default to 20)
let search: string; // (optional) (default to undefined)
let category: string; // (optional) (default to undefined)
let favoritesOnly: boolean; // (optional) (default to false)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)
let requestBody: Array<string | null>; // (optional)

const { status, data } = await apiInstance.listExercisesApiV1ExercisesGet(
    page,
    perPage,
    search,
    category,
    favoritesOnly,
    xRequestID,
    xOrganizationId,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string | null>**|  | |
| **page** | [**number**] |  | (optional) defaults to 1|
| **perPage** | [**number**] |  | (optional) defaults to 20|
| **search** | [**string**] |  | (optional) defaults to undefined|
| **category** | [**string**] |  | (optional) defaults to undefined|
| **favoritesOnly** | [**boolean**] |  | (optional) defaults to false|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseListResponse**

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

# **revokeExerciseAclApiV1ExercisesExerciseIdAclUserIdDelete**
> revokeExerciseAclApiV1ExercisesExerciseIdAclUserIdDelete()

Remove usuário da ACL do exercício. Apenas o criador pode revogar.

### Example

```typescript
import {
    ExercisesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseId: string; // (default to undefined)
let userId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.revokeExerciseAclApiV1ExercisesExerciseIdAclUserIdDelete(
    exerciseId,
    userId,
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
| **exerciseId** | [**string**] |  | defaults to undefined|
| **userId** | [**string**] |  | defaults to undefined|
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
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateExerciseApiV1ExercisesExerciseIdPatch**
> ExerciseResponse updateExerciseApiV1ExercisesExerciseIdPatch(exerciseUpdate)

Atualiza exercício existente. Valida tag_ids e escopo de organização.

### Example

```typescript
import {
    ExercisesApi,
    Configuration,
    ExerciseUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseId: string; // (default to undefined)
let exerciseUpdate: ExerciseUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateExerciseApiV1ExercisesExerciseIdPatch(
    exerciseId,
    exerciseUpdate,
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
| **exerciseUpdate** | **ExerciseUpdate**|  | |
| **exerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseResponse**

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

# **updateExerciseVisibilityApiV1ExercisesExerciseIdVisibilityPatch**
> ExerciseResponse updateExerciseVisibilityApiV1ExercisesExerciseIdVisibilityPatch(visibilityUpdateRequest)

Altera visibility_mode entre org_wide e restricted. Apenas o criador pode alterar.

### Example

```typescript
import {
    ExercisesApi,
    Configuration,
    VisibilityUpdateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExercisesApi(configuration);

let exerciseId: string; // (default to undefined)
let visibilityUpdateRequest: VisibilityUpdateRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateExerciseVisibilityApiV1ExercisesExerciseIdVisibilityPatch(
    exerciseId,
    visibilityUpdateRequest,
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
| **visibilityUpdateRequest** | **VisibilityUpdateRequest**|  | |
| **exerciseId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseResponse**

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

