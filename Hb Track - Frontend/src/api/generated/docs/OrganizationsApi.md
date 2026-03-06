# OrganizationsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createOrganizationApiV1OrganizationsPost**](#createorganizationapiv1organizationspost) | **POST** /api/v1/organizations | Criar organização|
|[**createOrganizationApiV1OrganizationsPost_0**](#createorganizationapiv1organizationspost_0) | **POST** /api/v1/organizations | Criar organização|
|[**getOrganizationByIdApiV1OrganizationsOrganizationIdGet**](#getorganizationbyidapiv1organizationsorganizationidget) | **GET** /api/v1/organizations/{organization_id} | Obter organização por ID|
|[**getOrganizationByIdApiV1OrganizationsOrganizationIdGet_0**](#getorganizationbyidapiv1organizationsorganizationidget_0) | **GET** /api/v1/organizations/{organization_id} | Obter organização por ID|
|[**updateOrganizationApiV1OrganizationsOrganizationIdPatch**](#updateorganizationapiv1organizationsorganizationidpatch) | **PATCH** /api/v1/organizations/{organization_id} | Atualizar organização|
|[**updateOrganizationApiV1OrganizationsOrganizationIdPatch_0**](#updateorganizationapiv1organizationsorganizationidpatch_0) | **PATCH** /api/v1/organizations/{organization_id} | Atualizar organização|

# **createOrganizationApiV1OrganizationsPost**
> Organization createOrganizationApiV1OrganizationsPost(organizationCreate)

Cria uma nova organização/clube.  **Regras aplicáveis:** R25/R26 (permissões), R29 (exclusão lógica), R31/R32 (auditoria)  **Comportamento:** - Valida unicidade de code e name - Registra auditoria da criação (R31/R32)

### Example

```typescript
import {
    OrganizationsApi,
    Configuration,
    OrganizationCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new OrganizationsApi(configuration);

let organizationCreate: OrganizationCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createOrganizationApiV1OrganizationsPost(
    organizationCreate,
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
| **organizationCreate** | **OrganizationCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Organization**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**409** | Code/name já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createOrganizationApiV1OrganizationsPost_0**
> Organization createOrganizationApiV1OrganizationsPost_0(organizationCreate)

Cria uma nova organização/clube.  **Regras aplicáveis:** R25/R26 (permissões), R29 (exclusão lógica), R31/R32 (auditoria)  **Comportamento:** - Valida unicidade de code e name - Registra auditoria da criação (R31/R32)

### Example

```typescript
import {
    OrganizationsApi,
    Configuration,
    OrganizationCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new OrganizationsApi(configuration);

let organizationCreate: OrganizationCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createOrganizationApiV1OrganizationsPost_0(
    organizationCreate,
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
| **organizationCreate** | **OrganizationCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Organization**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**409** | Code/name já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOrganizationByIdApiV1OrganizationsOrganizationIdGet**
> Organization getOrganizationByIdApiV1OrganizationsOrganizationIdGet()

Retorna os dados de uma organização específica.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    OrganizationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new OrganizationsApi(configuration);

let organizationId: string; // (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOrganizationByIdApiV1OrganizationsOrganizationIdGet(
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
| **organizationId** | [**string**] |  | defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Organization**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Organização não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOrganizationByIdApiV1OrganizationsOrganizationIdGet_0**
> Organization getOrganizationByIdApiV1OrganizationsOrganizationIdGet_0()

Retorna os dados de uma organização específica.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    OrganizationsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new OrganizationsApi(configuration);

let organizationId: string; // (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOrganizationByIdApiV1OrganizationsOrganizationIdGet_0(
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
| **organizationId** | [**string**] |  | defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Organization**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Organização não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateOrganizationApiV1OrganizationsOrganizationIdPatch**
> Organization updateOrganizationApiV1OrganizationsOrganizationIdPatch(organizationUpdate)

Atualiza dados de uma organização existente.  **Regras aplicáveis:** R25/R26 (permissões), R31/R32 (auditoria)  **Comportamento:** - Valida unicidade de code e name (se alterados) - Registra auditoria da alteração (R31/R32)

### Example

```typescript
import {
    OrganizationsApi,
    Configuration,
    OrganizationUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new OrganizationsApi(configuration);

let organizationId: string; // (default to undefined)
let organizationUpdate: OrganizationUpdate; //
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateOrganizationApiV1OrganizationsOrganizationIdPatch(
    organizationId,
    organizationUpdate,
    teamId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationUpdate** | **OrganizationUpdate**|  | |
| **organizationId** | [**string**] |  | defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Organization**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**409** | Code/name já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateOrganizationApiV1OrganizationsOrganizationIdPatch_0**
> Organization updateOrganizationApiV1OrganizationsOrganizationIdPatch_0(organizationUpdate)

Atualiza dados de uma organização existente.  **Regras aplicáveis:** R25/R26 (permissões), R31/R32 (auditoria)  **Comportamento:** - Valida unicidade de code e name (se alterados) - Registra auditoria da alteração (R31/R32)

### Example

```typescript
import {
    OrganizationsApi,
    Configuration,
    OrganizationUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new OrganizationsApi(configuration);

let organizationId: string; // (default to undefined)
let organizationUpdate: OrganizationUpdate; //
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateOrganizationApiV1OrganizationsOrganizationIdPatch_0(
    organizationId,
    organizationUpdate,
    teamId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationUpdate** | **OrganizationUpdate**|  | |
| **organizationId** | [**string**] |  | defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Organization**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**409** | Code/name já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

