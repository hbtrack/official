# TeamsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete**](#cancelteammemberinviteapiv1teamsteamidmembersmembershipidcancelinvitedelete) | **DELETE** /api/v1/teams/{team_id}/members/{membership_id}/cancel-invite | Cancel Team Member Invite|
|[**cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete_0**](#cancelteammemberinviteapiv1teamsteamidmembersmembershipidcancelinvitedelete_0) | **DELETE** /api/v1/teams/{team_id}/members/{membership_id}/cancel-invite | Cancel Team Member Invite|
|[**createTeamApiV1TeamsPost**](#createteamapiv1teamspost) | **POST** /api/v1/teams | Create Team|
|[**createTeamApiV1TeamsPost_0**](#createteamapiv1teamspost_0) | **POST** /api/v1/teams | Create Team|
|[**deleteTeamApiV1TeamsTeamIdDelete**](#deleteteamapiv1teamsteamiddelete) | **DELETE** /api/v1/teams/{team_id} | Delete Team|
|[**deleteTeamApiV1TeamsTeamIdDelete_0**](#deleteteamapiv1teamsteamiddelete_0) | **DELETE** /api/v1/teams/{team_id} | Delete Team|
|[**getTeamApiV1TeamsTeamIdGet**](#getteamapiv1teamsteamidget) | **GET** /api/v1/teams/{team_id} | Get Team|
|[**getTeamApiV1TeamsTeamIdGet_0**](#getteamapiv1teamsteamidget_0) | **GET** /api/v1/teams/{team_id} | Get Team|
|[**getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet**](#getteamcoacheshistoryapiv1teamsteamidcoacheshistoryget) | **GET** /api/v1/teams/{team_id}/coaches/history | Histórico de treinadores da equipe|
|[**getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet_0**](#getteamcoacheshistoryapiv1teamsteamidcoacheshistoryget_0) | **GET** /api/v1/teams/{team_id}/coaches/history | Histórico de treinadores da equipe|
|[**getTeamStaffApiV1TeamsTeamIdStaffGet**](#getteamstaffapiv1teamsteamidstaffget) | **GET** /api/v1/teams/{team_id}/staff | Get Team Staff|
|[**getTeamStaffApiV1TeamsTeamIdStaffGet_0**](#getteamstaffapiv1teamsteamidstaffget_0) | **GET** /api/v1/teams/{team_id}/staff | Get Team Staff|
|[**getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet**](#getteamwellnesstopperformersapiv1teamsteamidwellnesstopperformersget) | **GET** /api/v1/teams/{team_id}/wellness-top-performers | Get Team Wellness Top Performers|
|[**getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet_0**](#getteamwellnesstopperformersapiv1teamsteamidwellnesstopperformersget_0) | **GET** /api/v1/teams/{team_id}/wellness-top-performers | Get Team Wellness Top Performers|
|[**moveAthleteToTeam**](#moveathletetoteam) | **POST** /api/v1/teams/{team_id}/registrations | Mover atleta para equipe|
|[**moveAthleteToTeam_0**](#moveathletetoteam_0) | **POST** /api/v1/teams/{team_id}/registrations | Mover atleta para equipe|
|[**reassignTeamCoachApiV1TeamsTeamIdCoachPatch**](#reassignteamcoachapiv1teamsteamidcoachpatch) | **PATCH** /api/v1/teams/{team_id}/coach | Reatribuir treinador da equipe|
|[**reassignTeamCoachApiV1TeamsTeamIdCoachPatch_0**](#reassignteamcoachapiv1teamsteamidcoachpatch_0) | **PATCH** /api/v1/teams/{team_id}/coach | Reatribuir treinador da equipe|
|[**removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete**](#removestaffmemberapiv1teamsteamidstaffmembershipiddelete) | **DELETE** /api/v1/teams/{team_id}/staff/{membership_id} | Remover membro do staff|
|[**removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete_0**](#removestaffmemberapiv1teamsteamidstaffmembershipiddelete_0) | **DELETE** /api/v1/teams/{team_id}/staff/{membership_id} | Remover membro do staff|
|[**resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost**](#resendteammemberinviteapiv1teamsteamidmembersmembershipidresendinvitepost) | **POST** /api/v1/teams/{team_id}/members/{membership_id}/resend-invite | Resend Team Member Invite|
|[**resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost_0**](#resendteammemberinviteapiv1teamsteamidmembersmembershipidresendinvitepost_0) | **POST** /api/v1/teams/{team_id}/members/{membership_id}/resend-invite | Resend Team Member Invite|
|[**updateTeamApiV1TeamsTeamIdPatch**](#updateteamapiv1teamsteamidpatch) | **PATCH** /api/v1/teams/{team_id} | Update Team|
|[**updateTeamApiV1TeamsTeamIdPatch_0**](#updateteamapiv1teamsteamidpatch_0) | **PATCH** /api/v1/teams/{team_id} | Update Team|
|[**updateTeamSettingsApiV1TeamsTeamIdSettingsPatch**](#updateteamsettingsapiv1teamsteamidsettingspatch) | **PATCH** /api/v1/teams/{team_id}/settings | Update Team Settings|
|[**updateTeamSettingsApiV1TeamsTeamIdSettingsPatch_0**](#updateteamsettingsapiv1teamsteamidsettingspatch_0) | **PATCH** /api/v1/teams/{team_id}/settings | Update Team Settings|

# **cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete**
> any cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete()

Cancela convite pendente de membro da equipe.  **Ações:** - Busca TeamMembership com status=\'pendente\' - Busca PasswordReset vinculado ao usuário - Marca token como usado (used_at = now) para desativar - Soft delete do TeamMembership - **NÃO envia email ao convidado** (cancelamento silencioso)  **Permissões:** Dirigente ou Coordenador  **Step 16** do plano de gestão de staff.

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let membershipId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete(
    teamId,
    membershipId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **membershipId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete_0**
> any cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete_0()

Cancela convite pendente de membro da equipe.  **Ações:** - Busca TeamMembership com status=\'pendente\' - Busca PasswordReset vinculado ao usuário - Marca token como usado (used_at = now) para desativar - Soft delete do TeamMembership - **NÃO envia email ao convidado** (cancelamento silencioso)  **Permissões:** Dirigente ou Coordenador  **Step 16** do plano de gestão de staff.

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let membershipId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.cancelTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdCancelInviteDelete_0(
    teamId,
    membershipId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **membershipId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **createTeamApiV1TeamsPost**
> TeamBase createTeamApiV1TeamsPost(teamCreate)

Cria nova equipe. Regras: RF6 Step 4: Implementar lógica role-based - treinador se auto-atribui

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamCreate: TeamCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTeamApiV1TeamsPost(
    teamCreate,
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
| **teamCreate** | **TeamCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

# **createTeamApiV1TeamsPost_0**
> TeamBase createTeamApiV1TeamsPost_0(teamCreate)

Cria nova equipe. Regras: RF6 Step 4: Implementar lógica role-based - treinador se auto-atribui

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamCreate: TeamCreate; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createTeamApiV1TeamsPost_0(
    teamCreate,
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
| **teamCreate** | **TeamCreate**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

# **deleteTeamApiV1TeamsTeamIdDelete**
> deleteTeamApiV1TeamsTeamIdDelete()

Exclui equipe (soft delete). Regras: R29/R33  Comportamento: - Soft delete: marca deleted_at e deleted_reason - Não remove fisicamente do banco

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (optional) (default to 'Exclusão manual')
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTeamApiV1TeamsTeamIdDelete(
    teamId,
    reason,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | (optional) defaults to 'Exclusão manual'|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
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

# **deleteTeamApiV1TeamsTeamIdDelete_0**
> deleteTeamApiV1TeamsTeamIdDelete_0()

Exclui equipe (soft delete). Regras: R29/R33  Comportamento: - Soft delete: marca deleted_at e deleted_reason - Não remove fisicamente do banco

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (optional) (default to 'Exclusão manual')
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteTeamApiV1TeamsTeamIdDelete_0(
    teamId,
    reason,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | (optional) defaults to 'Exclusão manual'|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
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

# **getTeamApiV1TeamsTeamIdGet**
> TeamBase getTeamApiV1TeamsTeamIdGet()

Retorna equipe por ID.

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamApiV1TeamsTeamIdGet(
    teamId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

# **getTeamApiV1TeamsTeamIdGet_0**
> TeamBase getTeamApiV1TeamsTeamIdGet_0()

Retorna equipe por ID.

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamApiV1TeamsTeamIdGet_0(
    teamId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

# **getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet**
> TeamCoachHistoryResponse getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet()

Retorna todos os treinadores que já foram vinculados à equipe (ativos e inativos).  **Step 19:** Endpoint de histórico de coaches.  **Consulta:** - Busca todos TeamMemberships onde OrgMembership.role_id == 3 (treinador) - Ordena por start_at DESC (mais recente primeiro) - Inclui coach atual (end_at IS NULL) e coaches anteriores (end_at preenchido)  **Permissão:** Qualquer membro da equipe

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet(
    teamId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamCoachHistoryResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Histórico retornado com sucesso |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet_0**
> TeamCoachHistoryResponse getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet_0()

Retorna todos os treinadores que já foram vinculados à equipe (ativos e inativos).  **Step 19:** Endpoint de histórico de coaches.  **Consulta:** - Busca todos TeamMemberships onde OrgMembership.role_id == 3 (treinador) - Ordena por start_at DESC (mais recente primeiro) - Inclui coach atual (end_at IS NULL) e coaches anteriores (end_at preenchido)  **Permissão:** Qualquer membro da equipe

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamCoachesHistoryApiV1TeamsTeamIdCoachesHistoryGet_0(
    teamId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamCoachHistoryResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Histórico retornado com sucesso |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTeamStaffApiV1TeamsTeamIdStaffGet**
> TeamStaffResponse getTeamStaffApiV1TeamsTeamIdStaffGet()

Lista staff (treinadores) vinculados à equipe.  Regras: - R25/R26: Permissões por papel - RF7: coach_membership_id principal  Returns:     Lista de membros do staff com informações da pessoa

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let activeOnly: boolean; //Apenas vínculos ativos (optional) (default to true)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamStaffApiV1TeamsTeamIdStaffGet(
    teamId,
    activeOnly,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **activeOnly** | [**boolean**] | Apenas vínculos ativos | (optional) defaults to true|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamStaffResponse**

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

# **getTeamStaffApiV1TeamsTeamIdStaffGet_0**
> TeamStaffResponse getTeamStaffApiV1TeamsTeamIdStaffGet_0()

Lista staff (treinadores) vinculados à equipe.  Regras: - R25/R26: Permissões por papel - RF7: coach_membership_id principal  Returns:     Lista de membros do staff com informações da pessoa

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let activeOnly: boolean; //Apenas vínculos ativos (optional) (default to true)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamStaffApiV1TeamsTeamIdStaffGet_0(
    teamId,
    activeOnly,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **activeOnly** | [**boolean**] | Apenas vínculos ativos | (optional) defaults to true|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamStaffResponse**

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

# **getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet**
> any getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet()

Retorna Top 5 atletas com melhor taxa de resposta de wellness  Relatório de desempenho dos atletas mais comprometidos com wellness.  Args:     team_id: ID do team     month: Mês específico (YYYY-MM) ou None para mês anterior      Returns:     {         \"month\": \"2026-01\",         \"team_id\": \"uuid\",         \"team_name\": \"Sub-20\",         \"top_performers\": [             {                 \"athlete_id\": 10,                 \"athlete_name\": \"João Silva\",                 \"response_rate\": 95.5,                 \"badges_earned_count\": 3,                 \"current_streak_months\": 2,                 \"total_expected\": 20,                 \"total_responded\": 19             }         ]     }  Ordenação: Por response_rate DESC LIMIT 5  Acesso: - Dirigente: Qualquer team da organização - Coordenador/Treinador: Apenas teams que coordena/treina

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let month: string; //Mês de referência (YYYY-MM), default: mês anterior (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet(
    teamId,
    month,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **month** | [**string**] | Mês de referência (YYYY-MM), default: mês anterior | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet_0**
> any getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet_0()

Retorna Top 5 atletas com melhor taxa de resposta de wellness  Relatório de desempenho dos atletas mais comprometidos com wellness.  Args:     team_id: ID do team     month: Mês específico (YYYY-MM) ou None para mês anterior      Returns:     {         \"month\": \"2026-01\",         \"team_id\": \"uuid\",         \"team_name\": \"Sub-20\",         \"top_performers\": [             {                 \"athlete_id\": 10,                 \"athlete_name\": \"João Silva\",                 \"response_rate\": 95.5,                 \"badges_earned_count\": 3,                 \"current_streak_months\": 2,                 \"total_expected\": 20,                 \"total_responded\": 19             }         ]     }  Ordenação: Por response_rate DESC LIMIT 5  Acesso: - Dirigente: Qualquer team da organização - Coordenador/Treinador: Apenas teams que coordena/treina

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let month: string; //Mês de referência (YYYY-MM), default: mês anterior (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamWellnessTopPerformersApiV1TeamsTeamIdWellnessTopPerformersGet_0(
    teamId,
    month,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **month** | [**string**] | Mês de referência (YYYY-MM), default: mês anterior | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **moveAthleteToTeam**
> TeamRegistration moveAthleteToTeam(teamRegistrationMoveRequest)

Move atleta para equipe na temporada.  - Encerra inscricoes ativas na temporada (RDB10) - Cria nova inscricao na equipe alvo

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamRegistrationMoveRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamRegistrationMoveRequest: TeamRegistrationMoveRequest; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.moveAthleteToTeam(
    teamId,
    teamRegistrationMoveRequest,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamRegistrationMoveRequest** | **TeamRegistrationMoveRequest**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Inscricao criada com sucesso |  -  |
|**401** | Token invalido ou ausente |  -  |
|**403** | Permissao insuficiente |  -  |
|**404** | Atleta ou equipe nao encontrada |  -  |
|**409** | Periodo sobreposto (RDB10) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **moveAthleteToTeam_0**
> TeamRegistration moveAthleteToTeam_0(teamRegistrationMoveRequest)

Move atleta para equipe na temporada.  - Encerra inscricoes ativas na temporada (RDB10) - Cria nova inscricao na equipe alvo

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamRegistrationMoveRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamRegistrationMoveRequest: TeamRegistrationMoveRequest; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.moveAthleteToTeam_0(
    teamId,
    teamRegistrationMoveRequest,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamRegistrationMoveRequest** | **TeamRegistrationMoveRequest**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamRegistration**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Inscricao criada com sucesso |  -  |
|**401** | Token invalido ou ausente |  -  |
|**403** | Permissao insuficiente |  -  |
|**404** | Atleta ou equipe nao encontrada |  -  |
|**409** | Periodo sobreposto (RDB10) |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reassignTeamCoachApiV1TeamsTeamIdCoachPatch**
> TeamBase reassignTeamCoachApiV1TeamsTeamIdCoachPatch(teamCoachUpdate)

Substitui o treinador atual por um novo.  **Steps 18 + 21:** Endpoint com notificações integradas.  **Ordem de operações:** 1. Busca equipe e valida coach antigo 2. Busca dados do coach antigo (user_id, nome) 3. **PRIMEIRO:** Encerra vínculo antigo (end_at, status=\'inativo\') 4. Valida novo coach (role_id=3, ativo, mesma org) 5. **DEPOIS:** Cria novo TeamMembership 6. Atualiza team.coach_membership_id 7. Commit 8. Envia notificação + email ao novo coach 9. Envia notificação ao coach antigo (removido)  **Permissão:** Dirigente ou Coordenador

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamCoachUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamCoachUpdate: TeamCoachUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.reassignTeamCoachApiV1TeamsTeamIdCoachPatch(
    teamId,
    teamCoachUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamCoachUpdate** | **TeamCoachUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Coach reatribuído com sucesso |  -  |
|**400** | Validação falhou (novo coach inválido) |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reassignTeamCoachApiV1TeamsTeamIdCoachPatch_0**
> TeamBase reassignTeamCoachApiV1TeamsTeamIdCoachPatch_0(teamCoachUpdate)

Substitui o treinador atual por um novo.  **Steps 18 + 21:** Endpoint com notificações integradas.  **Ordem de operações:** 1. Busca equipe e valida coach antigo 2. Busca dados do coach antigo (user_id, nome) 3. **PRIMEIRO:** Encerra vínculo antigo (end_at, status=\'inativo\') 4. Valida novo coach (role_id=3, ativo, mesma org) 5. **DEPOIS:** Cria novo TeamMembership 6. Atualiza team.coach_membership_id 7. Commit 8. Envia notificação + email ao novo coach 9. Envia notificação ao coach antigo (removido)  **Permissão:** Dirigente ou Coordenador

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamCoachUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamCoachUpdate: TeamCoachUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.reassignTeamCoachApiV1TeamsTeamIdCoachPatch_0(
    teamId,
    teamCoachUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamCoachUpdate** | **TeamCoachUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Coach reatribuído com sucesso |  -  |
|**400** | Validação falhou (novo coach inválido) |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete**
> any removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete()

Remove membro da comissão técnica (dirigente, coordenador ou treinador).  **Step 35:** Endpoint universal com lógica condicional baseada no papel.  **Comportamento:** - **SE treinador (role_id=3):**   - Encerra vínculo (end_at=now(), status=\'inativo\')   - Remove referência team.coach_membership_id = NULL   - Envia notificação via WebSocket ao treinador removido   - Retorna {team_without_coach: true} - **SENÃO (dirigente/coordenador):**   - Soft delete (deleted_at=now(), deleted_reason)   - Retorna {team_without_coach: false}  **Validações:** - 404: team ou membership não encontrado - 400: membership não pertence à equipe - 403: sem permissão (apenas dirigente/coordenador)  **Permissão:** Dirigente ou Coordenador

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let membershipId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete(
    teamId,
    membershipId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **membershipId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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
|**200** | Membro removido com sucesso |  -  |
|**400** | Membership não pertence à equipe |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Equipe ou membership não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete_0**
> any removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete_0()

Remove membro da comissão técnica (dirigente, coordenador ou treinador).  **Step 35:** Endpoint universal com lógica condicional baseada no papel.  **Comportamento:** - **SE treinador (role_id=3):**   - Encerra vínculo (end_at=now(), status=\'inativo\')   - Remove referência team.coach_membership_id = NULL   - Envia notificação via WebSocket ao treinador removido   - Retorna {team_without_coach: true} - **SENÃO (dirigente/coordenador):**   - Soft delete (deleted_at=now(), deleted_reason)   - Retorna {team_without_coach: false}  **Validações:** - 404: team ou membership não encontrado - 400: membership não pertence à equipe - 403: sem permissão (apenas dirigente/coordenador)  **Permissão:** Dirigente ou Coordenador

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let membershipId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.removeStaffMemberApiV1TeamsTeamIdStaffMembershipIdDelete_0(
    teamId,
    membershipId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **membershipId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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
|**200** | Membro removido com sucesso |  -  |
|**400** | Membership não pertence à equipe |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Equipe ou membership não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost**
> any resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost()

Reenvia convite para membro pendente da equipe.  **Regras:** - Apenas membros com status=\'pendente\' - Cooldown de 48h entre reenvios (configurável via INVITE_RESEND_COOLDOWN_HOURS) - Máximo de 3 reenvios por convite (configurável via INVITE_MAX_RESEND_COUNT) - Incrementa resend_count a cada reenvio - Atualiza updated_at para marcar último reenvio - Busca PasswordReset vinculado ao email da pessoa - Atualiza created_at do token para resetar expiry - Reenvia email de convite  **Permissões:** Dirigente ou Coordenador  **Step 16** do plano de gestão de staff.

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let membershipId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost(
    teamId,
    membershipId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **membershipId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost_0**
> any resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost_0()

Reenvia convite para membro pendente da equipe.  **Regras:** - Apenas membros com status=\'pendente\' - Cooldown de 48h entre reenvios (configurável via INVITE_RESEND_COOLDOWN_HOURS) - Máximo de 3 reenvios por convite (configurável via INVITE_MAX_RESEND_COUNT) - Incrementa resend_count a cada reenvio - Atualiza updated_at para marcar último reenvio - Busca PasswordReset vinculado ao email da pessoa - Atualiza created_at do token para resetar expiry - Reenvia email de convite  **Permissões:** Dirigente ou Coordenador  **Step 16** do plano de gestão de staff.

### Example

```typescript
import {
    TeamsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let membershipId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resendTeamMemberInviteApiV1TeamsTeamIdMembersMembershipIdResendInvitePost_0(
    teamId,
    membershipId,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **membershipId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
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

# **updateTeamApiV1TeamsTeamIdPatch**
> TeamBase updateTeamApiV1TeamsTeamIdPatch(teamUpdate)

Atualiza equipe. Regras: RF7, Step 2: Validação de permissão can_manage_teams

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamUpdate: TeamUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTeamApiV1TeamsTeamIdPatch(
    teamId,
    teamUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamUpdate** | **TeamUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

# **updateTeamApiV1TeamsTeamIdPatch_0**
> TeamBase updateTeamApiV1TeamsTeamIdPatch_0(teamUpdate)

Atualiza equipe. Regras: RF7, Step 2: Validação de permissão can_manage_teams

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamUpdate: TeamUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTeamApiV1TeamsTeamIdPatch_0(
    teamId,
    teamUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamUpdate** | **TeamUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

# **updateTeamSettingsApiV1TeamsTeamIdSettingsPatch**
> TeamBase updateTeamSettingsApiV1TeamsTeamIdSettingsPatch(teamSettingsUpdate)

Atualiza configurações da equipe (Step 15).  Permite ajustar o alert_threshold_multiplier que controla a sensibilidade dos alertas de wellness automáticos.  Valores recomendados: - 1.5: Juvenis (mais sensível) - 2.0: Padrão adultos - 2.5: Adultos tolerantes (menos alertas)  Permissões: Dirigente, Coordenador, ou Treinador responsável

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamSettingsUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamSettingsUpdate: TeamSettingsUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTeamSettingsApiV1TeamsTeamIdSettingsPatch(
    teamId,
    teamSettingsUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamSettingsUpdate** | **TeamSettingsUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

# **updateTeamSettingsApiV1TeamsTeamIdSettingsPatch_0**
> TeamBase updateTeamSettingsApiV1TeamsTeamIdSettingsPatch_0(teamSettingsUpdate)

Atualiza configurações da equipe (Step 15).  Permite ajustar o alert_threshold_multiplier que controla a sensibilidade dos alertas de wellness automáticos.  Valores recomendados: - 1.5: Juvenis (mais sensível) - 2.0: Padrão adultos - 2.5: Adultos tolerantes (menos alertas)  Permissões: Dirigente, Coordenador, ou Treinador responsável

### Example

```typescript
import {
    TeamsApi,
    Configuration,
    TeamSettingsUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new TeamsApi(configuration);

let teamId: string; // (default to undefined)
let teamSettingsUpdate: TeamSettingsUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateTeamSettingsApiV1TeamsTeamIdSettingsPatch_0(
    teamId,
    teamSettingsUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamSettingsUpdate** | **TeamSettingsUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamBase**

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

