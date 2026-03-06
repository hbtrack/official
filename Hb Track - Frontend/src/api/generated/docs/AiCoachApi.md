# AiCoachApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**applyDraftApiV1AiCoachDraftDraftIdApplyPatch**](#applydraftapiv1aicoachdraftdraftidapplypatch) | **PATCH** /api/v1/ai/coach/draft/{draft_id}/apply | Aplicar rascunho IA aprovado pelo treinador (INV-TRAIN-080)|
|[**applyDraftApiV1AiCoachDraftDraftIdApplyPatch_0**](#applydraftapiv1aicoachdraftdraftidapplypatch_0) | **PATCH** /api/v1/ai/coach/draft/{draft_id}/apply | Aplicar rascunho IA aprovado pelo treinador (INV-TRAIN-080)|
|[**chatApiV1AiChatPost**](#chatapiv1aichatpost) | **POST** /api/v1/ai/chat | Chat conversacional com IA Coach|
|[**chatApiV1AiChatPost_0**](#chatapiv1aichatpost_0) | **POST** /api/v1/ai/chat | Chat conversacional com IA Coach|
|[**justifySuggestionApiV1AiCoachJustifySuggestionPost**](#justifysuggestionapiv1aicoachjustifysuggestionpost) | **POST** /api/v1/ai/coach/justify-suggestion | Obter justificativa de sugestão IA (INV-TRAIN-081)|
|[**justifySuggestionApiV1AiCoachJustifySuggestionPost_0**](#justifysuggestionapiv1aicoachjustifysuggestionpost_0) | **POST** /api/v1/ai/coach/justify-suggestion | Obter justificativa de sugestão IA (INV-TRAIN-081)|
|[**listDraftsApiV1AiCoachDraftsGet**](#listdraftsapiv1aicoachdraftsget) | **GET** /api/v1/ai/coach/drafts | Listar rascunhos pendentes de revisão (treinador)|
|[**listDraftsApiV1AiCoachDraftsGet_0**](#listdraftsapiv1aicoachdraftsget_0) | **GET** /api/v1/ai/coach/drafts | Listar rascunhos pendentes de revisão (treinador)|
|[**suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost**](#suggestmicrocycleapiv1aicoachsuggestmicrocyclepost) | **POST** /api/v1/ai/coach/suggest-microcycle | Sugerir microciclo (treinador — rascunho obrigatório)|
|[**suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost_0**](#suggestmicrocycleapiv1aicoachsuggestmicrocyclepost_0) | **POST** /api/v1/ai/coach/suggest-microcycle | Sugerir microciclo (treinador — rascunho obrigatório)|
|[**suggestSessionApiV1AiCoachSuggestSessionPost**](#suggestsessionapiv1aicoachsuggestsessionpost) | **POST** /api/v1/ai/coach/suggest-session | Sugerir sessão de treino (treinador — rascunho obrigatório)|
|[**suggestSessionApiV1AiCoachSuggestSessionPost_0**](#suggestsessionapiv1aicoachsuggestsessionpost_0) | **POST** /api/v1/ai/coach/suggest-session | Sugerir sessão de treino (treinador — rascunho obrigatório)|

# **applyDraftApiV1AiCoachDraftDraftIdApplyPatch**
> any applyDraftApiV1AiCoachDraftDraftIdApplyPatch(applyDraftRequest)

Treinador aplica rascunho gerado pela IA. INV-TRAIN-080: draft DEVE ser aprovado antes de aplicar — chamar este endpoint implica aprovação. Stub canônico: tabela de drafts pendente de migration futura.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    ApplyDraftRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let draftId: string; // (default to undefined)
let applyDraftRequest: ApplyDraftRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.applyDraftApiV1AiCoachDraftDraftIdApplyPatch(
    draftId,
    applyDraftRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **applyDraftRequest** | **ApplyDraftRequest**|  | |
| **draftId** | [**string**] |  | defaults to undefined|
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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **applyDraftApiV1AiCoachDraftDraftIdApplyPatch_0**
> any applyDraftApiV1AiCoachDraftDraftIdApplyPatch_0(applyDraftRequest)

Treinador aplica rascunho gerado pela IA. INV-TRAIN-080: draft DEVE ser aprovado antes de aplicar — chamar este endpoint implica aprovação. Stub canônico: tabela de drafts pendente de migration futura.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    ApplyDraftRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let draftId: string; // (default to undefined)
let applyDraftRequest: ApplyDraftRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.applyDraftApiV1AiCoachDraftDraftIdApplyPatch_0(
    draftId,
    applyDraftRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **applyDraftRequest** | **ApplyDraftRequest**|  | |
| **draftId** | [**string**] |  | defaults to undefined|
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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **chatApiV1AiChatPost**
> ChatMessageResponse chatApiV1AiChatPost(chatMessageRequest)

Atleta ou treinador envia mensagem para a IA Coach. INV-072: guard de tom imperativo aplicado na resposta. INV-073: filtro de privacidade — conteúdo íntimo do atleta não exposto ao treinador.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    ChatMessageRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let chatMessageRequest: ChatMessageRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.chatApiV1AiChatPost(
    chatMessageRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chatMessageRequest** | **ChatMessageRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ChatMessageResponse**

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

# **chatApiV1AiChatPost_0**
> ChatMessageResponse chatApiV1AiChatPost_0(chatMessageRequest)

Atleta ou treinador envia mensagem para a IA Coach. INV-072: guard de tom imperativo aplicado na resposta. INV-073: filtro de privacidade — conteúdo íntimo do atleta não exposto ao treinador.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    ChatMessageRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let chatMessageRequest: ChatMessageRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.chatApiV1AiChatPost_0(
    chatMessageRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chatMessageRequest** | **ChatMessageRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ChatMessageResponse**

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

# **justifySuggestionApiV1AiCoachJustifySuggestionPost**
> any justifySuggestionApiV1AiCoachJustifySuggestionPost(justifySuggestionRequest)

Retorna justificativa obrigatória para sugestão do tipo \'recomendacao\'. INV-TRAIN-081: sugestão sem justificativa → label \'ideia_generica\'.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    JustifySuggestionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let justifySuggestionRequest: JustifySuggestionRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.justifySuggestionApiV1AiCoachJustifySuggestionPost(
    justifySuggestionRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **justifySuggestionRequest** | **JustifySuggestionRequest**|  | |
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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **justifySuggestionApiV1AiCoachJustifySuggestionPost_0**
> any justifySuggestionApiV1AiCoachJustifySuggestionPost_0(justifySuggestionRequest)

Retorna justificativa obrigatória para sugestão do tipo \'recomendacao\'. INV-TRAIN-081: sugestão sem justificativa → label \'ideia_generica\'.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    JustifySuggestionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let justifySuggestionRequest: JustifySuggestionRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.justifySuggestionApiV1AiCoachJustifySuggestionPost_0(
    justifySuggestionRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **justifySuggestionRequest** | **JustifySuggestionRequest**|  | |
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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listDraftsApiV1AiCoachDraftsGet**
> DraftListResponse listDraftsApiV1AiCoachDraftsGet()

Lista rascunhos de sessões/microciclos gerados pela IA aguardando aprovação do treinador. INV-080: nenhum draft é autopublicado.

### Example

```typescript
import {
    AiCoachApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDraftsApiV1AiCoachDraftsGet(
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

**DraftListResponse**

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

# **listDraftsApiV1AiCoachDraftsGet_0**
> DraftListResponse listDraftsApiV1AiCoachDraftsGet_0()

Lista rascunhos de sessões/microciclos gerados pela IA aguardando aprovação do treinador. INV-080: nenhum draft é autopublicado.

### Example

```typescript
import {
    AiCoachApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listDraftsApiV1AiCoachDraftsGet_0(
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

**DraftListResponse**

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

# **suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost**
> any suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost(suggestMicrocycleRequest)

INV-080: microciclo sugerido sempre como draft. INV-081: sem justificativa → label \'ideia_generica\'.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    SuggestMicrocycleRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let suggestMicrocycleRequest: SuggestMicrocycleRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost(
    suggestMicrocycleRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestMicrocycleRequest** | **SuggestMicrocycleRequest**|  | |
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
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost_0**
> any suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost_0(suggestMicrocycleRequest)

INV-080: microciclo sugerido sempre como draft. INV-081: sem justificativa → label \'ideia_generica\'.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    SuggestMicrocycleRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let suggestMicrocycleRequest: SuggestMicrocycleRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestMicrocycleApiV1AiCoachSuggestMicrocyclePost_0(
    suggestMicrocycleRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestMicrocycleRequest** | **SuggestMicrocycleRequest**|  | |
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
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **suggestSessionApiV1AiCoachSuggestSessionPost**
> SuggestSessionResponse suggestSessionApiV1AiCoachSuggestSessionPost(suggestSessionRequest)

Treinador solicita sugestão de sessão à IA. INV-080: resultado SEMPRE criado como draft — nunca autopublicado. INV-081: justificativa obrigatória; sem ela → label \'ideia_generica\'.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    SuggestSessionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let suggestSessionRequest: SuggestSessionRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestSessionApiV1AiCoachSuggestSessionPost(
    suggestSessionRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestSessionRequest** | **SuggestSessionRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestSessionResponse**

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

# **suggestSessionApiV1AiCoachSuggestSessionPost_0**
> SuggestSessionResponse suggestSessionApiV1AiCoachSuggestSessionPost_0(suggestSessionRequest)

Treinador solicita sugestão de sessão à IA. INV-080: resultado SEMPRE criado como draft — nunca autopublicado. INV-081: justificativa obrigatória; sem ela → label \'ideia_generica\'.

### Example

```typescript
import {
    AiCoachApi,
    Configuration,
    SuggestSessionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AiCoachApi(configuration);

let suggestSessionRequest: SuggestSessionRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.suggestSessionApiV1AiCoachSuggestSessionPost_0(
    suggestSessionRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **suggestSessionRequest** | **SuggestSessionRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SuggestSessionResponse**

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

