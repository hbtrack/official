# ExerciseFavoritesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**favoriteExerciseApiV1ExerciseFavoritesPost**](#favoriteexerciseapiv1exercisefavoritespost) | **POST** /api/v1/exercise-favorites | Favoritar exercício|
|[**listMyFavoritesApiV1ExerciseFavoritesGet**](#listmyfavoritesapiv1exercisefavoritesget) | **GET** /api/v1/exercise-favorites | Listar meus favoritos|
|[**unfavoriteExerciseApiV1ExerciseFavoritesExerciseIdDelete**](#unfavoriteexerciseapiv1exercisefavoritesexerciseiddelete) | **DELETE** /api/v1/exercise-favorites/{exercise_id} | Remover dos favoritos|

# **favoriteExerciseApiV1ExerciseFavoritesPost**
> ExerciseFavoriteResponse favoriteExerciseApiV1ExerciseFavoritesPost(exerciseFavoriteCreate)

Marca exercício como favorito do usuário atual.

### Example

```typescript
import {
    ExerciseFavoritesApi,
    Configuration,
    ExerciseFavoriteCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new ExerciseFavoritesApi(configuration);

let exerciseFavoriteCreate: ExerciseFavoriteCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.favoriteExerciseApiV1ExerciseFavoritesPost(
    exerciseFavoriteCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exerciseFavoriteCreate** | **ExerciseFavoriteCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExerciseFavoriteResponse**

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

# **listMyFavoritesApiV1ExerciseFavoritesGet**
> Array<ExerciseFavoriteResponse> listMyFavoritesApiV1ExerciseFavoritesGet()

Lista exercícios favoritos do usuário atual.

### Example

```typescript
import {
    ExerciseFavoritesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExerciseFavoritesApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listMyFavoritesApiV1ExerciseFavoritesGet(
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ExerciseFavoriteResponse>**

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

# **unfavoriteExerciseApiV1ExerciseFavoritesExerciseIdDelete**
> unfavoriteExerciseApiV1ExerciseFavoritesExerciseIdDelete()

Remove exercício dos favoritos do usuário atual.

### Example

```typescript
import {
    ExerciseFavoritesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExerciseFavoritesApi(configuration);

let exerciseId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.unfavoriteExerciseApiV1ExerciseFavoritesExerciseIdDelete(
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

