# PermissionsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getPermissionByCodeApiV1PermissionsPermissionCodeGet**](#getpermissionbycodeapiv1permissionspermissioncodeget) | **GET** /api/v1/permissions/{permission_code} | Obter permissão por código|
|[**getPermissionByCodeApiV1PermissionsPermissionCodeGet_0**](#getpermissionbycodeapiv1permissionspermissioncodeget_0) | **GET** /api/v1/permissions/{permission_code} | Obter permissão por código|
|[**listPermissionsApiV1PermissionsGet**](#listpermissionsapiv1permissionsget) | **GET** /api/v1/permissions | Listar permissões disponíveis|
|[**listPermissionsApiV1PermissionsGet_0**](#listpermissionsapiv1permissionsget_0) | **GET** /api/v1/permissions | Listar permissões disponíveis|

# **getPermissionByCodeApiV1PermissionsPermissionCodeGet**
> Permission getPermissionByCodeApiV1PermissionsPermissionCodeGet()

Retorna os dados de uma permissão específica.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    PermissionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PermissionsApi(configuration);

let permissionCode: string; // (default to undefined)

const { status, data } = await apiInstance.getPermissionByCodeApiV1PermissionsPermissionCodeGet(
    permissionCode
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **permissionCode** | [**string**] |  | defaults to undefined|


### Return type

**Permission**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Permissão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPermissionByCodeApiV1PermissionsPermissionCodeGet_0**
> Permission getPermissionByCodeApiV1PermissionsPermissionCodeGet_0()

Retorna os dados de uma permissão específica.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    PermissionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PermissionsApi(configuration);

let permissionCode: string; // (default to undefined)

const { status, data } = await apiInstance.getPermissionByCodeApiV1PermissionsPermissionCodeGet_0(
    permissionCode
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **permissionCode** | [**string**] |  | defaults to undefined|


### Return type

**Permission**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Permissão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listPermissionsApiV1PermissionsGet**
> Array<Permission> listPermissionsApiV1PermissionsGet()

Lista as permissões disponíveis no sistema (catálogo). Opcionalmente filtra por papel (role_code).  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    PermissionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PermissionsApi(configuration);

let roleCode: RoleCode; //Filtrar permissões por papel (optional) (default to undefined)

const { status, data } = await apiInstance.listPermissionsApiV1PermissionsGet(
    roleCode
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **roleCode** | **RoleCode** | Filtrar permissões por papel | (optional) defaults to undefined|


### Return type

**Array<Permission>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listPermissionsApiV1PermissionsGet_0**
> Array<Permission> listPermissionsApiV1PermissionsGet_0()

Lista as permissões disponíveis no sistema (catálogo). Opcionalmente filtra por papel (role_code).  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    PermissionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PermissionsApi(configuration);

let roleCode: RoleCode; //Filtrar permissões por papel (optional) (default to undefined)

const { status, data } = await apiInstance.listPermissionsApiV1PermissionsGet_0(
    roleCode
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **roleCode** | **RoleCode** | Filtrar permissões por papel | (optional) defaults to undefined|


### Return type

**Array<Permission>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

