# PersonsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createPersonAddressApiV1PersonsPersonIdAddressesPost**](#createpersonaddressapiv1personspersonidaddressespost) | **POST** /api/v1/persons/{person_id}/addresses | Create Person Address|
|[**createPersonAddressApiV1PersonsPersonIdAddressesPost_0**](#createpersonaddressapiv1personspersonidaddressespost_0) | **POST** /api/v1/persons/{person_id}/addresses | Create Person Address|
|[**createPersonApiV1PersonsPost**](#createpersonapiv1personspost) | **POST** /api/v1/persons | Create Person|
|[**createPersonApiV1PersonsPost_0**](#createpersonapiv1personspost_0) | **POST** /api/v1/persons | Create Person|
|[**createPersonContactApiV1PersonsPersonIdContactsPost**](#createpersoncontactapiv1personspersonidcontactspost) | **POST** /api/v1/persons/{person_id}/contacts | Create Person Contact|
|[**createPersonContactApiV1PersonsPersonIdContactsPost_0**](#createpersoncontactapiv1personspersonidcontactspost_0) | **POST** /api/v1/persons/{person_id}/contacts | Create Person Contact|
|[**createPersonDocumentApiV1PersonsPersonIdDocumentsPost**](#createpersondocumentapiv1personspersoniddocumentspost) | **POST** /api/v1/persons/{person_id}/documents | Create Person Document|
|[**createPersonDocumentApiV1PersonsPersonIdDocumentsPost_0**](#createpersondocumentapiv1personspersoniddocumentspost_0) | **POST** /api/v1/persons/{person_id}/documents | Create Person Document|
|[**createPersonMediaApiV1PersonsPersonIdMediaPost**](#createpersonmediaapiv1personspersonidmediapost) | **POST** /api/v1/persons/{person_id}/media | Create Person Media|
|[**createPersonMediaApiV1PersonsPersonIdMediaPost_0**](#createpersonmediaapiv1personspersonidmediapost_0) | **POST** /api/v1/persons/{person_id}/media | Create Person Media|
|[**deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete**](#deletepersonaddressapiv1personspersonidaddressesaddressiddelete) | **DELETE** /api/v1/persons/{person_id}/addresses/{address_id} | Delete Person Address|
|[**deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete_0**](#deletepersonaddressapiv1personspersonidaddressesaddressiddelete_0) | **DELETE** /api/v1/persons/{person_id}/addresses/{address_id} | Delete Person Address|
|[**deletePersonApiV1PersonsPersonIdDelete**](#deletepersonapiv1personspersoniddelete) | **DELETE** /api/v1/persons/{person_id} | Delete Person|
|[**deletePersonApiV1PersonsPersonIdDelete_0**](#deletepersonapiv1personspersoniddelete_0) | **DELETE** /api/v1/persons/{person_id} | Delete Person|
|[**deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete**](#deletepersoncontactapiv1personspersonidcontactscontactiddelete) | **DELETE** /api/v1/persons/{person_id}/contacts/{contact_id} | Delete Person Contact|
|[**deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete_0**](#deletepersoncontactapiv1personspersonidcontactscontactiddelete_0) | **DELETE** /api/v1/persons/{person_id}/contacts/{contact_id} | Delete Person Contact|
|[**deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete**](#deletepersondocumentapiv1personspersoniddocumentsdocumentiddelete) | **DELETE** /api/v1/persons/{person_id}/documents/{document_id} | Delete Person Document|
|[**deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete_0**](#deletepersondocumentapiv1personspersoniddocumentsdocumentiddelete_0) | **DELETE** /api/v1/persons/{person_id}/documents/{document_id} | Delete Person Document|
|[**deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete**](#deletepersonmediaapiv1personspersonidmediamediaiddelete) | **DELETE** /api/v1/persons/{person_id}/media/{media_id} | Delete Person Media|
|[**deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete_0**](#deletepersonmediaapiv1personspersonidmediamediaiddelete_0) | **DELETE** /api/v1/persons/{person_id}/media/{media_id} | Delete Person Media|
|[**getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet**](#getpersonaddressapiv1personspersonidaddressesaddressidget) | **GET** /api/v1/persons/{person_id}/addresses/{address_id} | Get Person Address|
|[**getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet_0**](#getpersonaddressapiv1personspersonidaddressesaddressidget_0) | **GET** /api/v1/persons/{person_id}/addresses/{address_id} | Get Person Address|
|[**getPersonApiV1PersonsPersonIdGet**](#getpersonapiv1personspersonidget) | **GET** /api/v1/persons/{person_id} | Get Person|
|[**getPersonApiV1PersonsPersonIdGet_0**](#getpersonapiv1personspersonidget_0) | **GET** /api/v1/persons/{person_id} | Get Person|
|[**getPersonContactApiV1PersonsPersonIdContactsContactIdGet**](#getpersoncontactapiv1personspersonidcontactscontactidget) | **GET** /api/v1/persons/{person_id}/contacts/{contact_id} | Get Person Contact|
|[**getPersonContactApiV1PersonsPersonIdContactsContactIdGet_0**](#getpersoncontactapiv1personspersonidcontactscontactidget_0) | **GET** /api/v1/persons/{person_id}/contacts/{contact_id} | Get Person Contact|
|[**getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet**](#getpersondocumentapiv1personspersoniddocumentsdocumentidget) | **GET** /api/v1/persons/{person_id}/documents/{document_id} | Get Person Document|
|[**getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet_0**](#getpersondocumentapiv1personspersoniddocumentsdocumentidget_0) | **GET** /api/v1/persons/{person_id}/documents/{document_id} | Get Person Document|
|[**getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet**](#getpersonmediaapiv1personspersonidmediamediaidget) | **GET** /api/v1/persons/{person_id}/media/{media_id} | Get Person Media|
|[**getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet_0**](#getpersonmediaapiv1personspersonidmediamediaidget_0) | **GET** /api/v1/persons/{person_id}/media/{media_id} | Get Person Media|
|[**listPersonAddressesApiV1PersonsPersonIdAddressesGet**](#listpersonaddressesapiv1personspersonidaddressesget) | **GET** /api/v1/persons/{person_id}/addresses | List Person Addresses|
|[**listPersonAddressesApiV1PersonsPersonIdAddressesGet_0**](#listpersonaddressesapiv1personspersonidaddressesget_0) | **GET** /api/v1/persons/{person_id}/addresses | List Person Addresses|
|[**listPersonContactsApiV1PersonsPersonIdContactsGet**](#listpersoncontactsapiv1personspersonidcontactsget) | **GET** /api/v1/persons/{person_id}/contacts | List Person Contacts|
|[**listPersonContactsApiV1PersonsPersonIdContactsGet_0**](#listpersoncontactsapiv1personspersonidcontactsget_0) | **GET** /api/v1/persons/{person_id}/contacts | List Person Contacts|
|[**listPersonDocumentsApiV1PersonsPersonIdDocumentsGet**](#listpersondocumentsapiv1personspersoniddocumentsget) | **GET** /api/v1/persons/{person_id}/documents | List Person Documents|
|[**listPersonDocumentsApiV1PersonsPersonIdDocumentsGet_0**](#listpersondocumentsapiv1personspersoniddocumentsget_0) | **GET** /api/v1/persons/{person_id}/documents | List Person Documents|
|[**listPersonMediaApiV1PersonsPersonIdMediaGet**](#listpersonmediaapiv1personspersonidmediaget) | **GET** /api/v1/persons/{person_id}/media | List Person Media|
|[**listPersonMediaApiV1PersonsPersonIdMediaGet_0**](#listpersonmediaapiv1personspersonidmediaget_0) | **GET** /api/v1/persons/{person_id}/media | List Person Media|
|[**listPersonsApiV1PersonsGet**](#listpersonsapiv1personsget) | **GET** /api/v1/persons | List Persons|
|[**listPersonsApiV1PersonsGet_0**](#listpersonsapiv1personsget_0) | **GET** /api/v1/persons | List Persons|
|[**updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut**](#updatepersonaddressapiv1personspersonidaddressesaddressidput) | **PUT** /api/v1/persons/{person_id}/addresses/{address_id} | Update Person Address|
|[**updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut_0**](#updatepersonaddressapiv1personspersonidaddressesaddressidput_0) | **PUT** /api/v1/persons/{person_id}/addresses/{address_id} | Update Person Address|
|[**updatePersonApiV1PersonsPersonIdPut**](#updatepersonapiv1personspersonidput) | **PUT** /api/v1/persons/{person_id} | Update Person|
|[**updatePersonApiV1PersonsPersonIdPut_0**](#updatepersonapiv1personspersonidput_0) | **PUT** /api/v1/persons/{person_id} | Update Person|
|[**updatePersonContactApiV1PersonsPersonIdContactsContactIdPut**](#updatepersoncontactapiv1personspersonidcontactscontactidput) | **PUT** /api/v1/persons/{person_id}/contacts/{contact_id} | Update Person Contact|
|[**updatePersonContactApiV1PersonsPersonIdContactsContactIdPut_0**](#updatepersoncontactapiv1personspersonidcontactscontactidput_0) | **PUT** /api/v1/persons/{person_id}/contacts/{contact_id} | Update Person Contact|
|[**updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut**](#updatepersondocumentapiv1personspersoniddocumentsdocumentidput) | **PUT** /api/v1/persons/{person_id}/documents/{document_id} | Update Person Document|
|[**updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut_0**](#updatepersondocumentapiv1personspersoniddocumentsdocumentidput_0) | **PUT** /api/v1/persons/{person_id}/documents/{document_id} | Update Person Document|
|[**updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut**](#updatepersonmediaapiv1personspersonidmediamediaidput) | **PUT** /api/v1/persons/{person_id}/media/{media_id} | Update Person Media|
|[**updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut_0**](#updatepersonmediaapiv1personspersonidmediamediaidput_0) | **PUT** /api/v1/persons/{person_id}/media/{media_id} | Update Person Media|

# **createPersonAddressApiV1PersonsPersonIdAddressesPost**
> PersonAddressResponse createPersonAddressApiV1PersonsPersonIdAddressesPost(appSchemasPersonPersonAddressCreate)

Cria novo endereço para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonAddressCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonAddressCreate: AppSchemasPersonPersonAddressCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonAddressApiV1PersonsPersonIdAddressesPost(
    personId,
    appSchemasPersonPersonAddressCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonAddressCreate** | **AppSchemasPersonPersonAddressCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonAddressResponse**

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

# **createPersonAddressApiV1PersonsPersonIdAddressesPost_0**
> PersonAddressResponse createPersonAddressApiV1PersonsPersonIdAddressesPost_0(appSchemasPersonPersonAddressCreate)

Cria novo endereço para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonAddressCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonAddressCreate: AppSchemasPersonPersonAddressCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonAddressApiV1PersonsPersonIdAddressesPost_0(
    personId,
    appSchemasPersonPersonAddressCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonAddressCreate** | **AppSchemasPersonPersonAddressCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonAddressResponse**

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

# **createPersonApiV1PersonsPost**
> PersonResponse createPersonApiV1PersonsPost(appSchemasPersonPersonCreate)

Cria nova pessoa com dados relacionados (V1.2)  Permissões: coordenador, dirigente (R26)  Permite criar pessoa com: - Contatos - Endereços - Documentos - Mídias  Todos em uma única requisição.

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let appSchemasPersonPersonCreate: AppSchemasPersonPersonCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonApiV1PersonsPost(
    appSchemasPersonPersonCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonCreate** | **AppSchemasPersonPersonCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonResponse**

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

# **createPersonApiV1PersonsPost_0**
> PersonResponse createPersonApiV1PersonsPost_0(appSchemasPersonPersonCreate)

Cria nova pessoa com dados relacionados (V1.2)  Permissões: coordenador, dirigente (R26)  Permite criar pessoa com: - Contatos - Endereços - Documentos - Mídias  Todos em uma única requisição.

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let appSchemasPersonPersonCreate: AppSchemasPersonPersonCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonApiV1PersonsPost_0(
    appSchemasPersonPersonCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonCreate** | **AppSchemasPersonPersonCreate**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonResponse**

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

# **createPersonContactApiV1PersonsPersonIdContactsPost**
> PersonContactResponse createPersonContactApiV1PersonsPersonIdContactsPost(appSchemasPersonPersonContactCreate)

Cria novo contato para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonContactCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonContactCreate: AppSchemasPersonPersonContactCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonContactApiV1PersonsPersonIdContactsPost(
    personId,
    appSchemasPersonPersonContactCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonContactCreate** | **AppSchemasPersonPersonContactCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonContactResponse**

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

# **createPersonContactApiV1PersonsPersonIdContactsPost_0**
> PersonContactResponse createPersonContactApiV1PersonsPersonIdContactsPost_0(appSchemasPersonPersonContactCreate)

Cria novo contato para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonContactCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonContactCreate: AppSchemasPersonPersonContactCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonContactApiV1PersonsPersonIdContactsPost_0(
    personId,
    appSchemasPersonPersonContactCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonContactCreate** | **AppSchemasPersonPersonContactCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonContactResponse**

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

# **createPersonDocumentApiV1PersonsPersonIdDocumentsPost**
> PersonDocumentResponse createPersonDocumentApiV1PersonsPersonIdDocumentsPost(appSchemasPersonPersonDocumentCreate)

Cria novo documento para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonDocumentCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonDocumentCreate: AppSchemasPersonPersonDocumentCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonDocumentApiV1PersonsPersonIdDocumentsPost(
    personId,
    appSchemasPersonPersonDocumentCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonDocumentCreate** | **AppSchemasPersonPersonDocumentCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonDocumentResponse**

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

# **createPersonDocumentApiV1PersonsPersonIdDocumentsPost_0**
> PersonDocumentResponse createPersonDocumentApiV1PersonsPersonIdDocumentsPost_0(appSchemasPersonPersonDocumentCreate)

Cria novo documento para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonDocumentCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonDocumentCreate: AppSchemasPersonPersonDocumentCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonDocumentApiV1PersonsPersonIdDocumentsPost_0(
    personId,
    appSchemasPersonPersonDocumentCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonDocumentCreate** | **AppSchemasPersonPersonDocumentCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonDocumentResponse**

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

# **createPersonMediaApiV1PersonsPersonIdMediaPost**
> PersonMediaResponse createPersonMediaApiV1PersonsPersonIdMediaPost(appSchemasPersonPersonMediaCreate)

Cria nova mídia para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonMediaCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonMediaCreate: AppSchemasPersonPersonMediaCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonMediaApiV1PersonsPersonIdMediaPost(
    personId,
    appSchemasPersonPersonMediaCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonMediaCreate** | **AppSchemasPersonPersonMediaCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonMediaResponse**

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

# **createPersonMediaApiV1PersonsPersonIdMediaPost_0**
> PersonMediaResponse createPersonMediaApiV1PersonsPersonIdMediaPost_0(appSchemasPersonPersonMediaCreate)

Cria nova mídia para pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    AppSchemasPersonPersonMediaCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let appSchemasPersonPersonMediaCreate: AppSchemasPersonPersonMediaCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createPersonMediaApiV1PersonsPersonIdMediaPost_0(
    personId,
    appSchemasPersonPersonMediaCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appSchemasPersonPersonMediaCreate** | **AppSchemasPersonPersonMediaCreate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonMediaResponse**

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

# **deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete**
> deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete(personAddressSoftDelete)

Soft delete de endereço

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonAddressSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let addressId: string; // (default to undefined)
let personAddressSoftDelete: PersonAddressSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete(
    personId,
    addressId,
    personAddressSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personAddressSoftDelete** | **PersonAddressSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **addressId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete_0**
> deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete_0(personAddressSoftDelete)

Soft delete de endereço

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonAddressSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let addressId: string; // (default to undefined)
let personAddressSoftDelete: PersonAddressSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonAddressApiV1PersonsPersonIdAddressesAddressIdDelete_0(
    personId,
    addressId,
    personAddressSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personAddressSoftDelete** | **PersonAddressSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **addressId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonApiV1PersonsPersonIdDelete**
> deletePersonApiV1PersonsPersonIdDelete(personSoftDelete)

Soft delete de pessoa e todos os dados relacionados (V1.2)  Permissões: coordenador, dirigente (R26)  Referências RAG: - RDB4: deleted_reason obrigatório - R29: Exclusão lógica de pessoa + contatos + endereços + documentos + mídias

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let personSoftDelete: PersonSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonApiV1PersonsPersonIdDelete(
    personId,
    personSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personSoftDelete** | **PersonSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonApiV1PersonsPersonIdDelete_0**
> deletePersonApiV1PersonsPersonIdDelete_0(personSoftDelete)

Soft delete de pessoa e todos os dados relacionados (V1.2)  Permissões: coordenador, dirigente (R26)  Referências RAG: - RDB4: deleted_reason obrigatório - R29: Exclusão lógica de pessoa + contatos + endereços + documentos + mídias

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let personSoftDelete: PersonSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonApiV1PersonsPersonIdDelete_0(
    personId,
    personSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personSoftDelete** | **PersonSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete**
> deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete(personContactSoftDelete)

Soft delete de contato

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonContactSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let contactId: string; // (default to undefined)
let personContactSoftDelete: PersonContactSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete(
    personId,
    contactId,
    personContactSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personContactSoftDelete** | **PersonContactSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **contactId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete_0**
> deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete_0(personContactSoftDelete)

Soft delete de contato

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonContactSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let contactId: string; // (default to undefined)
let personContactSoftDelete: PersonContactSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonContactApiV1PersonsPersonIdContactsContactIdDelete_0(
    personId,
    contactId,
    personContactSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personContactSoftDelete** | **PersonContactSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **contactId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete**
> deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete(personDocumentSoftDelete)

Soft delete de documento

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonDocumentSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let personDocumentSoftDelete: PersonDocumentSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete(
    personId,
    documentId,
    personDocumentSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personDocumentSoftDelete** | **PersonDocumentSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **documentId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete_0**
> deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete_0(personDocumentSoftDelete)

Soft delete de documento

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonDocumentSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let personDocumentSoftDelete: PersonDocumentSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdDelete_0(
    personId,
    documentId,
    personDocumentSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personDocumentSoftDelete** | **PersonDocumentSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **documentId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete**
> deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete(personMediaSoftDelete)

Soft delete de mídia

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonMediaSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let mediaId: string; // (default to undefined)
let personMediaSoftDelete: PersonMediaSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete(
    personId,
    mediaId,
    personMediaSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personMediaSoftDelete** | **PersonMediaSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **mediaId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete_0**
> deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete_0(personMediaSoftDelete)

Soft delete de mídia

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonMediaSoftDelete
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let mediaId: string; // (default to undefined)
let personMediaSoftDelete: PersonMediaSoftDelete; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deletePersonMediaApiV1PersonsPersonIdMediaMediaIdDelete_0(
    personId,
    mediaId,
    personMediaSoftDelete,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personMediaSoftDelete** | **PersonMediaSoftDelete**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **mediaId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet**
> PersonAddressResponse getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet()

Busca endereço por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let addressId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet(
    personId,
    addressId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **addressId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonAddressResponse**

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

# **getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet_0**
> PersonAddressResponse getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet_0()

Busca endereço por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let addressId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonAddressApiV1PersonsPersonIdAddressesAddressIdGet_0(
    personId,
    addressId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **addressId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonAddressResponse**

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

# **getPersonApiV1PersonsPersonIdGet**
> PersonResponse getPersonApiV1PersonsPersonIdGet()

Busca pessoa por ID com todos os dados relacionados (V1.2)  Permissões: coordenador, dirigente (R26)  Retorna: - Dados básicos da pessoa - Contatos (telefone, email, whatsapp) - Endereços (residencial_1, residencial_2) - Documentos (CPF, RG, CNH) - Mídias (foto_perfil, foto_documento)

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonApiV1PersonsPersonIdGet(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonResponse**

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

# **getPersonApiV1PersonsPersonIdGet_0**
> PersonResponse getPersonApiV1PersonsPersonIdGet_0()

Busca pessoa por ID com todos os dados relacionados (V1.2)  Permissões: coordenador, dirigente (R26)  Retorna: - Dados básicos da pessoa - Contatos (telefone, email, whatsapp) - Endereços (residencial_1, residencial_2) - Documentos (CPF, RG, CNH) - Mídias (foto_perfil, foto_documento)

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonApiV1PersonsPersonIdGet_0(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonResponse**

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

# **getPersonContactApiV1PersonsPersonIdContactsContactIdGet**
> PersonContactResponse getPersonContactApiV1PersonsPersonIdContactsContactIdGet()

Busca contato por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let contactId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonContactApiV1PersonsPersonIdContactsContactIdGet(
    personId,
    contactId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **contactId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonContactResponse**

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

# **getPersonContactApiV1PersonsPersonIdContactsContactIdGet_0**
> PersonContactResponse getPersonContactApiV1PersonsPersonIdContactsContactIdGet_0()

Busca contato por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let contactId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonContactApiV1PersonsPersonIdContactsContactIdGet_0(
    personId,
    contactId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **contactId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonContactResponse**

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

# **getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet**
> PersonDocumentResponse getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet()

Busca documento por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet(
    personId,
    documentId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **documentId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonDocumentResponse**

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

# **getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet_0**
> PersonDocumentResponse getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet_0()

Busca documento por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdGet_0(
    personId,
    documentId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **documentId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonDocumentResponse**

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

# **getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet**
> PersonMediaResponse getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet()

Busca mídia por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let mediaId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet(
    personId,
    mediaId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **mediaId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonMediaResponse**

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

# **getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet_0**
> PersonMediaResponse getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet_0()

Busca mídia por ID

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let mediaId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPersonMediaApiV1PersonsPersonIdMediaMediaIdGet_0(
    personId,
    mediaId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **mediaId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonMediaResponse**

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

# **listPersonAddressesApiV1PersonsPersonIdAddressesGet**
> Array<PersonAddressResponse> listPersonAddressesApiV1PersonsPersonIdAddressesGet()

Lista todos os endereços de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonAddressesApiV1PersonsPersonIdAddressesGet(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonAddressResponse>**

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

# **listPersonAddressesApiV1PersonsPersonIdAddressesGet_0**
> Array<PersonAddressResponse> listPersonAddressesApiV1PersonsPersonIdAddressesGet_0()

Lista todos os endereços de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonAddressesApiV1PersonsPersonIdAddressesGet_0(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonAddressResponse>**

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

# **listPersonContactsApiV1PersonsPersonIdContactsGet**
> Array<PersonContactResponse> listPersonContactsApiV1PersonsPersonIdContactsGet()

Lista todos os contatos de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonContactsApiV1PersonsPersonIdContactsGet(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonContactResponse>**

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

# **listPersonContactsApiV1PersonsPersonIdContactsGet_0**
> Array<PersonContactResponse> listPersonContactsApiV1PersonsPersonIdContactsGet_0()

Lista todos os contatos de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonContactsApiV1PersonsPersonIdContactsGet_0(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonContactResponse>**

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

# **listPersonDocumentsApiV1PersonsPersonIdDocumentsGet**
> Array<PersonDocumentResponse> listPersonDocumentsApiV1PersonsPersonIdDocumentsGet()

Lista todos os documentos de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonDocumentsApiV1PersonsPersonIdDocumentsGet(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonDocumentResponse>**

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

# **listPersonDocumentsApiV1PersonsPersonIdDocumentsGet_0**
> Array<PersonDocumentResponse> listPersonDocumentsApiV1PersonsPersonIdDocumentsGet_0()

Lista todos os documentos de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonDocumentsApiV1PersonsPersonIdDocumentsGet_0(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonDocumentResponse>**

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

# **listPersonMediaApiV1PersonsPersonIdMediaGet**
> Array<PersonMediaResponse> listPersonMediaApiV1PersonsPersonIdMediaGet()

Lista todas as mídias de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonMediaApiV1PersonsPersonIdMediaGet(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonMediaResponse>**

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

# **listPersonMediaApiV1PersonsPersonIdMediaGet_0**
> Array<PersonMediaResponse> listPersonMediaApiV1PersonsPersonIdMediaGet_0()

Lista todas as mídias de uma pessoa

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonMediaApiV1PersonsPersonIdMediaGet_0(
    personId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<PersonMediaResponse>**

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

# **listPersonsApiV1PersonsGet**
> PaginatedResponsePersonListResponse listPersonsApiV1PersonsGet()

Lista todas as pessoas (V1.2) com filtros  Permissões: coordenador, dirigente (R26)  Filtros: - search: busca por nome (case-insensitive) - gender: filtro por gênero (masculino, feminino) - category_id: filtro por categoria (1-7) - team_category_id: filtra apenas atletas da mesma categoria ou inferior (para evitar cadastrar atletas mais velhos em categorias menores)  Referências RAG: - R26: Coordenador e Dirigente têm acesso a dados operacionais - R29: Apenas pessoas não deletadas são listadas

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let skip: number; // (optional) (default to 0)
let limit: number; // (optional) (default to 100)
let search: string; // (optional) (default to undefined)
let gender: string; // (optional) (default to undefined)
let categoryId: number; // (optional) (default to undefined)
let teamCategoryId: number; //Filtrar atletas da mesma categoria ou inferior (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonsApiV1PersonsGet(
    skip,
    limit,
    search,
    gender,
    categoryId,
    teamCategoryId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **skip** | [**number**] |  | (optional) defaults to 0|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **search** | [**string**] |  | (optional) defaults to undefined|
| **gender** | [**string**] |  | (optional) defaults to undefined|
| **categoryId** | [**number**] |  | (optional) defaults to undefined|
| **teamCategoryId** | [**number**] | Filtrar atletas da mesma categoria ou inferior | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PaginatedResponsePersonListResponse**

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

# **listPersonsApiV1PersonsGet_0**
> PaginatedResponsePersonListResponse listPersonsApiV1PersonsGet_0()

Lista todas as pessoas (V1.2) com filtros  Permissões: coordenador, dirigente (R26)  Filtros: - search: busca por nome (case-insensitive) - gender: filtro por gênero (masculino, feminino) - category_id: filtro por categoria (1-7) - team_category_id: filtra apenas atletas da mesma categoria ou inferior (para evitar cadastrar atletas mais velhos em categorias menores)  Referências RAG: - R26: Coordenador e Dirigente têm acesso a dados operacionais - R29: Apenas pessoas não deletadas são listadas

### Example

```typescript
import {
    PersonsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let skip: number; // (optional) (default to 0)
let limit: number; // (optional) (default to 100)
let search: string; // (optional) (default to undefined)
let gender: string; // (optional) (default to undefined)
let categoryId: number; // (optional) (default to undefined)
let teamCategoryId: number; //Filtrar atletas da mesma categoria ou inferior (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPersonsApiV1PersonsGet_0(
    skip,
    limit,
    search,
    gender,
    categoryId,
    teamCategoryId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **skip** | [**number**] |  | (optional) defaults to 0|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **search** | [**string**] |  | (optional) defaults to undefined|
| **gender** | [**string**] |  | (optional) defaults to undefined|
| **categoryId** | [**number**] |  | (optional) defaults to undefined|
| **teamCategoryId** | [**number**] | Filtrar atletas da mesma categoria ou inferior | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PaginatedResponsePersonListResponse**

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

# **updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut**
> PersonAddressResponse updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut(personAddressUpdate)

Atualiza endereço

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonAddressUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let addressId: string; // (default to undefined)
let personAddressUpdate: PersonAddressUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut(
    personId,
    addressId,
    personAddressUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personAddressUpdate** | **PersonAddressUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **addressId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonAddressResponse**

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

# **updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut_0**
> PersonAddressResponse updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut_0(personAddressUpdate)

Atualiza endereço

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonAddressUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let addressId: string; // (default to undefined)
let personAddressUpdate: PersonAddressUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonAddressApiV1PersonsPersonIdAddressesAddressIdPut_0(
    personId,
    addressId,
    personAddressUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personAddressUpdate** | **PersonAddressUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **addressId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonAddressResponse**

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

# **updatePersonApiV1PersonsPersonIdPut**
> PersonResponse updatePersonApiV1PersonsPersonIdPut(personUpdate)

Atualiza dados básicos da pessoa (V1.2)  Permissões: coordenador, dirigente (R26)  Nota: Para atualizar contatos, endereços, documentos ou mídias, use os endpoints específicos.

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let personUpdate: PersonUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonApiV1PersonsPersonIdPut(
    personId,
    personUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personUpdate** | **PersonUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonResponse**

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

# **updatePersonApiV1PersonsPersonIdPut_0**
> PersonResponse updatePersonApiV1PersonsPersonIdPut_0(personUpdate)

Atualiza dados básicos da pessoa (V1.2)  Permissões: coordenador, dirigente (R26)  Nota: Para atualizar contatos, endereços, documentos ou mídias, use os endpoints específicos.

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let personUpdate: PersonUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonApiV1PersonsPersonIdPut_0(
    personId,
    personUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personUpdate** | **PersonUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonResponse**

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

# **updatePersonContactApiV1PersonsPersonIdContactsContactIdPut**
> PersonContactResponse updatePersonContactApiV1PersonsPersonIdContactsContactIdPut(personContactUpdate)

Atualiza contato

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonContactUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let contactId: string; // (default to undefined)
let personContactUpdate: PersonContactUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonContactApiV1PersonsPersonIdContactsContactIdPut(
    personId,
    contactId,
    personContactUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personContactUpdate** | **PersonContactUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **contactId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonContactResponse**

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

# **updatePersonContactApiV1PersonsPersonIdContactsContactIdPut_0**
> PersonContactResponse updatePersonContactApiV1PersonsPersonIdContactsContactIdPut_0(personContactUpdate)

Atualiza contato

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonContactUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let contactId: string; // (default to undefined)
let personContactUpdate: PersonContactUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonContactApiV1PersonsPersonIdContactsContactIdPut_0(
    personId,
    contactId,
    personContactUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personContactUpdate** | **PersonContactUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **contactId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonContactResponse**

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

# **updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut**
> PersonDocumentResponse updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut(personDocumentUpdate)

Atualiza documento

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonDocumentUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let personDocumentUpdate: PersonDocumentUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut(
    personId,
    documentId,
    personDocumentUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personDocumentUpdate** | **PersonDocumentUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **documentId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonDocumentResponse**

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

# **updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut_0**
> PersonDocumentResponse updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut_0(personDocumentUpdate)

Atualiza documento

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonDocumentUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let documentId: string; // (default to undefined)
let personDocumentUpdate: PersonDocumentUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonDocumentApiV1PersonsPersonIdDocumentsDocumentIdPut_0(
    personId,
    documentId,
    personDocumentUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personDocumentUpdate** | **PersonDocumentUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **documentId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonDocumentResponse**

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

# **updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut**
> PersonMediaResponse updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut(personMediaUpdate)

Atualiza mídia

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonMediaUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let mediaId: string; // (default to undefined)
let personMediaUpdate: PersonMediaUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut(
    personId,
    mediaId,
    personMediaUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personMediaUpdate** | **PersonMediaUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **mediaId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonMediaResponse**

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

# **updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut_0**
> PersonMediaResponse updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut_0(personMediaUpdate)

Atualiza mídia

### Example

```typescript
import {
    PersonsApi,
    Configuration,
    PersonMediaUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new PersonsApi(configuration);

let personId: string; // (default to undefined)
let mediaId: string; // (default to undefined)
let personMediaUpdate: PersonMediaUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updatePersonMediaApiV1PersonsPersonIdMediaMediaIdPut_0(
    personId,
    mediaId,
    personMediaUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personMediaUpdate** | **PersonMediaUpdate**|  | |
| **personId** | [**string**] |  | defaults to undefined|
| **mediaId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**PersonMediaResponse**

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

