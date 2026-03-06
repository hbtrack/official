# UsersApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createUserApiV1UsersPost**](#createuserapiv1userspost) | **POST** /api/v1/users | Criar usuário|
|[**createUserApiV1UsersPost_0**](#createuserapiv1userspost_0) | **POST** /api/v1/users | Criar usuário|
|[**deleteUserApiV1UsersUserIdDelete**](#deleteuserapiv1usersuseriddelete) | **DELETE** /api/v1/users/{user_id} | Excluir usuário (soft delete)|
|[**deleteUserApiV1UsersUserIdDelete_0**](#deleteuserapiv1usersuseriddelete_0) | **DELETE** /api/v1/users/{user_id} | Excluir usuário (soft delete)|
|[**getCurrentUserProfileApiV1UsersMeGet**](#getcurrentuserprofileapiv1usersmeget) | **GET** /api/v1/users/me | Obter usuário atual|
|[**getCurrentUserProfileApiV1UsersMeGet_0**](#getcurrentuserprofileapiv1usersmeget_0) | **GET** /api/v1/users/me | Obter usuário atual|
|[**getUserByIdApiV1UsersUserIdGet**](#getuserbyidapiv1usersuseridget) | **GET** /api/v1/users/{user_id} | Obter usuário por ID|
|[**getUserByIdApiV1UsersUserIdGet_0**](#getuserbyidapiv1usersuseridget_0) | **GET** /api/v1/users/{user_id} | Obter usuário por ID|
|[**listUsersApiV1UsersGet**](#listusersapiv1usersget) | **GET** /api/v1/users | Listar usuários (paginado)|
|[**listUsersApiV1UsersGet_0**](#listusersapiv1usersget_0) | **GET** /api/v1/users | Listar usuários (paginado)|
|[**resetUserPasswordApiV1UsersUserIdResetPasswordPost**](#resetuserpasswordapiv1usersuseridresetpasswordpost) | **POST** /api/v1/users/{user_id}/reset-password | Resetar senha do usuário|
|[**resetUserPasswordApiV1UsersUserIdResetPasswordPost_0**](#resetuserpasswordapiv1usersuseridresetpasswordpost_0) | **POST** /api/v1/users/{user_id}/reset-password | Resetar senha do usuário|
|[**updateUserApiV1UsersUserIdPatch**](#updateuserapiv1usersuseridpatch) | **PATCH** /api/v1/users/{user_id} | Atualizar usuário|
|[**updateUserApiV1UsersUserIdPatch_0**](#updateuserapiv1usersuseridpatch_0) | **PATCH** /api/v1/users/{user_id} | Atualizar usuário|

# **createUserApiV1UsersPost**
> User createUserApiV1UsersPost(appSchemasRbacUserCreate)

Cria um novo usuário no sistema.  **Regras V1.2 aplicáveis:** - RF1: Cadeia hierárquica de criação (Super Admin > Dirigente > Coordenador > Treinador) - RF1.1: Vínculos automáticos por papel:   - Dirigente: NÃO cria vínculo organizacional automático   - Coordenador/Treinador: Cria vínculo automático (org_membership) com organização do criador   - Atleta: Usado endpoint específico de atletas - R25/R26: Permissões por papel e escopo - R31/R32: Auditoria de criação

### Example

```typescript
import {
    UsersApi,
    Configuration,
    AppSchemasRbacUserCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let appSchemasRbacUserCreate: AppSchemasRbacUserCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createUserApiV1UsersPost(
    appSchemasRbacUserCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasRbacUserCreate** | **AppSchemasRbacUserCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**User**

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
|**409** | Email já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createUserApiV1UsersPost_0**
> User createUserApiV1UsersPost_0(appSchemasRbacUserCreate)

Cria um novo usuário no sistema.  **Regras V1.2 aplicáveis:** - RF1: Cadeia hierárquica de criação (Super Admin > Dirigente > Coordenador > Treinador) - RF1.1: Vínculos automáticos por papel:   - Dirigente: NÃO cria vínculo organizacional automático   - Coordenador/Treinador: Cria vínculo automático (org_membership) com organização do criador   - Atleta: Usado endpoint específico de atletas - R25/R26: Permissões por papel e escopo - R31/R32: Auditoria de criação

### Example

```typescript
import {
    UsersApi,
    Configuration,
    AppSchemasRbacUserCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let appSchemasRbacUserCreate: AppSchemasRbacUserCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createUserApiV1UsersPost_0(
    appSchemasRbacUserCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasRbacUserCreate** | **AppSchemasRbacUserCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**User**

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
|**409** | Email já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteUserApiV1UsersUserIdDelete**
> deleteUserApiV1UsersUserIdDelete()

Exclui um usuário do sistema (soft delete).  **Regras aplicáveis:** R25/R26 (permissões), R29/R33 (soft delete)  **Comportamento:** - Soft delete: marca deleted_at e deleted_reason - Não remove fisicamente do banco

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteUserApiV1UsersUserIdDelete(
    userId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|
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
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteUserApiV1UsersUserIdDelete_0**
> deleteUserApiV1UsersUserIdDelete_0()

Exclui um usuário do sistema (soft delete).  **Regras aplicáveis:** R25/R26 (permissões), R29/R33 (soft delete)  **Comportamento:** - Soft delete: marca deleted_at e deleted_reason - Não remove fisicamente do banco

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteUserApiV1UsersUserIdDelete_0(
    userId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|
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
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCurrentUserProfileApiV1UsersMeGet**
> User getCurrentUserProfileApiV1UsersMeGet()

Retorna os dados do usuário autenticado.  Útil para obter informações do perfil do usuário logado.

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCurrentUserProfileApiV1UsersMeGet(
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

**User**

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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCurrentUserProfileApiV1UsersMeGet_0**
> User getCurrentUserProfileApiV1UsersMeGet_0()

Retorna os dados do usuário autenticado.  Útil para obter informações do perfil do usuário logado.

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCurrentUserProfileApiV1UsersMeGet_0(
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

**User**

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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUserByIdApiV1UsersUserIdGet**
> User getUserByIdApiV1UsersUserIdGet()

Retorna os dados de um usuário específico.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getUserByIdApiV1UsersUserIdGet(
    userId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**User**

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
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUserByIdApiV1UsersUserIdGet_0**
> User getUserByIdApiV1UsersUserIdGet_0()

Retorna os dados de um usuário específico.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getUserByIdApiV1UsersUserIdGet_0(
    userId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**User**

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
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listUsersApiV1UsersGet**
> UserPaginatedResponse listUsersApiV1UsersGet()

Lista paginada de usuários do sistema.  **Regras aplicáveis:** R25/R26 (permissões), R42 (vínculo ativo), R29/R33 (histórico)  **Comportamento:** - Retorna usuários ativos por padrão - Filtrar por search (full_name/email) quando necessário - Escopo organizacional aplicado automaticamente via JWT (R34)

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let orderBy: UserOrderBy; //Campo para ordenação (optional) (default to undefined)
let orderDir: OrderDirection; //Direção da ordenação (optional) (default to undefined)
let search: string; //Busca por full_name ou email (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listUsersApiV1UsersGet(
    page,
    limit,
    orderBy,
    orderDir,
    search,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **orderBy** | **UserOrderBy** | Campo para ordenação | (optional) defaults to undefined|
| **orderDir** | **OrderDirection** | Direção da ordenação | (optional) defaults to undefined|
| **search** | [**string**] | Busca por full_name ou email | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**UserPaginatedResponse**

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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listUsersApiV1UsersGet_0**
> UserPaginatedResponse listUsersApiV1UsersGet_0()

Lista paginada de usuários do sistema.  **Regras aplicáveis:** R25/R26 (permissões), R42 (vínculo ativo), R29/R33 (histórico)  **Comportamento:** - Retorna usuários ativos por padrão - Filtrar por search (full_name/email) quando necessário - Escopo organizacional aplicado automaticamente via JWT (R34)

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let orderBy: UserOrderBy; //Campo para ordenação (optional) (default to undefined)
let orderDir: OrderDirection; //Direção da ordenação (optional) (default to undefined)
let search: string; //Busca por full_name ou email (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listUsersApiV1UsersGet_0(
    page,
    limit,
    orderBy,
    orderDir,
    search,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **orderBy** | **UserOrderBy** | Campo para ordenação | (optional) defaults to undefined|
| **orderDir** | **OrderDirection** | Direção da ordenação | (optional) defaults to undefined|
| **search** | [**string**] | Busca por full_name ou email | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**UserPaginatedResponse**

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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetUserPasswordApiV1UsersUserIdResetPasswordPost**
> any resetUserPasswordApiV1UsersUserIdResetPasswordPost(appApiV1RoutersUsersResetPasswordRequest)

Reseta a senha de um usuário.

### Example

```typescript
import {
    UsersApi,
    Configuration,
    AppApiV1RoutersUsersResetPasswordRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let appApiV1RoutersUsersResetPasswordRequest: AppApiV1RoutersUsersResetPasswordRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resetUserPasswordApiV1UsersUserIdResetPasswordPost(
    userId,
    appApiV1RoutersUsersResetPasswordRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appApiV1RoutersUsersResetPasswordRequest** | **AppApiV1RoutersUsersResetPasswordRequest**|  | |
| **userId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

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
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resetUserPasswordApiV1UsersUserIdResetPasswordPost_0**
> any resetUserPasswordApiV1UsersUserIdResetPasswordPost_0(appApiV1RoutersUsersResetPasswordRequest)

Reseta a senha de um usuário.

### Example

```typescript
import {
    UsersApi,
    Configuration,
    AppApiV1RoutersUsersResetPasswordRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let appApiV1RoutersUsersResetPasswordRequest: AppApiV1RoutersUsersResetPasswordRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resetUserPasswordApiV1UsersUserIdResetPasswordPost_0(
    userId,
    appApiV1RoutersUsersResetPasswordRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appApiV1RoutersUsersResetPasswordRequest** | **AppApiV1RoutersUsersResetPasswordRequest**|  | |
| **userId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

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
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateUserApiV1UsersUserIdPatch**
> User updateUserApiV1UsersUserIdPatch(userUpdate)

Atualiza dados de um usuário existente.  **Regras aplicáveis:** R25/R26 (permissões), R31/R32 (auditoria)  **Comportamento:** - Valida unicidade de email (se alterado) - Registra auditoria da alteração (R31/R32)

### Example

```typescript
import {
    UsersApi,
    Configuration,
    UserUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let userUpdate: UserUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateUserApiV1UsersUserIdPatch(
    userId,
    userUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userUpdate** | **UserUpdate**|  | |
| **userId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**User**

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
|**409** | Email já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateUserApiV1UsersUserIdPatch_0**
> User updateUserApiV1UsersUserIdPatch_0(userUpdate)

Atualiza dados de um usuário existente.  **Regras aplicáveis:** R25/R26 (permissões), R31/R32 (auditoria)  **Comportamento:** - Valida unicidade de email (se alterado) - Registra auditoria da alteração (R31/R32)

### Example

```typescript
import {
    UsersApi,
    Configuration,
    UserUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let userUpdate: UserUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateUserApiV1UsersUserIdPatch_0(
    userId,
    userUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userUpdate** | **UserUpdate**|  | |
| **userId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**User**

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
|**409** | Email já cadastrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

