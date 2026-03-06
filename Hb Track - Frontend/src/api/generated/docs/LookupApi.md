# LookupApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getCategoriesApiV1CategoriesGet**](#getcategoriesapiv1categoriesget) | **GET** /api/v1/categories | Get Categories|
|[**getCategoriesApiV1CategoriesGet_0**](#getcategoriesapiv1categoriesget_0) | **GET** /api/v1/categories | Get Categories|
|[**getDefensivePositionsApiV1PositionsDefensiveGet**](#getdefensivepositionsapiv1positionsdefensiveget) | **GET** /api/v1/positions/defensive | Get Defensive Positions|
|[**getDefensivePositionsApiV1PositionsDefensiveGet_0**](#getdefensivepositionsapiv1positionsdefensiveget_0) | **GET** /api/v1/positions/defensive | Get Defensive Positions|
|[**getOffensivePositionsApiV1PositionsOffensiveGet**](#getoffensivepositionsapiv1positionsoffensiveget) | **GET** /api/v1/positions/offensive | Get Offensive Positions|
|[**getOffensivePositionsApiV1PositionsOffensiveGet_0**](#getoffensivepositionsapiv1positionsoffensiveget_0) | **GET** /api/v1/positions/offensive | Get Offensive Positions|
|[**getOrganizationsApiV1OrganizationsGet**](#getorganizationsapiv1organizationsget) | **GET** /api/v1/organizations | Get Organizations|
|[**getOrganizationsApiV1OrganizationsGet_0**](#getorganizationsapiv1organizationsget_0) | **GET** /api/v1/organizations | Get Organizations|
|[**getSchoolingLevelsApiV1SchoolingLevelsGet**](#getschoolinglevelsapiv1schoolinglevelsget) | **GET** /api/v1/schooling-levels | Get Schooling Levels|
|[**getSchoolingLevelsApiV1SchoolingLevelsGet_0**](#getschoolinglevelsapiv1schoolinglevelsget_0) | **GET** /api/v1/schooling-levels | Get Schooling Levels|
|[**getSeasonsApiV1SeasonsGet**](#getseasonsapiv1seasonsget) | **GET** /api/v1/seasons | Get Seasons|
|[**getSeasonsApiV1SeasonsGet_0**](#getseasonsapiv1seasonsget_0) | **GET** /api/v1/seasons | Get Seasons|
|[**getTeamsApiV1TeamsGet**](#getteamsapiv1teamsget) | **GET** /api/v1/teams | Get Teams|
|[**getTeamsApiV1TeamsGet_0**](#getteamsapiv1teamsget_0) | **GET** /api/v1/teams | Get Teams|

# **getCategoriesApiV1CategoriesGet**
> Array<AppApiV1RoutersLookupCategoryResponse> getCategoriesApiV1CategoriesGet()

Lista todas as categorias.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCategoriesApiV1CategoriesGet(
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

**Array<AppApiV1RoutersLookupCategoryResponse>**

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

# **getCategoriesApiV1CategoriesGet_0**
> Array<AppApiV1RoutersLookupCategoryResponse> getCategoriesApiV1CategoriesGet_0()

Lista todas as categorias.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCategoriesApiV1CategoriesGet_0(
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

**Array<AppApiV1RoutersLookupCategoryResponse>**

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

# **getDefensivePositionsApiV1PositionsDefensiveGet**
> Array<PositionResponse> getDefensivePositionsApiV1PositionsDefensiveGet()

Lista todas as posições defensivas.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDefensivePositionsApiV1PositionsDefensiveGet(
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

**Array<PositionResponse>**

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

# **getDefensivePositionsApiV1PositionsDefensiveGet_0**
> Array<PositionResponse> getDefensivePositionsApiV1PositionsDefensiveGet_0()

Lista todas as posições defensivas.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getDefensivePositionsApiV1PositionsDefensiveGet_0(
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

**Array<PositionResponse>**

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

# **getOffensivePositionsApiV1PositionsOffensiveGet**
> Array<PositionResponse> getOffensivePositionsApiV1PositionsOffensiveGet()

Lista todas as posições ofensivas.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOffensivePositionsApiV1PositionsOffensiveGet(
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

**Array<PositionResponse>**

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

# **getOffensivePositionsApiV1PositionsOffensiveGet_0**
> Array<PositionResponse> getOffensivePositionsApiV1PositionsOffensiveGet_0()

Lista todas as posições ofensivas.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOffensivePositionsApiV1PositionsOffensiveGet_0(
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

**Array<PositionResponse>**

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

# **getOrganizationsApiV1OrganizationsGet**
> Array<OrganizationResponse> getOrganizationsApiV1OrganizationsGet()

Lista organizações acessíveis pelo usuário. Super admin vê todas, outros vêem apenas suas organizações.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOrganizationsApiV1OrganizationsGet(
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

**Array<OrganizationResponse>**

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

# **getOrganizationsApiV1OrganizationsGet_0**
> Array<OrganizationResponse> getOrganizationsApiV1OrganizationsGet_0()

Lista organizações acessíveis pelo usuário. Super admin vê todas, outros vêem apenas suas organizações.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOrganizationsApiV1OrganizationsGet_0(
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

**Array<OrganizationResponse>**

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

# **getSchoolingLevelsApiV1SchoolingLevelsGet**
> Array<SchoolingLevelResponse> getSchoolingLevelsApiV1SchoolingLevelsGet()

Lista todos os níveis de escolaridade.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSchoolingLevelsApiV1SchoolingLevelsGet(
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

**Array<SchoolingLevelResponse>**

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

# **getSchoolingLevelsApiV1SchoolingLevelsGet_0**
> Array<SchoolingLevelResponse> getSchoolingLevelsApiV1SchoolingLevelsGet_0()

Lista todos os níveis de escolaridade.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSchoolingLevelsApiV1SchoolingLevelsGet_0(
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

**Array<SchoolingLevelResponse>**

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

# **getSeasonsApiV1SeasonsGet**
> Array<AppApiV1RoutersLookupSeasonResponse> getSeasonsApiV1SeasonsGet()

Lista temporadas disponíveis.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let organizationId: string; //Filtrar por organização (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSeasonsApiV1SeasonsGet(
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationId** | [**string**] | Filtrar por organização | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<AppApiV1RoutersLookupSeasonResponse>**

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

# **getSeasonsApiV1SeasonsGet_0**
> Array<AppApiV1RoutersLookupSeasonResponse> getSeasonsApiV1SeasonsGet_0()

Lista temporadas disponíveis.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let organizationId: string; //Filtrar por organização (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSeasonsApiV1SeasonsGet_0(
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationId** | [**string**] | Filtrar por organização | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<AppApiV1RoutersLookupSeasonResponse>**

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

# **getTeamsApiV1TeamsGet**
> Array<TeamResponse> getTeamsApiV1TeamsGet()

Lista equipes com filtros opcionais.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let organizationId: string; //Filtrar por organização (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let categoryId: number; //Filtrar por categoria (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamsApiV1TeamsGet(
    organizationId,
    seasonId,
    categoryId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationId** | [**string**] | Filtrar por organização | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **categoryId** | [**number**] | Filtrar por categoria | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TeamResponse>**

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

# **getTeamsApiV1TeamsGet_0**
> Array<TeamResponse> getTeamsApiV1TeamsGet_0()

Lista equipes com filtros opcionais.

### Example

```typescript
import {
    LookupApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LookupApi(configuration);

let organizationId: string; //Filtrar por organização (optional) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let categoryId: number; //Filtrar por categoria (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamsApiV1TeamsGet_0(
    organizationId,
    seasonId,
    categoryId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationId** | [**string**] | Filtrar por organização | (optional) defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **categoryId** | [**number**] | Filtrar por categoria | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TeamResponse>**

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

