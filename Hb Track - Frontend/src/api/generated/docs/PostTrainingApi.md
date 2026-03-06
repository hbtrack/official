# PostTrainingApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost**](#createposttrainingfeedbackapiv1posttrainingsessionssessionidfeedbackpost) | **POST** /api/v1/post-training/sessions/{session_id}/feedback | Registrar feedback pós-treino (atleta)|
|[**createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost_0**](#createposttrainingfeedbackapiv1posttrainingsessionssessionidfeedbackpost_0) | **POST** /api/v1/post-training/sessions/{session_id}/feedback | Registrar feedback pós-treino (atleta)|
|[**getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet**](#getsessionsummaryapiv1posttrainingsessionssessionidsummaryget) | **GET** /api/v1/post-training/sessions/{session_id}/summary | Resumo de sessão pós-treino (atleta e treinador)|
|[**getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet_0**](#getsessionsummaryapiv1posttrainingsessionssessionidsummaryget_0) | **GET** /api/v1/post-training/sessions/{session_id}/summary | Resumo de sessão pós-treino (atleta e treinador)|
|[**listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet**](#listathletefeedbacksapiv1posttrainingathletesathleteidfeedbacksget) | **GET** /api/v1/post-training/athletes/{athlete_id}/feedbacks | Listar feedbacks de atleta (treinador — apenas agregados)|
|[**listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet_0**](#listathletefeedbacksapiv1posttrainingathletesathleteidfeedbacksget_0) | **GET** /api/v1/post-training/athletes/{athlete_id}/feedbacks | Listar feedbacks de atleta (treinador — apenas agregados)|

# **createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost**
> PostTrainingFeedbackResponse createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost(postTrainingFeedbackRequest)

Atleta registra feedback imediato após encerramento da sessão. INV-TRAIN-070: somente aceito se sessão está encerrada. INV-TRAIN-077: texto é privado — treinador não acessa verbatim.

### Example

```typescript
import {
    PostTrainingApi,
    Configuration,
    PostTrainingFeedbackRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new PostTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let postTrainingFeedbackRequest: PostTrainingFeedbackRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost(
    sessionId,
    postTrainingFeedbackRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **postTrainingFeedbackRequest** | **PostTrainingFeedbackRequest**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PostTrainingFeedbackResponse**

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

# **createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost_0**
> PostTrainingFeedbackResponse createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost_0(postTrainingFeedbackRequest)

Atleta registra feedback imediato após encerramento da sessão. INV-TRAIN-070: somente aceito se sessão está encerrada. INV-TRAIN-077: texto é privado — treinador não acessa verbatim.

### Example

```typescript
import {
    PostTrainingApi,
    Configuration,
    PostTrainingFeedbackRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new PostTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let postTrainingFeedbackRequest: PostTrainingFeedbackRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPostTrainingFeedbackApiV1PostTrainingSessionsSessionIdFeedbackPost_0(
    sessionId,
    postTrainingFeedbackRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **postTrainingFeedbackRequest** | **PostTrainingFeedbackRequest**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PostTrainingFeedbackResponse**

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

# **getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet**
> SessionSummaryResponse getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet()

Retorna resumo de performance da sessão encerrada. INV-TRAIN-077: treinador recebe apenas rating médio e contagem — NUNCA o texto verbatim do feedback do atleta.

### Example

```typescript
import {
    PostTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PostTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet(
    sessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionSummaryResponse**

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

# **getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet_0**
> SessionSummaryResponse getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet_0()

Retorna resumo de performance da sessão encerrada. INV-TRAIN-077: treinador recebe apenas rating médio e contagem — NUNCA o texto verbatim do feedback do atleta.

### Example

```typescript
import {
    PostTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PostTrainingApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionSummaryApiV1PostTrainingSessionsSessionIdSummaryGet_0(
    sessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SessionSummaryResponse**

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

# **listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet**
> any listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet()

Treinador lista feedbacks pós-treino de um atleta por sessão. INV-TRAIN-077: retorna somente rating por sessão — NUNCA texto verbatim.

### Example

```typescript
import {
    PostTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PostTrainingApi(configuration);

let athleteId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet(
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
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

# **listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet_0**
> any listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet_0()

Treinador lista feedbacks pós-treino de um atleta por sessão. INV-TRAIN-077: retorna somente rating por sessão — NUNCA texto verbatim.

### Example

```typescript
import {
    PostTrainingApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PostTrainingApi(configuration);

let athleteId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAthleteFeedbacksApiV1PostTrainingAthletesAthleteIdFeedbacksGet_0(
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
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

