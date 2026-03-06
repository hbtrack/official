# HealthApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**healthApiV1HealthGet**](#healthapiv1healthget) | **GET** /api/v1/health | Health|
|[**healthApiV1HealthGet_0**](#healthapiv1healthget_0) | **GET** /api/v1/health | Health|
|[**healthFullApiV1HealthFullGet**](#healthfullapiv1healthfullget) | **GET** /api/v1/health/full | Health Full|
|[**healthFullApiV1HealthFullGet_0**](#healthfullapiv1healthfullget_0) | **GET** /api/v1/health/full | Health Full|
|[**livenessApiV1HealthLivenessGet**](#livenessapiv1healthlivenessget) | **GET** /api/v1/health/liveness | Liveness|
|[**livenessApiV1HealthLivenessGet_0**](#livenessapiv1healthlivenessget_0) | **GET** /api/v1/health/liveness | Liveness|
|[**readinessApiV1HealthReadinessGet**](#readinessapiv1healthreadinessget) | **GET** /api/v1/health/readiness | Readiness|
|[**readinessApiV1HealthReadinessGet_0**](#readinessapiv1healthreadinessget_0) | **GET** /api/v1/health/readiness | Readiness|

# **healthApiV1HealthGet**
> any healthApiV1HealthGet()

Health check completo  Verifica: - Database connection - PostgreSQL version - pgcrypto extension (RDB1) - Alembic migration version  Returns:     dict: Status de saúde do sistema

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthApiV1HealthGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **healthApiV1HealthGet_0**
> any healthApiV1HealthGet_0()

Health check completo  Verifica: - Database connection - PostgreSQL version - pgcrypto extension (RDB1) - Alembic migration version  Returns:     dict: Status de saúde do sistema

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthApiV1HealthGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **healthFullApiV1HealthFullGet**
> any healthFullApiV1HealthFullGet()

Healthcheck completo (validações profundas)  Verifica: - Database connection - Critical tables exist - Alembic migration version - Super admin exists (R3, RDB6) - Roles seeded (R4) - Categories seeded (R15) - VIEW v_seasons_with_status exists  Returns:     dict: Status detalhado de saúde com todas as validações

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthFullApiV1HealthFullGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **healthFullApiV1HealthFullGet_0**
> any healthFullApiV1HealthFullGet_0()

Healthcheck completo (validações profundas)  Verifica: - Database connection - Critical tables exist - Alembic migration version - Super admin exists (R3, RDB6) - Roles seeded (R4) - Categories seeded (R15) - VIEW v_seasons_with_status exists  Returns:     dict: Status detalhado de saúde com todas as validações

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthFullApiV1HealthFullGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **livenessApiV1HealthLivenessGet**
> any livenessApiV1HealthLivenessGet()

Liveness probe (Kubernetes)  Retorna 200 se a aplicação está rodando

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.livenessApiV1HealthLivenessGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **livenessApiV1HealthLivenessGet_0**
> any livenessApiV1HealthLivenessGet_0()

Liveness probe (Kubernetes)  Retorna 200 se a aplicação está rodando

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.livenessApiV1HealthLivenessGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **readinessApiV1HealthReadinessGet**
> any readinessApiV1HealthReadinessGet()

Readiness probe (Kubernetes)  Retorna 200 se a aplicação está pronta para receber tráfego

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.readinessApiV1HealthReadinessGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **readinessApiV1HealthReadinessGet_0**
> any readinessApiV1HealthReadinessGet_0()

Readiness probe (Kubernetes)  Retorna 200 se a aplicação está pronta para receber tráfego

### Example

```typescript
import {
    HealthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.readinessApiV1HealthReadinessGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

