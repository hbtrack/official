# ReportsMaintenanceApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getViewsStatsApiV1ReportsStatsGet**](#getviewsstatsapiv1reportsstatsget) | **GET** /api/v1/reports/stats | Estatísticas das Materialized Views|
|[**refreshAllViewsApiV1ReportsRefreshAllPost**](#refreshallviewsapiv1reportsrefreshallpost) | **POST** /api/v1/reports/refresh-all | Refresh de Todas as Materialized Views|
|[**refreshSpecificViewApiV1ReportsRefreshViewNamePost**](#refreshspecificviewapiv1reportsrefreshviewnamepost) | **POST** /api/v1/reports/refresh/{view_name} | Refresh Materialized View Específica|

# **getViewsStatsApiV1ReportsStatsGet**
> any getViewsStatsApiV1ReportsStatsGet()

Retorna estatísticas sobre todas as materialized views.      **Informações retornadas:**     - Número de registros em cada view     - Schema e metadados     - Último vacuum/refresh      **Referências RAG:**     - RF29: Monitoramento de performance     - RD85: Otimizações      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsMaintenanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsMaintenanceApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getViewsStatsApiV1ReportsStatsGet(
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

# **refreshAllViewsApiV1ReportsRefreshAllPost**
> any refreshAllViewsApiV1ReportsRefreshAllPost()

Atualiza todas as 4 materialized views do sistema de relatórios.      **Operação:**     - Refresha todas as views com CONCURRENTLY (não bloqueia leituras)     - Retorna estatísticas de cada view após refresh      **Referências RAG:**     - RF29: Performance de queries     - RD85: Índices e otimizações     - R21: Atualização de relatórios      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsMaintenanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsMaintenanceApi(configuration);

let concurrent: boolean; //Usar CONCURRENTLY (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshAllViewsApiV1ReportsRefreshAllPost(
    concurrent,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **concurrent** | [**boolean**] | Usar CONCURRENTLY | (optional) defaults to true|
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

# **refreshSpecificViewApiV1ReportsRefreshViewNamePost**
> any refreshSpecificViewApiV1ReportsRefreshViewNamePost()

Atualiza uma materialized view específica.      **Views disponíveis:**     - training_performance (R1)     - athlete_training_summary (R2)     - wellness_summary (R3)     - medical_cases_summary (R4)      **Referências RAG:**     - RF29: Performance de queries     - RD85: Índices e otimizações     - R21: Atualização de relatórios      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsMaintenanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsMaintenanceApi(configuration);

let viewName: 'training_performance' | 'athlete_training_summary' | 'wellness_summary' | 'medical_cases_summary'; // (default to undefined)
let concurrent: boolean; //Usar CONCURRENTLY (recomendado) (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshSpecificViewApiV1ReportsRefreshViewNamePost(
    viewName,
    concurrent,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **viewName** | [**&#39;training_performance&#39; | &#39;athlete_training_summary&#39; | &#39;wellness_summary&#39; | &#39;medical_cases_summary&#39;**]**Array<&#39;training_performance&#39; &#124; &#39;athlete_training_summary&#39; &#124; &#39;wellness_summary&#39; &#124; &#39;medical_cases_summary&#39;>** |  | defaults to undefined|
| **concurrent** | [**boolean**] | Usar CONCURRENTLY (recomendado) | (optional) defaults to true|
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

