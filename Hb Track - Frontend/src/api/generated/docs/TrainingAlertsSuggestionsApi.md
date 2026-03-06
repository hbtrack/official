# TrainingAlertsSuggestionsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost**](#applysuggestionapiv1trainingalertssuggestionssuggestionssuggestionidapplypost) | **POST** /api/v1/training/alerts-suggestions/suggestions/{suggestion_id}/apply | Aplicar Sugestão|
|[**applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost_0**](#applysuggestionapiv1trainingalertssuggestionssuggestionssuggestionidapplypost_0) | **POST** /api/v1/training/alerts-suggestions/suggestions/{suggestion_id}/apply | Aplicar Sugestão|
|[**dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost**](#dismissalertapiv1trainingalertssuggestionsalertsalertiddismisspost) | **POST** /api/v1/training/alerts-suggestions/alerts/{alert_id}/dismiss | Dismissar Alerta|
|[**dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost_0**](#dismissalertapiv1trainingalertssuggestionsalertsalertiddismisspost_0) | **POST** /api/v1/training/alerts-suggestions/alerts/{alert_id}/dismiss | Dismissar Alerta|
|[**dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost**](#dismisssuggestionapiv1trainingalertssuggestionssuggestionssuggestioniddismisspost) | **POST** /api/v1/training/alerts-suggestions/suggestions/{suggestion_id}/dismiss | Dismissar Sugestão|
|[**dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost_0**](#dismisssuggestionapiv1trainingalertssuggestionssuggestionssuggestioniddismisspost_0) | **POST** /api/v1/training/alerts-suggestions/suggestions/{suggestion_id}/dismiss | Dismissar Sugestão|
|[**getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet**](#getactivealertsapiv1trainingalertssuggestionsalertsteamteamidactiveget) | **GET** /api/v1/training/alerts-suggestions/alerts/team/{team_id}/active | Lista Alertas Ativos|
|[**getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet_0**](#getactivealertsapiv1trainingalertssuggestionsalertsteamteamidactiveget_0) | **GET** /api/v1/training/alerts-suggestions/alerts/team/{team_id}/active | Lista Alertas Ativos|
|[**getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet**](#getalerthistoryapiv1trainingalertssuggestionsalertsteamteamidhistoryget) | **GET** /api/v1/training/alerts-suggestions/alerts/team/{team_id}/history | Histórico de Alertas|
|[**getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet_0**](#getalerthistoryapiv1trainingalertssuggestionsalertsteamteamidhistoryget_0) | **GET** /api/v1/training/alerts-suggestions/alerts/team/{team_id}/history | Histórico de Alertas|
|[**getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet**](#getalertstatsapiv1trainingalertssuggestionsalertsteamteamidstatsget) | **GET** /api/v1/training/alerts-suggestions/alerts/team/{team_id}/stats | Estatísticas de Alertas|
|[**getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet_0**](#getalertstatsapiv1trainingalertssuggestionsalertsteamteamidstatsget_0) | **GET** /api/v1/training/alerts-suggestions/alerts/team/{team_id}/stats | Estatísticas de Alertas|
|[**getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet**](#getpendingsuggestionsapiv1trainingalertssuggestionssuggestionsteamteamidpendingget) | **GET** /api/v1/training/alerts-suggestions/suggestions/team/{team_id}/pending | Lista Sugestões Pendentes|
|[**getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet_0**](#getpendingsuggestionsapiv1trainingalertssuggestionssuggestionsteamteamidpendingget_0) | **GET** /api/v1/training/alerts-suggestions/suggestions/team/{team_id}/pending | Lista Sugestões Pendentes|
|[**getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet**](#getsuggestionhistoryapiv1trainingalertssuggestionssuggestionsteamteamidhistoryget) | **GET** /api/v1/training/alerts-suggestions/suggestions/team/{team_id}/history | Histórico de Sugestões|
|[**getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet_0**](#getsuggestionhistoryapiv1trainingalertssuggestionssuggestionsteamteamidhistoryget_0) | **GET** /api/v1/training/alerts-suggestions/suggestions/team/{team_id}/history | Histórico de Sugestões|
|[**getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet**](#getsuggestionstatsapiv1trainingalertssuggestionssuggestionsteamteamidstatsget) | **GET** /api/v1/training/alerts-suggestions/suggestions/team/{team_id}/stats | Estatísticas de Sugestões|
|[**getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet_0**](#getsuggestionstatsapiv1trainingalertssuggestionssuggestionsteamteamidstatsget_0) | **GET** /api/v1/training/alerts-suggestions/suggestions/team/{team_id}/stats | Estatísticas de Sugestões|

# **applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost**
> SuggestionResponse applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost(suggestionApply)

Aplica sugestão ajustando focus_pct das sessões alvo.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration,
    SuggestionApply
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let suggestionId: string; // (default to undefined)
let suggestionApply: SuggestionApply; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost(
    suggestionId,
    suggestionApply,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestionApply** | **SuggestionApply**|  | |
| **suggestionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionResponse**

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

# **applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost_0**
> SuggestionResponse applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost_0(suggestionApply)

Aplica sugestão ajustando focus_pct das sessões alvo.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration,
    SuggestionApply
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let suggestionId: string; // (default to undefined)
let suggestionApply: SuggestionApply; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.applySuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdApplyPost_0(
    suggestionId,
    suggestionApply,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestionApply** | **SuggestionApply**|  | |
| **suggestionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionResponse**

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

# **dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost**
> AlertResponse dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost()

Marca alerta como dismissado (dismissed_at, dismissed_by_user_id).

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let alertId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost(
    alertId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **alertId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AlertResponse**

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

# **dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost_0**
> AlertResponse dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost_0()

Marca alerta como dismissado (dismissed_at, dismissed_by_user_id).

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let alertId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.dismissAlertApiV1TrainingAlertsSuggestionsAlertsAlertIdDismissPost_0(
    alertId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **alertId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AlertResponse**

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

# **dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost**
> SuggestionResponse dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost(suggestionDismiss)

Marca sugestão como dismissada com justificativa.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration,
    SuggestionDismiss
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let suggestionId: string; // (default to undefined)
let suggestionDismiss: SuggestionDismiss; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost(
    suggestionId,
    suggestionDismiss,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestionDismiss** | **SuggestionDismiss**|  | |
| **suggestionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionResponse**

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

# **dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost_0**
> SuggestionResponse dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost_0(suggestionDismiss)

Marca sugestão como dismissada com justificativa.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration,
    SuggestionDismiss
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let suggestionId: string; // (default to undefined)
let suggestionDismiss: SuggestionDismiss; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.dismissSuggestionApiV1TrainingAlertsSuggestionsSuggestionsSuggestionIdDismissPost_0(
    suggestionId,
    suggestionDismiss,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestionDismiss** | **SuggestionDismiss**|  | |
| **suggestionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionResponse**

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

# **getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet**
> Array<AlertResponse> getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet()

Retorna alertas não-dismissados de uma equipe.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let limit: number; // (optional) (default to 10)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet(
    teamId,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<AlertResponse>**

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

# **getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet_0**
> Array<AlertResponse> getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet_0()

Retorna alertas não-dismissados de uma equipe.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let limit: number; // (optional) (default to 10)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getActiveAlertsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdActiveGet_0(
    teamId,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<AlertResponse>**

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

# **getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet**
> AlertListResponse getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet()

Retorna alertas paginados com filtros opcionais.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let page: number; // (optional) (default to 1)
let limit: number; // (optional) (default to 10)
let alertType: string; // (optional) (default to undefined)
let severity: string; // (optional) (default to undefined)
let isActive: boolean; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet(
    teamId,
    page,
    limit,
    alertType,
    severity,
    isActive,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **page** | [**number**] |  | (optional) defaults to 1|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **alertType** | [**string**] |  | (optional) defaults to undefined|
| **severity** | [**string**] |  | (optional) defaults to undefined|
| **isActive** | [**boolean**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AlertListResponse**

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

# **getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet_0**
> AlertListResponse getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet_0()

Retorna alertas paginados com filtros opcionais.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let page: number; // (optional) (default to 1)
let limit: number; // (optional) (default to 10)
let alertType: string; // (optional) (default to undefined)
let severity: string; // (optional) (default to undefined)
let isActive: boolean; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAlertHistoryApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdHistoryGet_0(
    teamId,
    page,
    limit,
    alertType,
    severity,
    isActive,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **page** | [**number**] |  | (optional) defaults to 1|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **alertType** | [**string**] |  | (optional) defaults to undefined|
| **severity** | [**string**] |  | (optional) defaults to undefined|
| **isActive** | [**boolean**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AlertListResponse**

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

# **getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet**
> AlertStatsResponse getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet()

Retorna estatísticas agregadas de alertas.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let alertType: string; // (optional) (default to undefined)
let severity: string; // (optional) (default to undefined)
let startDate: string; // (optional) (default to undefined)
let endDate: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet(
    teamId,
    alertType,
    severity,
    startDate,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **alertType** | [**string**] |  | (optional) defaults to undefined|
| **severity** | [**string**] |  | (optional) defaults to undefined|
| **startDate** | [**string**] |  | (optional) defaults to undefined|
| **endDate** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AlertStatsResponse**

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

# **getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet_0**
> AlertStatsResponse getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet_0()

Retorna estatísticas agregadas de alertas.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let alertType: string; // (optional) (default to undefined)
let severity: string; // (optional) (default to undefined)
let startDate: string; // (optional) (default to undefined)
let endDate: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAlertStatsApiV1TrainingAlertsSuggestionsAlertsTeamTeamIdStatsGet_0(
    teamId,
    alertType,
    severity,
    startDate,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **alertType** | [**string**] |  | (optional) defaults to undefined|
| **severity** | [**string**] |  | (optional) defaults to undefined|
| **startDate** | [**string**] |  | (optional) defaults to undefined|
| **endDate** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AlertStatsResponse**

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

# **getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet**
> Array<SuggestionResponse> getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet()

Retorna sugestões pendentes de uma equipe.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let limit: number; // (optional) (default to 10)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet(
    teamId,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<SuggestionResponse>**

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

# **getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet_0**
> Array<SuggestionResponse> getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet_0()

Retorna sugestões pendentes de uma equipe.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let limit: number; // (optional) (default to 10)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPendingSuggestionsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdPendingGet_0(
    teamId,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<SuggestionResponse>**

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

# **getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet**
> SuggestionListResponse getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet()

Retorna sugestões paginadas com filtros opcionais.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let page: number; // (optional) (default to 1)
let limit: number; // (optional) (default to 10)
let type: string; // (optional) (default to undefined)
let status: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet(
    teamId,
    page,
    limit,
    type,
    status,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **page** | [**number**] |  | (optional) defaults to 1|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **type** | [**string**] |  | (optional) defaults to undefined|
| **status** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionListResponse**

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

# **getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet_0**
> SuggestionListResponse getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet_0()

Retorna sugestões paginadas com filtros opcionais.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let page: number; // (optional) (default to 1)
let limit: number; // (optional) (default to 10)
let type: string; // (optional) (default to undefined)
let status: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSuggestionHistoryApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdHistoryGet_0(
    teamId,
    page,
    limit,
    type,
    status,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **page** | [**number**] |  | (optional) defaults to 1|
| **limit** | [**number**] |  | (optional) defaults to 10|
| **type** | [**string**] |  | (optional) defaults to undefined|
| **status** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionListResponse**

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

# **getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet**
> SuggestionStatsResponse getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet()

Retorna estatísticas agregadas de sugestões.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let type: string; // (optional) (default to undefined)
let status: string; // (optional) (default to undefined)
let startDate: string; // (optional) (default to undefined)
let endDate: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet(
    teamId,
    type,
    status,
    startDate,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **type** | [**string**] |  | (optional) defaults to undefined|
| **status** | [**string**] |  | (optional) defaults to undefined|
| **startDate** | [**string**] |  | (optional) defaults to undefined|
| **endDate** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionStatsResponse**

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

# **getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet_0**
> SuggestionStatsResponse getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet_0()

Retorna estatísticas agregadas de sugestões.

### Example

```typescript
import {
    TrainingAlertsSuggestionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new TrainingAlertsSuggestionsApi(configuration);

let teamId: string; // (default to undefined)
let type: string; // (optional) (default to undefined)
let status: string; // (optional) (default to undefined)
let startDate: string; // (optional) (default to undefined)
let endDate: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSuggestionStatsApiV1TrainingAlertsSuggestionsSuggestionsTeamTeamIdStatsGet_0(
    teamId,
    type,
    status,
    startDate,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **type** | [**string**] |  | (optional) defaults to undefined|
| **status** | [**string**] |  | (optional) defaults to undefined|
| **startDate** | [**string**] |  | (optional) defaults to undefined|
| **endDate** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestionStatsResponse**

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

