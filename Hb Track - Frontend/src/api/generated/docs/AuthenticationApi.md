# AuthenticationApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**changePasswordApiV1AuthChangePasswordPost**](#changepasswordapiv1authchangepasswordpost) | **POST** /api/v1/auth/change-password | Alterar senha|
|[**forgotPasswordApiV1AuthForgotPasswordPost**](#forgotpasswordapiv1authforgotpasswordpost) | **POST** /api/v1/auth/forgot-password | Solicitar recuperação de senha|
|[**getContextApiV1AuthContextGet**](#getcontextapiv1authcontextget) | **GET** /api/v1/auth/context | Contexto completo de acesso|
|[**getMeApiV1AuthMeGet**](#getmeapiv1authmeget) | **GET** /api/v1/auth/me | Dados do usuário autenticado|
|[**getPermissionsApiV1AuthPermissionsGet**](#getpermissionsapiv1authpermissionsget) | **GET** /api/v1/auth/permissions | Permissões do usuário autenticado|
|[**getRolesApiV1AuthRolesGet**](#getrolesapiv1authrolesget) | **GET** /api/v1/auth/roles | Ver papéis|
|[**initialSetupApiV1AuthInitialSetupPost**](#initialsetupapiv1authinitialsetuppost) | **POST** /api/v1/auth/initial-setup | Setup inicial para dirigente|
|[**loginApiV1AuthLoginPost**](#loginapiv1authloginpost) | **POST** /api/v1/auth/login | Login com email e senha|
|[**logoutApiV1AuthLogoutPost**](#logoutapiv1authlogoutpost) | **POST** /api/v1/auth/logout | Logout - Revoga Refresh Token|
|[**refreshTokenApiV1AuthRefreshPost**](#refreshtokenapiv1authrefreshpost) | **POST** /api/v1/auth/refresh | Renovar access token|
|[**resendVerificationApiV1AuthResendVerificationPost**](#resendverificationapiv1authresendverificationpost) | **POST** /api/v1/auth/resend-verification | Reenviar verificação|
|[**resetPasswordApiV1AuthResetPasswordPost**](#resetpasswordapiv1authresetpasswordpost) | **POST** /api/v1/auth/reset-password | Resetar senha com token|
|[**setPasswordWithTokenApiV1AuthSetPasswordPost**](#setpasswordwithtokenapiv1authsetpasswordpost) | **POST** /api/v1/auth/set-password | Definir senha com token|
|[**verifyEmailApiV1AuthVerifyEmailPost**](#verifyemailapiv1authverifyemailpost) | **POST** /api/v1/auth/verify-email | Verificar email|
|[**welcomeCompleteApiV1AuthWelcomeCompletePost**](#welcomecompleteapiv1authwelcomecompletepost) | **POST** /api/v1/auth/welcome/complete | Completar cadastro de welcome|
|[**welcomeVerifyApiV1AuthWelcomeVerifyGet**](#welcomeverifyapiv1authwelcomeverifyget) | **GET** /api/v1/auth/welcome/verify | Verificar token de welcome|

# **changePasswordApiV1AuthChangePasswordPost**
> changePasswordApiV1AuthChangePasswordPost(changePasswordRequest)

Altera a senha do usuário autenticado.

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    ChangePasswordRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let changePasswordRequest: ChangePasswordRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.changePasswordApiV1AuthChangePasswordPost(
    changePasswordRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **changePasswordRequest** | **ChangePasswordRequest**|  | |
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
|**401** | Senha atual incorreta |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **forgotPasswordApiV1AuthForgotPasswordPost**
> ForgotPasswordResponse forgotPasswordApiV1AuthForgotPasswordPost(forgotPasswordRequest)

Solicita recuperação de senha. Envia email com link de reset.  **Fluxo:** 1. Usuário insere email 2. Sistema envia email com link de reset 3. Email contém link para /new-password?token=xxx 4. Link expira em 24 horas  **Segurança:** - Rate limit: 5 requisições por hora por email - Token seguro e único - Tokens anteriores são invalidados

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    ForgotPasswordRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let forgotPasswordRequest: ForgotPasswordRequest; //

const { status, data } = await apiInstance.forgotPasswordApiV1AuthForgotPasswordPost(
    forgotPasswordRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **forgotPasswordRequest** | **ForgotPasswordRequest**|  | |


### Return type

**ForgotPasswordResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Email enviado com sucesso |  -  |
|**400** | Email não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getContextApiV1AuthContextGet**
> AuthContextResponse getContextApiV1AuthContextGet()

Retorna papel, vínculos e permissões. CONTRATO FIXO. Apenas espelho do ExecutionContext.

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getContextApiV1AuthContextGet(
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

**AuthContextResponse**

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

# **getMeApiV1AuthMeGet**
> UserMeResponse getMeApiV1AuthMeGet()

Retorna informações do usuário autenticado a partir do JWT.

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMeApiV1AuthMeGet(
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

**UserMeResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPermissionsApiV1AuthPermissionsGet**
> Array<string | null> getPermissionsApiV1AuthPermissionsGet()

Retorna lista de permissões baseadas no papel do usuário.

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getPermissionsApiV1AuthPermissionsGet(
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

**Array<string | null>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getRolesApiV1AuthRolesGet**
> any getRolesApiV1AuthRolesGet()

Espelho de roles para o contrato (Phase 2).

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.getRolesApiV1AuthRolesGet();
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

# **initialSetupApiV1AuthInitialSetupPost**
> InitialSetupResponse initialSetupApiV1AuthInitialSetupPost(initialSetupRequest)

Cria organização e temporada inicial para dirigente na primeira vez.  **Requisitos:** - Usuário deve ser dirigente - Não deve ter organização cadastrada  **O que é criado:** - Organização - Vínculo do dirigente com a organização - Temporada inicial (ativa)

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    InitialSetupRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let initialSetupRequest: InitialSetupRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.initialSetupApiV1AuthInitialSetupPost(
    initialSetupRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **initialSetupRequest** | **InitialSetupRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**InitialSetupResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Usuário não é dirigente ou já tem organização |  -  |
|**422** | Dados inválidos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **loginApiV1AuthLoginPost**
> LoginResponse loginApiV1AuthLoginPost()

Autentica usuário e retorna JWT access token.  **Regras aplicáveis:** - R2: Usuário com email único - R42: Vínculo ativo obrigatório (exceto superadmin) - R3: Superadmin pode operar sem vínculo  **Rate Limit:** 5 tentativas por minuto por IP

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let username: string; // (default to undefined)
let password: string; // (default to undefined)
let grantType: string; // (optional) (default to undefined)
let scope: string; // (optional) (default to '')
let clientId: string; // (optional) (default to undefined)
let clientSecret: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.loginApiV1AuthLoginPost(
    username,
    password,
    grantType,
    scope,
    clientId,
    clientSecret
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **username** | [**string**] |  | defaults to undefined|
| **password** | [**string**] |  | defaults to undefined|
| **grantType** | [**string**] |  | (optional) defaults to undefined|
| **scope** | [**string**] |  | (optional) defaults to ''|
| **clientId** | [**string**] |  | (optional) defaults to undefined|
| **clientSecret** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LoginResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Email ou senha inválidos |  -  |
|**403** | Usuário sem vínculo ativo (R42) |  -  |
|**429** | Rate limit excedido - muitas tentativas |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **logoutApiV1AuthLogoutPost**
> logoutApiV1AuthLogoutPost()

Endpoint de logout que remove o cookie HttpOnly e revoga o Refresh Token no banco de dados.

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    RefreshTokenRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)
let refreshTokenRequest: RefreshTokenRequest; // (optional)

const { status, data } = await apiInstance.logoutApiV1AuthLogoutPost(
    xRequestID,
    xOrganizationId,
    refreshTokenRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **refreshTokenRequest** | **RefreshTokenRequest**|  | |
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

# **refreshTokenApiV1AuthRefreshPost**
> RefreshTokenResponse refreshTokenApiV1AuthRefreshPost(refreshTokenRequest)

Renova o access token usando um refresh token válido.  **Fase 2: Persistência e Rotação** 1. Valida JWT assinado 2. Valida hash no banco de dados 3. Detecta reuso (se token revogado for usado, mata todas as sessões do usuário) 4. Gera novos tokens e revoga o anterior

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    RefreshTokenRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let refreshTokenRequest: RefreshTokenRequest; //

const { status, data } = await apiInstance.refreshTokenApiV1AuthRefreshPost(
    refreshTokenRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **refreshTokenRequest** | **RefreshTokenRequest**|  | |


### Return type

**RefreshTokenResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Refresh token inválido, expirado ou revogado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resendVerificationApiV1AuthResendVerificationPost**
> any resendVerificationApiV1AuthResendVerificationPost()

Stub para contrato (Phase 2).

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.resendVerificationApiV1AuthResendVerificationPost();
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

# **resetPasswordApiV1AuthResetPasswordPost**
> ResetPasswordResponse resetPasswordApiV1AuthResetPasswordPost(appApiV1RoutersAuthResetPasswordRequest)

Reseta a senha usando um token válido.  **Validações:** - Token deve ser válido e não expirado - Senhas devem coincidir - Nova senha deve ter mínimo 8 caracteres - Token pode ser usado apenas uma vez

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    AppApiV1RoutersAuthResetPasswordRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let appApiV1RoutersAuthResetPasswordRequest: AppApiV1RoutersAuthResetPasswordRequest; //

const { status, data } = await apiInstance.resetPasswordApiV1AuthResetPasswordPost(
    appApiV1RoutersAuthResetPasswordRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **appApiV1RoutersAuthResetPasswordRequest** | **AppApiV1RoutersAuthResetPasswordRequest**|  | |


### Return type

**ResetPasswordResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Senha alterada com sucesso |  -  |
|**400** | Token inválido, expirado ou senhas não coincidem |  -  |
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **setPasswordWithTokenApiV1AuthSetPasswordPost**
> SetPasswordResponse setPasswordWithTokenApiV1AuthSetPasswordPost(setPasswordRequest)

Valida token de ativação e define senha (primeira vez).          SEGURANÇA:     - Token single-use (marcado como `used`)     - Expira em 24h     - Validado via hash SHA-256          Usado quando usuário recebe email de convite.

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    SetPasswordRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let setPasswordRequest: SetPasswordRequest; //

const { status, data } = await apiInstance.setPasswordWithTokenApiV1AuthSetPasswordPost(
    setPasswordRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **setPasswordRequest** | **SetPasswordRequest**|  | |


### Return type

**SetPasswordResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Token inválido ou expirado |  -  |
|**404** | Usuário não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verifyEmailApiV1AuthVerifyEmailPost**
> any verifyEmailApiV1AuthVerifyEmailPost()

Stub para contrato (Phase 2).

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.verifyEmailApiV1AuthVerifyEmailPost();
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

# **welcomeCompleteApiV1AuthWelcomeCompletePost**
> WelcomeCompleteResponse welcomeCompleteApiV1AuthWelcomeCompletePost(welcomeCompleteRequest)

Completa o cadastro do usuário convidado:     1. Valida token de welcome     2. Define senha do usuário     3. Atualiza dados da pessoa (nome, telefone, etc.)     4. Ativa o TeamMembership (status → \'ativo\')     5. Marca token como usado     6. Retorna sessão/login automático          SEGURANÇA:     - Token single-use     - Senha validada (mínimo 8 caracteres)

### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    WelcomeCompleteRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let welcomeCompleteRequest: WelcomeCompleteRequest; //

const { status, data } = await apiInstance.welcomeCompleteApiV1AuthWelcomeCompletePost(
    welcomeCompleteRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **welcomeCompleteRequest** | **WelcomeCompleteRequest**|  | |


### Return type

**WelcomeCompleteResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Token inválido ou senhas não conferem |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **welcomeVerifyApiV1AuthWelcomeVerifyGet**
> WelcomeVerifyResponse welcomeVerifyApiV1AuthWelcomeVerifyGet()

Verifica se o token de welcome é válido e retorna informações do convite.          SEGURANÇA:     - Token deve ser do tipo \'welcome\'     - Token não pode estar usado     - Token não pode estar expirado (48h)          Retorna dados do convidado para pré-popular o formulário.

### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let token: string; // (default to undefined)

const { status, data } = await apiInstance.welcomeVerifyApiV1AuthWelcomeVerifyGet(
    token
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **token** | [**string**] |  | defaults to undefined|


### Return type

**WelcomeVerifyResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Token inválido, expirado ou já utilizado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

