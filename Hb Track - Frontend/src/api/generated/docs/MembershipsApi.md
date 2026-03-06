# MembershipsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost**](#createmembershipfororganizationapiv1organizationsorganizationidmembershipspost) | **POST** /api/v1/organizations/{organization_id}/memberships | Criar vínculo para organização|
|[**createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost_0**](#createmembershipfororganizationapiv1organizationsorganizationidmembershipspost_0) | **POST** /api/v1/organizations/{organization_id}/memberships | Criar vínculo para organização|
|[**endMembershipApiV1MembershipsMembershipIdEndPost**](#endmembershipapiv1membershipsmembershipidendpost) | **POST** /api/v1/memberships/{membership_id}/end | Encerrar vínculo|
|[**endMembershipApiV1MembershipsMembershipIdEndPost_0**](#endmembershipapiv1membershipsmembershipidendpost_0) | **POST** /api/v1/memberships/{membership_id}/end | Encerrar vínculo|
|[**getMembershipByIdApiV1MembershipsMembershipIdGet**](#getmembershipbyidapiv1membershipsmembershipidget) | **GET** /api/v1/memberships/{membership_id} | Obter vínculo por ID|
|[**getMembershipByIdApiV1MembershipsMembershipIdGet_0**](#getmembershipbyidapiv1membershipsmembershipidget_0) | **GET** /api/v1/memberships/{membership_id} | Obter vínculo por ID|
|[**listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet**](#listmembershipsbyorganizationapiv1organizationsorganizationidmembershipsget) | **GET** /api/v1/organizations/{organization_id}/memberships | Listar vínculos por organização (paginado)|
|[**listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet_0**](#listmembershipsbyorganizationapiv1organizationsorganizationidmembershipsget_0) | **GET** /api/v1/organizations/{organization_id}/memberships | Listar vínculos por organização (paginado)|
|[**updateMembershipApiV1MembershipsMembershipIdPatch**](#updatemembershipapiv1membershipsmembershipidpatch) | **PATCH** /api/v1/memberships/{membership_id} | Atualizar vínculo|
|[**updateMembershipApiV1MembershipsMembershipIdPatch_0**](#updatemembershipapiv1membershipsmembershipidpatch_0) | **PATCH** /api/v1/memberships/{membership_id} | Atualizar vínculo|

# **createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost**
> Membership createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost(appSchemasRbacMembershipCreate)

Cria um novo vínculo (membership) user↔organization+role.  **Regras aplicáveis:** R6/R7, RDB9 (exclusividade)

### Example

```typescript
import {
    MembershipsApi,
    Configuration,
    AppSchemasRbacMembershipCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let organizationId: string; // (default to undefined)
let appSchemasRbacMembershipCreate: AppSchemasRbacMembershipCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost(
    organizationId,
    appSchemasRbacMembershipCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasRbacMembershipCreate** | **AppSchemasRbacMembershipCreate**|  | |
| **organizationId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**409** | Vínculo ativo duplicado (RDB9) |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost_0**
> Membership createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost_0(appSchemasRbacMembershipCreate)

Cria um novo vínculo (membership) user↔organization+role.  **Regras aplicáveis:** R6/R7, RDB9 (exclusividade)

### Example

```typescript
import {
    MembershipsApi,
    Configuration,
    AppSchemasRbacMembershipCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let organizationId: string; // (default to undefined)
let appSchemasRbacMembershipCreate: AppSchemasRbacMembershipCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createMembershipForOrganizationApiV1OrganizationsOrganizationIdMembershipsPost_0(
    organizationId,
    appSchemasRbacMembershipCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasRbacMembershipCreate** | **AppSchemasRbacMembershipCreate**|  | |
| **organizationId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**409** | Vínculo ativo duplicado (RDB9) |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **endMembershipApiV1MembershipsMembershipIdEndPost**
> Membership endMembershipApiV1MembershipsMembershipIdEndPost()

Encerra um vínculo ativo (soft delete via status=inativo).  **Regras aplicáveis:** R7 (encerramento de vínculo)

### Example

```typescript
import {
    MembershipsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let membershipId: string; // (default to undefined)
let endDate: string; //Data de encerramento (default: hoje) (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.endMembershipApiV1MembershipsMembershipIdEndPost(
    membershipId,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **membershipId** | [**string**] |  | defaults to undefined|
| **endDate** | [**string**] | Data de encerramento (default: hoje) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**404** | Vínculo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **endMembershipApiV1MembershipsMembershipIdEndPost_0**
> Membership endMembershipApiV1MembershipsMembershipIdEndPost_0()

Encerra um vínculo ativo (soft delete via status=inativo).  **Regras aplicáveis:** R7 (encerramento de vínculo)

### Example

```typescript
import {
    MembershipsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let membershipId: string; // (default to undefined)
let endDate: string; //Data de encerramento (default: hoje) (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.endMembershipApiV1MembershipsMembershipIdEndPost_0(
    membershipId,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **membershipId** | [**string**] |  | defaults to undefined|
| **endDate** | [**string**] | Data de encerramento (default: hoje) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**404** | Vínculo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMembershipByIdApiV1MembershipsMembershipIdGet**
> Membership getMembershipByIdApiV1MembershipsMembershipIdGet()

Retorna os dados de um vínculo específico.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    MembershipsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let membershipId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMembershipByIdApiV1MembershipsMembershipIdGet(
    membershipId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **membershipId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**404** | Vínculo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMembershipByIdApiV1MembershipsMembershipIdGet_0**
> Membership getMembershipByIdApiV1MembershipsMembershipIdGet_0()

Retorna os dados de um vínculo específico.  **Regras aplicáveis:** R25/R26 (permissões)

### Example

```typescript
import {
    MembershipsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let membershipId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMembershipByIdApiV1MembershipsMembershipIdGet_0(
    membershipId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **membershipId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**404** | Vínculo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet**
> MembershipPaginatedResponse listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet()

Lista paginada de vínculos (memberships) de uma organização.  **Regras aplicáveis:** R6/R7, RDB9, R25/R26

### Example

```typescript
import {
    MembershipsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let organizationId: string; // (default to undefined)
let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let orderBy: MembershipOrderBy; //Campo para ordenação (optional) (default to undefined)
let orderDir: OrderDirection; //Direção da ordenação (optional) (default to undefined)
let isActive: boolean; //Filtrar por status ativo/inativo (optional) (default to undefined)
let roleCode: RoleCode; //Filtrar por papel (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet(
    organizationId,
    page,
    limit,
    orderBy,
    orderDir,
    isActive,
    roleCode,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationId** | [**string**] |  | defaults to undefined|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **orderBy** | **MembershipOrderBy** | Campo para ordenação | (optional) defaults to undefined|
| **orderDir** | **OrderDirection** | Direção da ordenação | (optional) defaults to undefined|
| **isActive** | [**boolean**] | Filtrar por status ativo/inativo | (optional) defaults to undefined|
| **roleCode** | **RoleCode** | Filtrar por papel | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MembershipPaginatedResponse**

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

# **listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet_0**
> MembershipPaginatedResponse listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet_0()

Lista paginada de vínculos (memberships) de uma organização.  **Regras aplicáveis:** R6/R7, RDB9, R25/R26

### Example

```typescript
import {
    MembershipsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let organizationId: string; // (default to undefined)
let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let orderBy: MembershipOrderBy; //Campo para ordenação (optional) (default to undefined)
let orderDir: OrderDirection; //Direção da ordenação (optional) (default to undefined)
let isActive: boolean; //Filtrar por status ativo/inativo (optional) (default to undefined)
let roleCode: RoleCode; //Filtrar por papel (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listMembershipsByOrganizationApiV1OrganizationsOrganizationIdMembershipsGet_0(
    organizationId,
    page,
    limit,
    orderBy,
    orderDir,
    isActive,
    roleCode,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationId** | [**string**] |  | defaults to undefined|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **orderBy** | **MembershipOrderBy** | Campo para ordenação | (optional) defaults to undefined|
| **orderDir** | **OrderDirection** | Direção da ordenação | (optional) defaults to undefined|
| **isActive** | [**boolean**] | Filtrar por status ativo/inativo | (optional) defaults to undefined|
| **roleCode** | **RoleCode** | Filtrar por papel | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MembershipPaginatedResponse**

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

# **updateMembershipApiV1MembershipsMembershipIdPatch**
> Membership updateMembershipApiV1MembershipsMembershipIdPatch(membershipUpdate)

Atualiza role_code e/ou is_active de um vínculo existente.  **Regras aplicáveis:** R6/R7, RDB9, R25/R26

### Example

```typescript
import {
    MembershipsApi,
    Configuration,
    MembershipUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let membershipId: string; // (default to undefined)
let membershipUpdate: MembershipUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateMembershipApiV1MembershipsMembershipIdPatch(
    membershipId,
    membershipUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **membershipUpdate** | **MembershipUpdate**|  | |
| **membershipId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**404** | Vínculo não encontrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateMembershipApiV1MembershipsMembershipIdPatch_0**
> Membership updateMembershipApiV1MembershipsMembershipIdPatch_0(membershipUpdate)

Atualiza role_code e/ou is_active de um vínculo existente.  **Regras aplicáveis:** R6/R7, RDB9, R25/R26

### Example

```typescript
import {
    MembershipsApi,
    Configuration,
    MembershipUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MembershipsApi(configuration);

let membershipId: string; // (default to undefined)
let membershipUpdate: MembershipUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateMembershipApiV1MembershipsMembershipIdPatch_0(
    membershipId,
    membershipUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **membershipUpdate** | **MembershipUpdate**|  | |
| **membershipId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Membership**

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
|**404** | Vínculo não encontrado |  -  |
|**422** | Payload inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

