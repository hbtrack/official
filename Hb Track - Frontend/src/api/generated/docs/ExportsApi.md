# ExportsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**checkExportRateLimitApiV1AnalyticsExportRateLimitGet**](#checkexportratelimitapiv1analyticsexportratelimitget) | **GET** /api/v1/analytics/export-rate-limit | Verifica rate limit atual|
|[**getExportJobStatusApiV1AnalyticsExportsJobIdGet**](#getexportjobstatusapiv1analyticsexportsjobidget) | **GET** /api/v1/analytics/exports/{job_id} | Consulta status de export job|
|[**listUserExportsApiV1AnalyticsExportsGet**](#listuserexportsapiv1analyticsexportsget) | **GET** /api/v1/analytics/exports | Lista exports do usuário|
|[**requestAnalyticsPdfExportApiV1AnalyticsExportPdfPost**](#requestanalyticspdfexportapiv1analyticsexportpdfpost) | **POST** /api/v1/analytics/export-pdf | Solicita export PDF analytics|

# **checkExportRateLimitApiV1AnalyticsExportRateLimitGet**
> ExportRateLimitResponse checkExportRateLimitApiV1AnalyticsExportRateLimitGet()

Retorna informações sobre rate limit do usuário.          Útil para:     - Exibir no frontend: \"Você pode exportar mais X vezes hoje\"     - Prevenir tentativas de export quando limite atingido     - Mostrar quando limite reseta (meia-noite)

### Example

```typescript
import {
    ExportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportsApi(configuration);

let exportType: string; //Tipo de export (optional) (default to 'analytics_pdf')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.checkExportRateLimitApiV1AnalyticsExportRateLimitGet(
    exportType,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **exportType** | [**string**] | Tipo de export | (optional) defaults to 'analytics_pdf'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExportRateLimitResponse**

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

# **getExportJobStatusApiV1AnalyticsExportsJobIdGet**
> ExportJobResponse getExportJobStatusApiV1AnalyticsExportsJobIdGet()

Retorna status atual do job de export.          **Status possíveis**:     - `pending`: Na fila (Celery worker irá processar)     - `processing`: Sendo gerado neste momento     - `completed`: Pronto para download (file_url disponível)     - `failed`: Erro durante geração (error_message disponível)          **Polling**: Recomendado fazer GET a cada 2-3 segundos até status != pending          **Expiração**: file_url é válido por 7 dias após completed_at

### Example

```typescript
import {
    ExportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportsApi(configuration);

let jobId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getExportJobStatusApiV1AnalyticsExportsJobIdGet(
    jobId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExportJobResponse**

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

# **listUserExportsApiV1AnalyticsExportsGet**
> ExportJobListResponse listUserExportsApiV1AnalyticsExportsGet()

Lista histórico de exports do usuário (paginado).          Útil para:     - Dashboard \"Meus Exports\"     - Redownload de PDFs anteriores (se ainda válidos)     - Histórico de exports com status/data

### Example

```typescript
import {
    ExportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportsApi(configuration);

let page: number; //Página (1-indexed) (optional) (default to 1)
let perPage: number; //Itens por página (optional) (default to 10)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listUserExportsApiV1AnalyticsExportsGet(
    page,
    perPage,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] | Página (1-indexed) | (optional) defaults to 1|
| **perPage** | [**number**] | Itens por página | (optional) defaults to 10|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExportJobListResponse**

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

# **requestAnalyticsPdfExportApiV1AnalyticsExportPdfPost**
> ExportJobResponse requestAnalyticsPdfExportApiV1AnalyticsExportPdfPost(analyticsPDFExportRequest)

Cria job assíncrono para gerar PDF com analytics do team.          **Rate Limit**: 5 exports/dia por usuário          **Fluxo**:     1. Valida rate limit (retorna 429 se excedido)     2. Calcula hash dos params (cache)     3. Verifica se export idêntico já existe e é válido     4. Se cached: retorna job existente (não conta no rate limit)     5. Se novo: cria job, incrementa contador, dispara Celery task          **Polling**: Cliente deve fazer GET /analytics/exports/{id} a cada 2s     para verificar status (pending → processing → completed/failed)          **Cache**: Export idêntico é reutilizado se ainda válido (<7 dias)

### Example

```typescript
import {
    ExportsApi,
    Configuration,
    AnalyticsPDFExportRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new ExportsApi(configuration);

let analyticsPDFExportRequest: AnalyticsPDFExportRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.requestAnalyticsPdfExportApiV1AnalyticsExportPdfPost(
    analyticsPDFExportRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **analyticsPDFExportRequest** | **AnalyticsPDFExportRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ExportJobResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

