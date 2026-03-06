# SessionTemplatesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createSessionTemplateApiV1SessionTemplatesPost**](#createsessiontemplateapiv1sessiontemplatespost) | **POST** /api/v1/session-templates | Create session template|
|[**createSessionTemplateApiV1SessionTemplatesPost_0**](#createsessiontemplateapiv1sessiontemplatespost_0) | **POST** /api/v1/session-templates | Create session template|
|[**deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete**](#deletesessiontemplateapiv1sessiontemplatestemplateiddelete) | **DELETE** /api/v1/session-templates/{template_id} | Delete session template|
|[**deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete_0**](#deletesessiontemplateapiv1sessiontemplatestemplateiddelete_0) | **DELETE** /api/v1/session-templates/{template_id} | Delete session template|
|[**getSessionTemplateApiV1SessionTemplatesTemplateIdGet**](#getsessiontemplateapiv1sessiontemplatestemplateidget) | **GET** /api/v1/session-templates/{template_id} | Get session template|
|[**getSessionTemplateApiV1SessionTemplatesTemplateIdGet_0**](#getsessiontemplateapiv1sessiontemplatestemplateidget_0) | **GET** /api/v1/session-templates/{template_id} | Get session template|
|[**listSessionTemplatesApiV1SessionTemplatesGet**](#listsessiontemplatesapiv1sessiontemplatesget) | **GET** /api/v1/session-templates | List session templates|
|[**listSessionTemplatesApiV1SessionTemplatesGet_0**](#listsessiontemplatesapiv1sessiontemplatesget_0) | **GET** /api/v1/session-templates | List session templates|
|[**toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch**](#togglefavoritetemplateapiv1sessiontemplatestemplateidfavoritepatch) | **PATCH** /api/v1/session-templates/{template_id}/favorite | Toggle favorite|
|[**toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch_0**](#togglefavoritetemplateapiv1sessiontemplatestemplateidfavoritepatch_0) | **PATCH** /api/v1/session-templates/{template_id}/favorite | Toggle favorite|
|[**updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch**](#updatesessiontemplateapiv1sessiontemplatestemplateidpatch) | **PATCH** /api/v1/session-templates/{template_id} | Update session template|
|[**updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch_0**](#updatesessiontemplateapiv1sessiontemplatestemplateidpatch_0) | **PATCH** /api/v1/session-templates/{template_id} | Update session template|

# **createSessionTemplateApiV1SessionTemplatesPost**
> SessionTemplateResponse createSessionTemplateApiV1SessionTemplatesPost(sessionTemplateCreate)

Cria template customizado (limite 50 por org)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration,
    SessionTemplateCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let sessionTemplateCreate: SessionTemplateCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSessionTemplateApiV1SessionTemplatesPost(
    sessionTemplateCreate,
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
| **sessionTemplateCreate** | **SessionTemplateCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

# **createSessionTemplateApiV1SessionTemplatesPost_0**
> SessionTemplateResponse createSessionTemplateApiV1SessionTemplatesPost_0(sessionTemplateCreate)

Cria template customizado (limite 50 por org)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration,
    SessionTemplateCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let sessionTemplateCreate: SessionTemplateCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createSessionTemplateApiV1SessionTemplatesPost_0(
    sessionTemplateCreate,
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
| **sessionTemplateCreate** | **SessionTemplateCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

# **deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete**
> deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete()

HARD DELETE - Remove template permanentemente e libera espaço no limite 50

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete(
    templateId,
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
| **templateId** | [**string**] |  | defaults to undefined|
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

# **deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete_0**
> deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete_0()

HARD DELETE - Remove template permanentemente e libera espaço no limite 50

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteSessionTemplateApiV1SessionTemplatesTemplateIdDelete_0(
    templateId,
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
| **templateId** | [**string**] |  | defaults to undefined|
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

# **getSessionTemplateApiV1SessionTemplatesTemplateIdGet**
> SessionTemplateResponse getSessionTemplateApiV1SessionTemplatesTemplateIdGet()

Retorna template específico

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionTemplateApiV1SessionTemplatesTemplateIdGet(
    templateId,
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
| **templateId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

# **getSessionTemplateApiV1SessionTemplatesTemplateIdGet_0**
> SessionTemplateResponse getSessionTemplateApiV1SessionTemplatesTemplateIdGet_0()

Retorna template específico

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionTemplateApiV1SessionTemplatesTemplateIdGet_0(
    templateId,
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
| **templateId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

# **listSessionTemplatesApiV1SessionTemplatesGet**
> SessionTemplateListResponse listSessionTemplatesApiV1SessionTemplatesGet()

Lista templates de treino da organização (máx 50, favoritos primeiro)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let activeOnly: boolean; //Filtrar apenas templates ativos (optional) (default to true)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSessionTemplatesApiV1SessionTemplatesGet(
    activeOnly,
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
| **activeOnly** | [**boolean**] | Filtrar apenas templates ativos | (optional) defaults to true|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateListResponse**

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

# **listSessionTemplatesApiV1SessionTemplatesGet_0**
> SessionTemplateListResponse listSessionTemplatesApiV1SessionTemplatesGet_0()

Lista templates de treino da organização (máx 50, favoritos primeiro)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let activeOnly: boolean; //Filtrar apenas templates ativos (optional) (default to true)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSessionTemplatesApiV1SessionTemplatesGet_0(
    activeOnly,
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
| **activeOnly** | [**boolean**] | Filtrar apenas templates ativos | (optional) defaults to true|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateListResponse**

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

# **toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch**
> SessionTemplateResponse toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch()

Alterna favorito do template (⭐)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch(
    templateId,
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
| **templateId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

# **toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch_0**
> SessionTemplateResponse toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch_0()

Alterna favorito do template (⭐)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.toggleFavoriteTemplateApiV1SessionTemplatesTemplateIdFavoritePatch_0(
    templateId,
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
| **templateId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

# **updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch**
> SessionTemplateResponse updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch(sessionTemplateUpdate)

Atualiza template (permite editar templates usados em treinos)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration,
    SessionTemplateUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let sessionTemplateUpdate: SessionTemplateUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch(
    templateId,
    sessionTemplateUpdate,
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
| **sessionTemplateUpdate** | **SessionTemplateUpdate**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

# **updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch_0**
> SessionTemplateResponse updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch_0(sessionTemplateUpdate)

Atualiza template (permite editar templates usados em treinos)

### Example

```typescript
import {
    SessionTemplatesApi,
    Configuration,
    SessionTemplateUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new SessionTemplatesApi(configuration);

let templateId: string; // (default to undefined)
let sessionTemplateUpdate: SessionTemplateUpdate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateSessionTemplateApiV1SessionTemplatesTemplateIdPatch_0(
    templateId,
    sessionTemplateUpdate,
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
| **sessionTemplateUpdate** | **SessionTemplateUpdate**|  | |
| **templateId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionTemplateResponse**

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

