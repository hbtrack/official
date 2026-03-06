# ExerciseTagsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createTagApiV1ExerciseTagsPost**](#createtagapiv1exercisetagspost) | **POST** /api/v1/exercise-tags | Criar tag de exercício|
|[**listTagsApiV1ExerciseTagsGet**](#listtagsapiv1exercisetagsget) | **GET** /api/v1/exercise-tags | Listar tags de exercícios|
|[**updateTagApiV1ExerciseTagsTagIdPatch**](#updatetagapiv1exercisetagstagidpatch) | **PATCH** /api/v1/exercise-tags/{tag_id} | Atualizar tag de exercício|

# **createTagApiV1ExerciseTagsPost**
> ExerciseTagResponse createTagApiV1ExerciseTagsPost(exerciseTagCreate)

Cria nova tag. Requer role dirigente ou coordenador.

### Example

```typescript
import {
    ExerciseTagsApi,
    Configuration,
    ExerciseTagCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new ExerciseTagsApi(configuration);

let exerciseTagCreate: ExerciseTagCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTagApiV1ExerciseTagsPost(
    exerciseTagCreate,
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
| **exerciseTagCreate** | **ExerciseTagCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseTagResponse**

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

# **listTagsApiV1ExerciseTagsGet**
> Array<ExerciseTagResponse> listTagsApiV1ExerciseTagsGet()

Lista todas as tags hierárquicas. Requer autenticação.

### Example

```typescript
import {
    ExerciseTagsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExerciseTagsApi(configuration);

let activeOnly: boolean; // (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listTagsApiV1ExerciseTagsGet(
    activeOnly,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **activeOnly** | [**boolean**] |  | (optional) defaults to true|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ExerciseTagResponse>**

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

# **updateTagApiV1ExerciseTagsTagIdPatch**
> ExerciseTagResponse updateTagApiV1ExerciseTagsTagIdPatch(exerciseTagUpdate)

Atualiza tag existente. Inclui validação anti-ciclo.

### Example

```typescript
import {
    ExerciseTagsApi,
    Configuration,
    ExerciseTagUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new ExerciseTagsApi(configuration);

let tagId: string; // (default to undefined)
let exerciseTagUpdate: ExerciseTagUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTagApiV1ExerciseTagsTagIdPatch(
    tagId,
    exerciseTagUpdate,
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
| **exerciseTagUpdate** | **ExerciseTagUpdate**|  | |
| **tagId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseTagResponse**

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

