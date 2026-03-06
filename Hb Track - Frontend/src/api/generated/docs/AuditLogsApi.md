# AuditLogsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getAuditLogByIdApiV1AuditLogsAuditLogIdGet**](#getauditlogbyidapiv1auditlogsauditlogidget) | **GET** /api/v1/audit-logs/{audit_log_id} | Obtém um log de auditoria por ID|
|[**getAuditLogByIdApiV1AuditLogsAuditLogIdGet_0**](#getauditlogbyidapiv1auditlogsauditlogidget_0) | **GET** /api/v1/audit-logs/{audit_log_id} | Obtém um log de auditoria por ID|
|[**listAuditLogsApiV1AuditLogsGet**](#listauditlogsapiv1auditlogsget) | **GET** /api/v1/audit-logs | Lista paginada de logs de auditoria|
|[**listAuditLogsApiV1AuditLogsGet_0**](#listauditlogsapiv1auditlogsget_0) | **GET** /api/v1/audit-logs | Lista paginada de logs de auditoria|

# **getAuditLogByIdApiV1AuditLogsAuditLogIdGet**
> AuditLog getAuditLogByIdApiV1AuditLogsAuditLogIdGet()

Retorna detalhes de um log de auditoria específico.  **x-rule-ids**: R25, R26, R31, R32, R42  Erros possíveis: - 401 unauthorized: Token inválido ou ausente - 403 permission_denied: Permissão insuficiente (R25/R26) - 404 not_found: Log de auditoria não encontrado  TODO (FASE 5/6): - Implementar busca por ID - Validar permissões R25/R26 (somente coordenador/dirigente/superadmin) - Verificar se log pertence à organization do token (R34) - Verificar vínculo ativo do requisitante (R42)

### Example

```typescript
import {
    AuditLogsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditLogsApi(configuration);

let auditLogId: string; // (default to undefined)

const { status, data } = await apiInstance.getAuditLogByIdApiV1AuditLogsAuditLogIdGet(
    auditLogId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **auditLogId** | [**string**] |  | defaults to undefined|


### Return type

**AuditLog**

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
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Log de auditoria não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAuditLogByIdApiV1AuditLogsAuditLogIdGet_0**
> AuditLog getAuditLogByIdApiV1AuditLogsAuditLogIdGet_0()

Retorna detalhes de um log de auditoria específico.  **x-rule-ids**: R25, R26, R31, R32, R42  Erros possíveis: - 401 unauthorized: Token inválido ou ausente - 403 permission_denied: Permissão insuficiente (R25/R26) - 404 not_found: Log de auditoria não encontrado  TODO (FASE 5/6): - Implementar busca por ID - Validar permissões R25/R26 (somente coordenador/dirigente/superadmin) - Verificar se log pertence à organization do token (R34) - Verificar vínculo ativo do requisitante (R42)

### Example

```typescript
import {
    AuditLogsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditLogsApi(configuration);

let auditLogId: string; // (default to undefined)

const { status, data } = await apiInstance.getAuditLogByIdApiV1AuditLogsAuditLogIdGet_0(
    auditLogId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **auditLogId** | [**string**] |  | defaults to undefined|


### Return type

**AuditLog**

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
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Log de auditoria não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listAuditLogsApiV1AuditLogsGet**
> AuditLogPaginatedResponse listAuditLogsApiV1AuditLogsGet()

Lista logs de auditoria com filtros por recurso, ação, ator e período.  **x-rule-ids**: R25, R26, R29, R31, R32, R33, R42  Filtros disponíveis: - resource_type: match, training_session, attendance, wellness_pre, wellness_post, etc. - action: game_finalize, game_reopen, wellness_post_update, membership_update, etc. - actor_membership_id: UUID do vínculo do ator - actor_role_code: superadmin, dirigente, coordenador, treinador, atleta - season_id: UUID da temporada - date_range_start/date_range_end: período de ocorrência  Erros possíveis: - 401 unauthorized: Token inválido ou ausente - 403 permission_denied: Permissão insuficiente (R25/R26) - 422 validation_error: Parâmetros de consulta inválidos  TODO (FASE 5/6): - Implementar lógica de busca no banco - Validar permissões R25/R26 (somente coordenador/dirigente/superadmin) - Aplicar filtro implícito por organization_id do token (R34) - Verificar vínculo ativo do requisitante (R42)

### Example

```typescript
import {
    AuditLogsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditLogsApi(configuration);

let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let orderBy: string; //Campo para ordenação (optional) (default to 'occurred_at')
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let resourceType: string; //Tipo do recurso auditado (optional) (default to undefined)
let resourceId: string; //UUID do recurso (optional) (default to undefined)
let action: string; //Ação executada (optional) (default to undefined)
let actorMembershipId: string; //UUID do vínculo do ator (optional) (default to undefined)
let actorRoleCode: ActorRoleCode; //Papel do ator (optional) (default to undefined)
let seasonId: string; //UUID da temporada (optional) (default to undefined)
let dateRangeStart: string; //Data inicial (optional) (default to undefined)
let dateRangeEnd: string; //Data final (optional) (default to undefined)

const { status, data } = await apiInstance.listAuditLogsApiV1AuditLogsGet(
    page,
    limit,
    orderBy,
    orderDir,
    resourceType,
    resourceId,
    action,
    actorMembershipId,
    actorRoleCode,
    seasonId,
    dateRangeStart,
    dateRangeEnd
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **orderBy** | [**string**] | Campo para ordenação | (optional) defaults to 'occurred_at'|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **resourceType** | [**string**] | Tipo do recurso auditado | (optional) defaults to undefined|
| **resourceId** | [**string**] | UUID do recurso | (optional) defaults to undefined|
| **action** | [**string**] | Ação executada | (optional) defaults to undefined|
| **actorMembershipId** | [**string**] | UUID do vínculo do ator | (optional) defaults to undefined|
| **actorRoleCode** | **ActorRoleCode** | Papel do ator | (optional) defaults to undefined|
| **seasonId** | [**string**] | UUID da temporada | (optional) defaults to undefined|
| **dateRangeStart** | [**string**] | Data inicial | (optional) defaults to undefined|
| **dateRangeEnd** | [**string**] | Data final | (optional) defaults to undefined|


### Return type

**AuditLogPaginatedResponse**

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
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Parâmetros de consulta inválidos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listAuditLogsApiV1AuditLogsGet_0**
> AuditLogPaginatedResponse listAuditLogsApiV1AuditLogsGet_0()

Lista logs de auditoria com filtros por recurso, ação, ator e período.  **x-rule-ids**: R25, R26, R29, R31, R32, R33, R42  Filtros disponíveis: - resource_type: match, training_session, attendance, wellness_pre, wellness_post, etc. - action: game_finalize, game_reopen, wellness_post_update, membership_update, etc. - actor_membership_id: UUID do vínculo do ator - actor_role_code: superadmin, dirigente, coordenador, treinador, atleta - season_id: UUID da temporada - date_range_start/date_range_end: período de ocorrência  Erros possíveis: - 401 unauthorized: Token inválido ou ausente - 403 permission_denied: Permissão insuficiente (R25/R26) - 422 validation_error: Parâmetros de consulta inválidos  TODO (FASE 5/6): - Implementar lógica de busca no banco - Validar permissões R25/R26 (somente coordenador/dirigente/superadmin) - Aplicar filtro implícito por organization_id do token (R34) - Verificar vínculo ativo do requisitante (R42)

### Example

```typescript
import {
    AuditLogsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuditLogsApi(configuration);

let page: number; //Número da página (optional) (default to 1)
let limit: number; //Itens por página (optional) (default to 50)
let orderBy: string; //Campo para ordenação (optional) (default to 'occurred_at')
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let resourceType: string; //Tipo do recurso auditado (optional) (default to undefined)
let resourceId: string; //UUID do recurso (optional) (default to undefined)
let action: string; //Ação executada (optional) (default to undefined)
let actorMembershipId: string; //UUID do vínculo do ator (optional) (default to undefined)
let actorRoleCode: ActorRoleCode; //Papel do ator (optional) (default to undefined)
let seasonId: string; //UUID da temporada (optional) (default to undefined)
let dateRangeStart: string; //Data inicial (optional) (default to undefined)
let dateRangeEnd: string; //Data final (optional) (default to undefined)

const { status, data } = await apiInstance.listAuditLogsApiV1AuditLogsGet_0(
    page,
    limit,
    orderBy,
    orderDir,
    resourceType,
    resourceId,
    action,
    actorMembershipId,
    actorRoleCode,
    seasonId,
    dateRangeStart,
    dateRangeEnd
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Número da página | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página | (optional) defaults to 50|
| **orderBy** | [**string**] | Campo para ordenação | (optional) defaults to 'occurred_at'|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **resourceType** | [**string**] | Tipo do recurso auditado | (optional) defaults to undefined|
| **resourceId** | [**string**] | UUID do recurso | (optional) defaults to undefined|
| **action** | [**string**] | Ação executada | (optional) defaults to undefined|
| **actorMembershipId** | [**string**] | UUID do vínculo do ator | (optional) defaults to undefined|
| **actorRoleCode** | **ActorRoleCode** | Papel do ator | (optional) defaults to undefined|
| **seasonId** | [**string**] | UUID da temporada | (optional) defaults to undefined|
| **dateRangeStart** | [**string**] | Data inicial | (optional) defaults to undefined|
| **dateRangeEnd** | [**string**] | Data final | (optional) defaults to undefined|


### Return type

**AuditLogPaginatedResponse**

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
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**422** | Parâmetros de consulta inválidos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

