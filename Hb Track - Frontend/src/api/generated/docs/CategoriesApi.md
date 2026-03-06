# CategoriesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createCategoryApiV1CategoriesPost**](#createcategoryapiv1categoriespost) | **POST** /api/v1/categories | Create Category|
|[**createCategoryApiV1CategoriesPost_0**](#createcategoryapiv1categoriespost_0) | **POST** /api/v1/categories | Create Category|
|[**getCategoryApiV1CategoriesCategoryIdGet**](#getcategoryapiv1categoriescategoryidget) | **GET** /api/v1/categories/{category_id} | Get Category|
|[**getCategoryApiV1CategoriesCategoryIdGet_0**](#getcategoryapiv1categoriescategoryidget_0) | **GET** /api/v1/categories/{category_id} | Get Category|
|[**updateCategoryApiV1CategoriesCategoryIdPut**](#updatecategoryapiv1categoriescategoryidput) | **PUT** /api/v1/categories/{category_id} | Update Category|
|[**updateCategoryApiV1CategoriesCategoryIdPut_0**](#updatecategoryapiv1categoriescategoryidput_0) | **PUT** /api/v1/categories/{category_id} | Update Category|

# **createCategoryApiV1CategoriesPost**
> AppSchemasCategoriesCategoryResponse createCategoryApiV1CategoriesPost(categoryCreate)

Cria nova categoria  Permissões: coordenador, dirigente (R26)  Referências RAG: - R15: Categorias globais definidas por idade - RDB11: Validação min_age <= max_age

### Example

```typescript
import {
    CategoriesApi,
    Configuration,
    CategoryCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CategoriesApi(configuration);

let categoryCreate: CategoryCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCategoryApiV1CategoriesPost(
    categoryCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **categoryCreate** | **CategoryCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasCategoriesCategoryResponse**

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

# **createCategoryApiV1CategoriesPost_0**
> AppSchemasCategoriesCategoryResponse createCategoryApiV1CategoriesPost_0(categoryCreate)

Cria nova categoria  Permissões: coordenador, dirigente (R26)  Referências RAG: - R15: Categorias globais definidas por idade - RDB11: Validação min_age <= max_age

### Example

```typescript
import {
    CategoriesApi,
    Configuration,
    CategoryCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CategoriesApi(configuration);

let categoryCreate: CategoryCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCategoryApiV1CategoriesPost_0(
    categoryCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **categoryCreate** | **CategoryCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasCategoriesCategoryResponse**

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

# **getCategoryApiV1CategoriesCategoryIdGet**
> AppSchemasCategoriesCategoryResponse getCategoryApiV1CategoriesCategoryIdGet()

Busca categoria por ID  Permissões: coordenador, dirigente, treinador (R26)  Referências RAG: - R15: Categorias globais

### Example

```typescript
import {
    CategoriesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CategoriesApi(configuration);

let categoryId: number; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCategoryApiV1CategoriesCategoryIdGet(
    categoryId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **categoryId** | [**number**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasCategoriesCategoryResponse**

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

# **getCategoryApiV1CategoriesCategoryIdGet_0**
> AppSchemasCategoriesCategoryResponse getCategoryApiV1CategoriesCategoryIdGet_0()

Busca categoria por ID  Permissões: coordenador, dirigente, treinador (R26)  Referências RAG: - R15: Categorias globais

### Example

```typescript
import {
    CategoriesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CategoriesApi(configuration);

let categoryId: number; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCategoryApiV1CategoriesCategoryIdGet_0(
    categoryId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **categoryId** | [**number**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasCategoriesCategoryResponse**

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

# **updateCategoryApiV1CategoriesCategoryIdPut**
> AppSchemasCategoriesCategoryResponse updateCategoryApiV1CategoriesCategoryIdPut(categoryUpdate)

Atualiza categoria  Permissões: coordenador, dirigente (R26)  Referências RAG: - R15: Categorias globais - RDB11: Validação min_age <= max_age

### Example

```typescript
import {
    CategoriesApi,
    Configuration,
    CategoryUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CategoriesApi(configuration);

let categoryId: number; // (default to undefined)
let categoryUpdate: CategoryUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCategoryApiV1CategoriesCategoryIdPut(
    categoryId,
    categoryUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **categoryUpdate** | **CategoryUpdate**|  | |
| **categoryId** | [**number**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasCategoriesCategoryResponse**

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

# **updateCategoryApiV1CategoriesCategoryIdPut_0**
> AppSchemasCategoriesCategoryResponse updateCategoryApiV1CategoriesCategoryIdPut_0(categoryUpdate)

Atualiza categoria  Permissões: coordenador, dirigente (R26)  Referências RAG: - R15: Categorias globais - RDB11: Validação min_age <= max_age

### Example

```typescript
import {
    CategoriesApi,
    Configuration,
    CategoryUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CategoriesApi(configuration);

let categoryId: number; // (default to undefined)
let categoryUpdate: CategoryUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCategoryApiV1CategoriesCategoryIdPut_0(
    categoryId,
    categoryUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **categoryUpdate** | **CategoryUpdate**|  | |
| **categoryId** | [**number**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AppSchemasCategoriesCategoryResponse**

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

