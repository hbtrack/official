# MediaUploadApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**signUploadApiV1MediaSignUploadGet**](#signuploadapiv1mediasignuploadget) | **GET** /api/v1/media/sign-upload | Obter assinatura para upload Cloudinary|
|[**validateUploadUrlApiV1MediaValidateUrlGet**](#validateuploadurlapiv1mediavalidateurlget) | **GET** /api/v1/media/validate-url | Validar URL de upload Cloudinary|

# **signUploadApiV1MediaSignUploadGet**
> CloudinarySignatureResponse signUploadApiV1MediaSignUploadGet()

Gera assinatura para upload direto ao Cloudinary (client-side).          ## Fluxo:     1. Frontend chama este endpoint com o tipo de mídia     2. Backend retorna cloud_name, api_key, timestamp, signature     3. Frontend faz upload direto ao Cloudinary     4. Frontend envia URL resultante no payload da Ficha Única          ## Tipos de mídia:     - **photo**: Fotos de perfil (folder: athletes/photos ou persons/photos)     - **document**: Documentos (RG, certidões) (folder: documents)          ## Segurança:     - Assinatura expira em 1 hora     - Requer autenticação

### Example

```typescript
import {
    MediaUploadApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MediaUploadApi(configuration);

let mediaType: 'photo' | 'document'; //Tipo de mídia: photo ou document (optional) (default to 'photo')
let entityType: string; //Tipo de entidade: person, athlete, organization (optional) (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.signUploadApiV1MediaSignUploadGet(
    mediaType,
    entityType,
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
| **mediaType** | [**&#39;photo&#39; | &#39;document&#39;**]**Array<&#39;photo&#39; &#124; &#39;document&#39;>** | Tipo de mídia: photo ou document | (optional) defaults to 'photo'|
| **entityType** | [**string**] | Tipo de entidade: person, athlete, organization | (optional) defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CloudinarySignatureResponse**

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

# **validateUploadUrlApiV1MediaValidateUrlGet**
> any validateUploadUrlApiV1MediaValidateUrlGet()

Valida se uma URL de upload é do Cloudinary e está no formato esperado.          Útil para validação server-side antes de salvar a URL no banco.

### Example

```typescript
import {
    MediaUploadApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MediaUploadApi(configuration);

let url: string; //URL do arquivo no Cloudinary (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.validateUploadUrlApiV1MediaValidateUrlGet(
    url,
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
| **url** | [**string**] | URL do arquivo no Cloudinary | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
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

