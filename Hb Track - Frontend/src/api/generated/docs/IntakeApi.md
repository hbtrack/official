# IntakeApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**autocompleteOrganizationsApiV1IntakeOrganizationsAutocompleteGet**](#autocompleteorganizationsapiv1intakeorganizationsautocompleteget) | **GET** /api/v1/intake/organizations/autocomplete | Buscar Organizações (Autocomplete)|
|[**autocompleteSeasonsApiV1IntakeSeasonsAutocompleteGet**](#autocompleteseasonsapiv1intakeseasonsautocompleteget) | **GET** /api/v1/intake/seasons/autocomplete | Buscar Temporadas (Autocomplete)|
|[**autocompleteTeamsApiV1IntakeTeamsAutocompleteGet**](#autocompleteteamsapiv1intaketeamsautocompleteget) | **GET** /api/v1/intake/teams/autocomplete | Buscar Equipes (Autocomplete)|
|[**createFichaUnicaApiV1IntakeFichaUnicaPost**](#createfichaunicaapiv1intakefichaunicapost) | **POST** /api/v1/intake/ficha-unica | Cadastro via Ficha Única|
|[**dryRunFichaUnicaApiV1IntakeFichaUnicaDryRunPost**](#dryrunfichaunicaapiv1intakefichaunicadryrunpost) | **POST** /api/v1/intake/ficha-unica/dry-run | Preview da Ficha Única (dry-run)|
|[**savePersonMediaApiV1IntakePersonsPersonIdMediaPost**](#savepersonmediaapiv1intakepersonspersonidmediapost) | **POST** /api/v1/intake/persons/{person_id}/media | Persistir mídia da pessoa|
|[**signCloudinaryUploadApiV1IntakeMediaCloudinarySignPost**](#signcloudinaryuploadapiv1intakemediacloudinarysignpost) | **POST** /api/v1/intake/media/cloudinary/sign | Gerar assinatura Cloudinary|
|[**validateFichaUnicaApiV1IntakeFichaUnicaValidatePost**](#validatefichaunicaapiv1intakefichaunicavalidatepost) | **POST** /api/v1/intake/ficha-unica/validate | Validar Ficha Única (dry-run)|

# **autocompleteOrganizationsApiV1IntakeOrganizationsAutocompleteGet**
> OrganizationAutocompleteResponse autocompleteOrganizationsApiV1IntakeOrganizationsAutocompleteGet()

Retorna organizações filtradas por escopo do usuário.          - Superadmin: vê todas as organizações     - Outros papéis: apenas organizações com membership ativo

### Example

```typescript
import {
    IntakeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let q: string; //Termo de busca (mínimo 2 caracteres) (default to undefined)
let limit: number; //Número máximo de resultados (optional) (default to 10)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.autocompleteOrganizationsApiV1IntakeOrganizationsAutocompleteGet(
    q,
    limit,
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
| **q** | [**string**] | Termo de busca (mínimo 2 caracteres) | defaults to undefined|
| **limit** | [**number**] | Número máximo de resultados | (optional) defaults to 10|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**OrganizationAutocompleteResponse**

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

# **autocompleteSeasonsApiV1IntakeSeasonsAutocompleteGet**
> { [key: string]: any; } autocompleteSeasonsApiV1IntakeSeasonsAutocompleteGet()

Retorna temporadas disponíveis filtradas por escopo.          FASE 4.1 - Season Management          Parâmetros:     - q: Termo de busca opcional (filtro por ano)     - limit: Número máximo de resultados (default: 10)          Autorização:     - Superadmin: vê todas as temporadas     - Dirigente/Coordenador/Treinador: vê temporadas da organização vinculada

### Example

```typescript
import {
    IntakeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let q: string; //Termo de busca (ano ou nome) (optional) (default to '')
let limit: number; //Número máximo de resultados (optional) (default to 10)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.autocompleteSeasonsApiV1IntakeSeasonsAutocompleteGet(
    q,
    limit,
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
| **q** | [**string**] | Termo de busca (ano ou nome) | (optional) defaults to ''|
| **limit** | [**number**] | Número máximo de resultados | (optional) defaults to 10|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **autocompleteTeamsApiV1IntakeTeamsAutocompleteGet**
> TeamAutocompleteResponse autocompleteTeamsApiV1IntakeTeamsAutocompleteGet()

Retorna equipes da organização filtradas por escopo.          Parâmetros:     - organization_id: ID da organização (obrigatório)     - q: Termo de busca (opcional)

### Example

```typescript
import {
    IntakeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let organizationId: string; //ID da organização (default to undefined)
let q: string; //Termo de busca (opcional) (optional) (default to '')
let limit: number; //Número máximo de resultados (optional) (default to 10)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.autocompleteTeamsApiV1IntakeTeamsAutocompleteGet(
    organizationId,
    q,
    limit,
    teamId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **organizationId** | [**string**] | ID da organização | defaults to undefined|
| **q** | [**string**] | Termo de busca (opcional) | (optional) defaults to ''|
| **limit** | [**number**] | Número máximo de resultados | (optional) defaults to 10|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamAutocompleteResponse**

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

# **createFichaUnicaApiV1IntakeFichaUnicaPost**
> FichaUnicaResponse createFichaUnicaApiV1IntakeFichaUnicaPost(fichaUnicaRequest)

Cadastro unificado de Pessoa com opcionais:          - **Pessoa** (obrigatório): dados pessoais, contatos, documentos, endereço     - **Usuário** (opcional): cria login e envia email de ativação     - **Organização** (opcional): criar nova ou selecionar existente     - **Equipe** (opcional): criar nova ou selecionar existente     - **Atleta** (opcional): dados esportivos     - **Vínculos** (opcional): org_membership, team_registration          ## Features          - **Dry-run**: `?validate_only=true` para validar sem gravar     - **Idempotência**: Header `Idempotency-Key` evita duplicação em retry     - **Transação atômica**: tudo ou nada     - **Rate limiting**: 10 cadastros/minuto por IP     - **Email assíncrono**: Não bloqueia resposta, retry automático          ## Permissões          - Superadmin: acesso total     - Dirigente: todos os tipos de cadastro     - Coordenador: todos exceto criar organização     - Treinador: apenas atletas          ## Validações (R15, RD13, etc)          - CPF/RG únicos     - Email único     - Categoria vs idade (R15)     - Gênero compatível com equipe     - Goleira sem posição ofensiva (RD13)

### Example

```typescript
import {
    IntakeApi,
    Configuration,
    FichaUnicaRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let fichaUnicaRequest: FichaUnicaRequest; //
let validateOnly: boolean; //Se True, apenas valida sem gravar no banco (optional) (default to false)
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let idempotencyKey: string; //Chave única para evitar duplicação em retry (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createFichaUnicaApiV1IntakeFichaUnicaPost(
    fichaUnicaRequest,
    validateOnly,
    organizationId,
    teamId,
    athleteId,
    idempotencyKey,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **fichaUnicaRequest** | **FichaUnicaRequest**|  | |
| **validateOnly** | [**boolean**] | Se True, apenas valida sem gravar no banco | (optional) defaults to false|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **idempotencyKey** | [**string**] | Chave única para evitar duplicação em retry | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**FichaUnicaResponse**

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

# **dryRunFichaUnicaApiV1IntakeFichaUnicaDryRunPost**
> FichaUnicaDryRunResponse dryRunFichaUnicaApiV1IntakeFichaUnicaDryRunPost(fichaUnicaRequest)

Valida e retorna preview do que seria criado.          Inclui:     - Resultado da validação     - Preview das entidades que seriam criadas     - Warnings sobre regras de negócio

### Example

```typescript
import {
    IntakeApi,
    Configuration,
    FichaUnicaRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let fichaUnicaRequest: FichaUnicaRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.dryRunFichaUnicaApiV1IntakeFichaUnicaDryRunPost(
    fichaUnicaRequest,
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
| **fichaUnicaRequest** | **FichaUnicaRequest**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**FichaUnicaDryRunResponse**

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

# **savePersonMediaApiV1IntakePersonsPersonIdMediaPost**
> any savePersonMediaApiV1IntakePersonsPersonIdMediaPost()

Salva referência da foto após upload no Cloudinary

### Example

```typescript
import {
    IntakeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let personId: string; // (default to undefined)
let publicId: string; //Public ID retornado pelo Cloudinary (default to undefined)
let roles: Array<string>; // (optional) (default to undefined)
let requireOrg: boolean; // (optional) (default to false)
let requireTeam: boolean; // (optional) (default to false)
let requireTeamRegistration: boolean; // (optional) (default to false)

const { status, data } = await apiInstance.savePersonMediaApiV1IntakePersonsPersonIdMediaPost(
    personId,
    publicId,
    roles,
    requireOrg,
    requireTeam,
    requireTeamRegistration
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **publicId** | [**string**] | Public ID retornado pelo Cloudinary | defaults to undefined|
| **roles** | **Array&lt;string&gt;** |  | (optional) defaults to undefined|
| **requireOrg** | [**boolean**] |  | (optional) defaults to false|
| **requireTeam** | [**boolean**] |  | (optional) defaults to false|
| **requireTeamRegistration** | [**boolean**] |  | (optional) defaults to false|


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
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **signCloudinaryUploadApiV1IntakeMediaCloudinarySignPost**
> any signCloudinaryUploadApiV1IntakeMediaCloudinarySignPost()

Gera assinatura para upload direto ao Cloudinary (signed upload)

### Example

```typescript
import {
    IntakeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let personId: string; // (default to undefined)
let roles: Array<string>; // (optional) (default to undefined)
let requireOrg: boolean; // (optional) (default to false)
let requireTeam: boolean; // (optional) (default to false)
let requireTeamRegistration: boolean; // (optional) (default to false)

const { status, data } = await apiInstance.signCloudinaryUploadApiV1IntakeMediaCloudinarySignPost(
    personId,
    roles,
    requireOrg,
    requireTeam,
    requireTeamRegistration
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **personId** | [**string**] |  | defaults to undefined|
| **roles** | **Array&lt;string&gt;** |  | (optional) defaults to undefined|
| **requireOrg** | [**boolean**] |  | (optional) defaults to false|
| **requireTeam** | [**boolean**] |  | (optional) defaults to false|
| **requireTeamRegistration** | [**boolean**] |  | (optional) defaults to false|


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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validateFichaUnicaApiV1IntakeFichaUnicaValidatePost**
> ValidationResult validateFichaUnicaApiV1IntakeFichaUnicaValidatePost(fichaUnicaRequest)

Valida o payload da Ficha Única sem gravar no banco.          Útil para validação em tempo real no frontend (UX).          Retorna:     - Erros de unicidade (CPF, RG, email)     - Erros de regras de negócio (R15, RD13)     - Warnings (avisos não bloqueantes)

### Example

```typescript
import {
    IntakeApi,
    Configuration,
    FichaUnicaRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new IntakeApi(configuration);

let fichaUnicaRequest: FichaUnicaRequest; //
let organizationId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.validateFichaUnicaApiV1IntakeFichaUnicaValidatePost(
    fichaUnicaRequest,
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
| **fichaUnicaRequest** | **FichaUnicaRequest**|  | |
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ValidationResult**

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

