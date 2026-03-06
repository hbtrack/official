# RolesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getRoleByIdApiV1RolesRoleIdGet**](#getrolebyidapiv1rolesroleidget) | **GET** /api/v1/roles/{role_id} | Obter papel por ID|
|[**getRoleByIdApiV1RolesRoleIdGet_0**](#getrolebyidapiv1rolesroleidget_0) | **GET** /api/v1/roles/{role_id} | Obter papel por ID|
|[**getRoleByNameApiV1RolesByNameRoleNameGet**](#getrolebynameapiv1rolesbynamerolenameget) | **GET** /api/v1/roles/by-name/{role_name} | Obter papel por nome|
|[**getRoleByNameApiV1RolesByNameRoleNameGet_0**](#getrolebynameapiv1rolesbynamerolenameget_0) | **GET** /api/v1/roles/by-name/{role_name} | Obter papel por nome|
|[**listRolesApiV1RolesGet**](#listrolesapiv1rolesget) | **GET** /api/v1/roles | Listar papéis disponíveis|
|[**listRolesApiV1RolesGet_0**](#listrolesapiv1rolesget_0) | **GET** /api/v1/roles | Listar papéis disponíveis|

# **getRoleByIdApiV1RolesRoleIdGet**
> Role getRoleByIdApiV1RolesRoleIdGet()

Retorna os dados de um papel específico.  **Regras aplicáveis:** R4 (papéis são catálogo fixo)

### Example

```typescript
import {
    RolesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RolesApi(configuration);

let roleId: number; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getRoleByIdApiV1RolesRoleIdGet(
    roleId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **roleId** | [**number**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Role**

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
|**404** | Papel não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getRoleByIdApiV1RolesRoleIdGet_0**
> Role getRoleByIdApiV1RolesRoleIdGet_0()

Retorna os dados de um papel específico.  **Regras aplicáveis:** R4 (papéis são catálogo fixo)

### Example

```typescript
import {
    RolesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RolesApi(configuration);

let roleId: number; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getRoleByIdApiV1RolesRoleIdGet_0(
    roleId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **roleId** | [**number**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Role**

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
|**404** | Papel não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getRoleByNameApiV1RolesByNameRoleNameGet**
> Role getRoleByNameApiV1RolesByNameRoleNameGet()

Retorna os dados de um papel pelo nome (dirigente, coordenador, treinador, atleta).  **Regras aplicáveis:** R4 (papéis são catálogo fixo)

### Example

```typescript
import {
    RolesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RolesApi(configuration);

let roleName: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getRoleByNameApiV1RolesByNameRoleNameGet(
    roleName,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **roleName** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Role**

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
|**404** | Papel não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getRoleByNameApiV1RolesByNameRoleNameGet_0**
> Role getRoleByNameApiV1RolesByNameRoleNameGet_0()

Retorna os dados de um papel pelo nome (dirigente, coordenador, treinador, atleta).  **Regras aplicáveis:** R4 (papéis são catálogo fixo)

### Example

```typescript
import {
    RolesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RolesApi(configuration);

let roleName: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getRoleByNameApiV1RolesByNameRoleNameGet_0(
    roleName,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **roleName** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Role**

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
|**404** | Papel não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listRolesApiV1RolesGet**
> Array<Role> listRolesApiV1RolesGet()

Lista os papéis disponíveis no sistema (catálogo).  **Papéis V1:** dirigente, coordenador, treinador, atleta  **Regras aplicáveis:** R4 (papéis são catálogo fixo)  **Nota:** Endpoint público (não requer autenticação) pois é apenas um catálogo.

### Example

```typescript
import {
    RolesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RolesApi(configuration);

const { status, data } = await apiInstance.listRolesApiV1RolesGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<Role>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listRolesApiV1RolesGet_0**
> Array<Role> listRolesApiV1RolesGet_0()

Lista os papéis disponíveis no sistema (catálogo).  **Papéis V1:** dirigente, coordenador, treinador, atleta  **Regras aplicáveis:** R4 (papéis são catálogo fixo)  **Nota:** Endpoint público (não requer autenticação) pois é apenas um catálogo.

### Example

```typescript
import {
    RolesApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new RolesApi(configuration);

const { status, data } = await apiInstance.listRolesApiV1RolesGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<Role>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

