# UnifiedRegistrationApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createUnifiedRegistrationApiV1UnifiedRegistrationPost**](#createunifiedregistrationapiv1unifiedregistrationpost) | **POST** /api/v1/unified-registration | Cadastro Unificado de Pessoa|
|[**createUnifiedRegistrationApiV1UnifiedRegistrationPost_0**](#createunifiedregistrationapiv1unifiedregistrationpost_0) | **POST** /api/v1/unified-registration | Cadastro Unificado de Pessoa|
|[**getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet**](#getcreationpermissionsapiv1unifiedregistrationpermissionsget) | **GET** /api/v1/unified-registration/permissions | Permissões de Criação|
|[**getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet_0**](#getcreationpermissionsapiv1unifiedregistrationpermissionsget_0) | **GET** /api/v1/unified-registration/permissions | Permissões de Criação|

# **createUnifiedRegistrationApiV1UnifiedRegistrationPost**
> UnifiedRegistrationResponse createUnifiedRegistrationApiV1UnifiedRegistrationPost(unifiedRegistrationRequest)

Cria uma pessoa no sistema com todos os dados relacionados em uma única operação.          **Tipos de Cadastro:**     - atleta: Cria pessoa + atleta + team_registration     - treinador/coordenador/dirigente: Cria pessoa + membership          **Permissões:**     - super_admin: pode criar todos os tipos     - dirigente: pode criar atleta, treinador, coordenador     - coordenador: pode criar atleta, treinador     - treinador: pode criar atleta          **Criação de Usuário:**     - Se `create_user=true` e email preenchido, cria usuário com acesso ao sistema     - Email de boas-vindas é enviado automaticamente

### Example

```typescript
import {
    UnifiedRegistrationApi,
    Configuration,
    UnifiedRegistrationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new UnifiedRegistrationApi(configuration);

let unifiedRegistrationRequest: UnifiedRegistrationRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createUnifiedRegistrationApiV1UnifiedRegistrationPost(
    unifiedRegistrationRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **unifiedRegistrationRequest** | **UnifiedRegistrationRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**UnifiedRegistrationResponse**

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

# **createUnifiedRegistrationApiV1UnifiedRegistrationPost_0**
> UnifiedRegistrationResponse createUnifiedRegistrationApiV1UnifiedRegistrationPost_0(unifiedRegistrationRequest)

Cria uma pessoa no sistema com todos os dados relacionados em uma única operação.          **Tipos de Cadastro:**     - atleta: Cria pessoa + atleta + team_registration     - treinador/coordenador/dirigente: Cria pessoa + membership          **Permissões:**     - super_admin: pode criar todos os tipos     - dirigente: pode criar atleta, treinador, coordenador     - coordenador: pode criar atleta, treinador     - treinador: pode criar atleta          **Criação de Usuário:**     - Se `create_user=true` e email preenchido, cria usuário com acesso ao sistema     - Email de boas-vindas é enviado automaticamente

### Example

```typescript
import {
    UnifiedRegistrationApi,
    Configuration,
    UnifiedRegistrationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new UnifiedRegistrationApi(configuration);

let unifiedRegistrationRequest: UnifiedRegistrationRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createUnifiedRegistrationApiV1UnifiedRegistrationPost_0(
    unifiedRegistrationRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **unifiedRegistrationRequest** | **UnifiedRegistrationRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**UnifiedRegistrationResponse**

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

# **getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet**
> any getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet()

Retorna os tipos de cadastro que o usuário atual pode criar

### Example

```typescript
import {
    UnifiedRegistrationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UnifiedRegistrationApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet(
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

**any**

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

# **getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet_0**
> any getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet_0()

Retorna os tipos de cadastro que o usuário atual pode criar

### Example

```typescript
import {
    UnifiedRegistrationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UnifiedRegistrationApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCreationPermissionsApiV1UnifiedRegistrationPermissionsGet_0(
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

**any**

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

