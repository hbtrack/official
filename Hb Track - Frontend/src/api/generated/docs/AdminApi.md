# AdminApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**clearCacheApiV1AdminCacheClearPost**](#clearcacheapiv1admincacheclearpost) | **POST** /api/v1/admin/cache/clear | Clear Cache|
|[**clearCacheApiV1AdminCacheClearPost_0**](#clearcacheapiv1admincacheclearpost_0) | **POST** /api/v1/admin/cache/clear | Clear Cache|
|[**getCacheStatisticsApiV1AdminCacheStatsGet**](#getcachestatisticsapiv1admincachestatsget) | **GET** /api/v1/admin/cache/stats | Get Cache Statistics|
|[**getCacheStatisticsApiV1AdminCacheStatsGet_0**](#getcachestatisticsapiv1admincachestatsget_0) | **GET** /api/v1/admin/cache/stats | Get Cache Statistics|
|[**healthUtcSeasonApiV1AdminHealthUtcSeasonGet**](#healthutcseasonapiv1adminhealthutcseasonget) | **GET** /api/v1/admin/health/utc-season | Health Utc Season|
|[**healthUtcSeasonApiV1AdminHealthUtcSeasonGet_0**](#healthutcseasonapiv1adminhealthutcseasonget_0) | **GET** /api/v1/admin/health/utc-season | Health Utc Season|
|[**neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet**](#neoncheckandseedapiv1adminneoncheckandseedget) | **GET** /api/v1/admin/neon/check-and-seed | Neon Check And Seed|
|[**neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet_0**](#neoncheckandseedapiv1adminneoncheckandseedget_0) | **GET** /api/v1/admin/neon/check-and-seed | Neon Check And Seed|

# **clearCacheApiV1AdminCacheClearPost**
> { [key: string]: string; } clearCacheApiV1AdminCacheClearPost()

Limpa todos os caches server-side (dev-only).  Útil para: - Testes - Forçar refresh de dados - Debug

### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.clearCacheApiV1AdminCacheClearPost();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: string; }**

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

# **clearCacheApiV1AdminCacheClearPost_0**
> { [key: string]: string; } clearCacheApiV1AdminCacheClearPost_0()

Limpa todos os caches server-side (dev-only).  Útil para: - Testes - Forçar refresh de dados - Debug

### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.clearCacheApiV1AdminCacheClearPost_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: string; }**

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

# **getCacheStatisticsApiV1AdminCacheStatsGet**
> { [key: string]: any; } getCacheStatisticsApiV1AdminCacheStatsGet()

Retorna estatísticas dos caches server-side (dev-only).  Mostra: - Tamanho atual de cada cache - Capacidade máxima - TTL configurado

### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.getCacheStatisticsApiV1AdminCacheStatsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

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

# **getCacheStatisticsApiV1AdminCacheStatsGet_0**
> { [key: string]: any; } getCacheStatisticsApiV1AdminCacheStatsGet_0()

Retorna estatísticas dos caches server-side (dev-only).  Mostra: - Tamanho atual de cada cache - Capacidade máxima - TTL configurado

### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.getCacheStatisticsApiV1AdminCacheStatsGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

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

# **healthUtcSeasonApiV1AdminHealthUtcSeasonGet**
> { [key: string]: any; } healthUtcSeasonApiV1AdminHealthUtcSeasonGet()


### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.healthUtcSeasonApiV1AdminHealthUtcSeasonGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

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

# **healthUtcSeasonApiV1AdminHealthUtcSeasonGet_0**
> { [key: string]: any; } healthUtcSeasonApiV1AdminHealthUtcSeasonGet_0()


### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.healthUtcSeasonApiV1AdminHealthUtcSeasonGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

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

# **neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet**
> { [key: string]: any; } neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet()


### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

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

# **neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet_0**
> { [key: string]: any; } neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet_0()


### Example

```typescript
import {
    AdminApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AdminApi(configuration);

const { status, data } = await apiInstance.neonCheckAndSeedApiV1AdminNeonCheckAndSeedGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

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

