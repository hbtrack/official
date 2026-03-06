# AttendanceApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost**](#addattendancebatchapiv1trainingsessionstrainingsessionidattendancebatchpost) | **POST** /api/v1/training_sessions/{training_session_id}/attendance/batch | Registra presenças em batch|
|[**addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost_0**](#addattendancebatchapiv1trainingsessionstrainingsessionidattendancebatchpost_0) | **POST** /api/v1/training_sessions/{training_session_id}/attendance/batch | Registra presenças em batch|
|[**addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost**](#addattendancetosessionapiv1trainingsessionstrainingsessionidattendancepost) | **POST** /api/v1/training_sessions/{training_session_id}/attendance | Registra presença individual|
|[**addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost_0**](#addattendancetosessionapiv1trainingsessionstrainingsessionidattendancepost_0) | **POST** /api/v1/training_sessions/{training_session_id}/attendance | Registra presença individual|
|[**closeSessionApiV1AttendanceSessionsSessionIdClosePost**](#closesessionapiv1attendancesessionssessionidclosepost) | **POST** /api/v1/attendance/sessions/{session_id}/close | Treinador fecha sessão e consolida presenças (DEC-INV-065)|
|[**closeSessionApiV1AttendanceSessionsSessionIdClosePost_0**](#closesessionapiv1attendancesessionssessionidclosepost_0) | **POST** /api/v1/attendance/sessions/{session_id}/close | Treinador fecha sessão e consolida presenças (DEC-INV-065)|
|[**correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost**](#correctattendanceadministrativeapiv1attendanceattendanceidcorrectpost) | **POST** /api/v1/attendance/{attendance_id}/correct | Corrige presença administrativamente (RBAC)|
|[**correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost_0**](#correctattendanceadministrativeapiv1attendanceattendanceidcorrectpost_0) | **POST** /api/v1/attendance/{attendance_id}/correct | Corrige presença administrativamente (RBAC)|
|[**getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet**](#getsessionattendancestatisticsapiv1trainingsessionstrainingsessionidattendancestatisticsget) | **GET** /api/v1/training_sessions/{training_session_id}/attendance/statistics | Estatísticas de presença da sessão|
|[**getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet_0**](#getsessionattendancestatisticsapiv1trainingsessionstrainingsessionidattendancestatisticsget_0) | **GET** /api/v1/training_sessions/{training_session_id}/attendance/statistics | Estatísticas de presença da sessão|
|[**listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet**](#listattendancebysessionapiv1trainingsessionstrainingsessionidattendanceget) | **GET** /api/v1/training_sessions/{training_session_id}/attendance | Lista presenças da sessão|
|[**listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet_0**](#listattendancebysessionapiv1trainingsessionstrainingsessionidattendanceget_0) | **GET** /api/v1/training_sessions/{training_session_id}/attendance | Lista presenças da sessão|
|[**listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet**](#listsessionpendingitemsapiv1attendancesessionssessionidpendingitemsget) | **GET** /api/v1/attendance/sessions/{session_id}/pending-items | Lista pending items da sessão (INV-TRAIN-066)|
|[**listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet_0**](#listsessionpendingitemsapiv1attendancesessionssessionidpendingitemsget_0) | **GET** /api/v1/attendance/sessions/{session_id}/pending-items | Lista pending items da sessão (INV-TRAIN-066)|
|[**preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost**](#preconfirmattendanceapiv1attendancesessionssessionidpreconfirmpost) | **POST** /api/v1/attendance/sessions/{session_id}/preconfirm | Atleta registra pré-confirmação de presença (INV-TRAIN-063)|
|[**preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost_0**](#preconfirmattendanceapiv1attendancesessionssessionidpreconfirmpost_0) | **POST** /api/v1/attendance/sessions/{session_id}/preconfirm | Atleta registra pré-confirmação de presença (INV-TRAIN-063)|
|[**resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch**](#resolvependingitemapiv1attendancependingitemsitemidresolvepatch) | **PATCH** /api/v1/attendance/pending-items/{item_id}/resolve | Treinador resolve pending item de divergência (INV-TRAIN-067)|
|[**resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch_0**](#resolvependingitemapiv1attendancependingitemsitemidresolvepatch_0) | **PATCH** /api/v1/attendance/pending-items/{item_id}/resolve | Treinador resolve pending item de divergência (INV-TRAIN-067)|
|[**updateAttendanceApiV1AttendanceAttendanceIdPatch**](#updateattendanceapiv1attendanceattendanceidpatch) | **PATCH** /api/v1/attendance/{attendance_id} | Atualiza registro de presença|
|[**updateAttendanceApiV1AttendanceAttendanceIdPatch_0**](#updateattendanceapiv1attendanceattendanceidpatch_0) | **PATCH** /api/v1/attendance/{attendance_id} | Atualiza registro de presença|

# **addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost**
> Array<Attendance> addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost(attendanceCreate)

Cria múltiplos registros de presença em batch (operação otimizada). Apenas 1 presença por atleta por sessão (UNIQUE session_id + athlete_id).  **Regras**: - R22: Métricas operacionais. - RF5.2: Temporada interrompida bloqueia criação. - R25/R26: Permissões por papel e escopo.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada. - 409 conflict_unique: Presença já registrada para este atleta nesta sessão. - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido ou FK inválida.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let attendanceCreate: Array<AttendanceCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost(
    trainingSessionId,
    attendanceCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceCreate** | **Array<AttendanceCreate>**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<Attendance>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Presenças registradas com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**409** | Conflito (duplicidade ou temporada bloqueada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost_0**
> Array<Attendance> addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost_0(attendanceCreate)

Cria múltiplos registros de presença em batch (operação otimizada). Apenas 1 presença por atleta por sessão (UNIQUE session_id + athlete_id).  **Regras**: - R22: Métricas operacionais. - RF5.2: Temporada interrompida bloqueia criação. - R25/R26: Permissões por papel e escopo.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada. - 409 conflict_unique: Presença já registrada para este atleta nesta sessão. - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido ou FK inválida.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let attendanceCreate: Array<AttendanceCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addAttendanceBatchApiV1TrainingSessionsTrainingSessionIdAttendanceBatchPost_0(
    trainingSessionId,
    attendanceCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceCreate** | **Array<AttendanceCreate>**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<Attendance>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Presenças registradas com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**409** | Conflito (duplicidade ou temporada bloqueada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost**
> Attendance addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost(attendanceCreate)

Cria registro de presença individual para um atleta em uma sessão de treino.  **Nota**: Para múltiplos atletas, use o endpoint /batch para melhor performance.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    AttendanceCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let attendanceCreate: AttendanceCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost(
    trainingSessionId,
    attendanceCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceCreate** | **AttendanceCreate**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Attendance**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Presença registrada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**409** | Conflito (duplicidade ou temporada bloqueada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost_0**
> Attendance addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost_0(attendanceCreate)

Cria registro de presença individual para um atleta em uma sessão de treino.  **Nota**: Para múltiplos atletas, use o endpoint /batch para melhor performance.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    AttendanceCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let attendanceCreate: AttendanceCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addAttendanceToSessionApiV1TrainingSessionsTrainingSessionIdAttendancePost_0(
    trainingSessionId,
    attendanceCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceCreate** | **AttendanceCreate**|  | |
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Attendance**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Presença registrada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**409** | Conflito (duplicidade ou temporada bloqueada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **closeSessionApiV1AttendanceSessionsSessionIdClosePost**
> any closeSessionApiV1AttendanceSessionsSessionIdClosePost()

Consolida presenças ao fechar sessão.  DEC-INV-065: encerramento NUNCA é bloqueado por pending items. Converte registros preconfirm→absent (treinador define presença oficial). Permissão: treinador/admin.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.closeSessionApiV1AttendanceSessionsSessionIdClosePost(
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

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão fechada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas treinador/admin) |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **closeSessionApiV1AttendanceSessionsSessionIdClosePost_0**
> any closeSessionApiV1AttendanceSessionsSessionIdClosePost_0()

Consolida presenças ao fechar sessão.  DEC-INV-065: encerramento NUNCA é bloqueado por pending items. Converte registros preconfirm→absent (treinador define presença oficial). Permissão: treinador/admin.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.closeSessionApiV1AttendanceSessionsSessionIdClosePost_0(
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

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Sessão fechada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas treinador/admin) |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost**
> Attendance correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost(attendanceCorrection)

Aplica correção administrativa a um registro de presença.  **Regras RBAC (Step 11 - Refatoração Training):** - Apenas Coordenadores e Administradores podem corrigir - Requer permissão `attendance:correction_write` - Permitido apenas em sessões fechadas (R37: ação administrativa auditada)  **Auditoria automática:** - source = \'correction\' - correction_by_user_id = ID do usuário que corrigiu - correction_at = timestamp da correção - comment = motivo da correção (obrigatório, mín 10 caracteres)  **Diferença vs PATCH /attendance/{id}:** - PATCH: edição normal dentro da janela temporal (R40) - POST /correct: correção administrativa após fechamento (R37)  **Erros mapeados**: - 403 permission_denied: Sem permissão (apenas Coordenador/Admin). - 404 not_found: Presença não encontrada. - 422 validation_error: Sessão não fechada ou comment < 10 caracteres.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    AttendanceCorrection
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let attendanceId: string; // (default to undefined)
let attendanceCorrection: AttendanceCorrection; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost(
    attendanceId,
    attendanceCorrection,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceCorrection** | **AttendanceCorrection**|  | |
| **attendanceId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Attendance**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Presença corrigida com auditoria |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas Coordenador/Admin) |  -  |
|**404** | Presença não encontrada |  -  |
|**422** | Validação: sessão não fechada ou comment inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost_0**
> Attendance correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost_0(attendanceCorrection)

Aplica correção administrativa a um registro de presença.  **Regras RBAC (Step 11 - Refatoração Training):** - Apenas Coordenadores e Administradores podem corrigir - Requer permissão `attendance:correction_write` - Permitido apenas em sessões fechadas (R37: ação administrativa auditada)  **Auditoria automática:** - source = \'correction\' - correction_by_user_id = ID do usuário que corrigiu - correction_at = timestamp da correção - comment = motivo da correção (obrigatório, mín 10 caracteres)  **Diferença vs PATCH /attendance/{id}:** - PATCH: edição normal dentro da janela temporal (R40) - POST /correct: correção administrativa após fechamento (R37)  **Erros mapeados**: - 403 permission_denied: Sem permissão (apenas Coordenador/Admin). - 404 not_found: Presença não encontrada. - 422 validation_error: Sessão não fechada ou comment < 10 caracteres.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    AttendanceCorrection
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let attendanceId: string; // (default to undefined)
let attendanceCorrection: AttendanceCorrection; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.correctAttendanceAdministrativeApiV1AttendanceAttendanceIdCorrectPost_0(
    attendanceId,
    attendanceCorrection,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceCorrection** | **AttendanceCorrection**|  | |
| **attendanceId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Attendance**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Presença corrigida com auditoria |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas Coordenador/Admin) |  -  |
|**404** | Presença não encontrada |  -  |
|**422** | Validação: sessão não fechada ou comment inválido |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet**
> { [key: string]: any; } getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet()

Retorna estatísticas agregadas de presença de uma sessão.  Retorna:     - total_athletes: Total de atletas registrados     - present_count: Quantidade de presentes     - absent_count: Quantidade de ausentes     - attendance_rate: Taxa de presença (0-100%)

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
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
|**200** | Estatísticas agregadas |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet_0**
> { [key: string]: any; } getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet_0()

Retorna estatísticas agregadas de presença de uma sessão.  Retorna:     - total_athletes: Total de atletas registrados     - present_count: Quantidade de presentes     - absent_count: Quantidade de ausentes     - attendance_rate: Taxa de presença (0-100%)

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSessionAttendanceStatisticsApiV1TrainingSessionsTrainingSessionIdAttendanceStatisticsGet_0(
    trainingSessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
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
|**200** | Estatísticas agregadas |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet**
> Array<Attendance> listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet()

Retorna lista de registros de presença para uma sessão de treino.  **Performance**: Usa eager loading (joinedload) para resolver N+1 queries (<50ms). **LGPD**: Filtra por team_memberships e registra acesso em data_access_logs.  **Regras**: R22 (métricas operacionais), R25/R26 (permissões).  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let athleteId: string; //Filtrar por atleta (optional) (default to undefined)
let status: string; //Filtrar por status (\'present\', \'absent\') (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet(
    trainingSessionId,
    athleteId,
    status,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] | Filtrar por atleta | (optional) defaults to undefined|
| **status** | [**string**] | Filtrar por status (\&#39;present\&#39;, \&#39;absent\&#39;) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<Attendance>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de presenças com eager loading (&lt;50ms) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet_0**
> Array<Attendance> listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet_0()

Retorna lista de registros de presença para uma sessão de treino.  **Performance**: Usa eager loading (joinedload) para resolver N+1 queries (<50ms). **LGPD**: Filtra por team_memberships e registra acesso em data_access_logs.  **Regras**: R22 (métricas operacionais), R25/R26 (permissões).  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Sessão não encontrada.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let trainingSessionId: string; // (default to undefined)
let athleteId: string; //Filtrar por atleta (optional) (default to undefined)
let status: string; //Filtrar por status (\'present\', \'absent\') (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAttendanceBySessionApiV1TrainingSessionsTrainingSessionIdAttendanceGet_0(
    trainingSessionId,
    athleteId,
    status,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **trainingSessionId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] | Filtrar por atleta | (optional) defaults to undefined|
| **status** | [**string**] | Filtrar por status (\&#39;present\&#39;, \&#39;absent\&#39;) | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<Attendance>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de presenças com eager loading (&lt;50ms) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet**
> any listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet()

Lista todos os pending items de divergência da sessão.  INV-TRAIN-066: treinador vê todos; atleta vê apenas os próprios (RBAC no service). Permissão: treinador/admin.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet(
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

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de pending items |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas treinador/admin) |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet_0**
> any listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet_0()

Lista todos os pending items de divergência da sessão.  INV-TRAIN-066: treinador vê todos; atleta vê apenas os próprios (RBAC no service). Permissão: treinador/admin.

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listSessionPendingItemsApiV1AttendanceSessionsSessionIdPendingItemsGet_0(
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

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista de pending items |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas treinador/admin) |  -  |
|**404** | Sessão não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost**
> any preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost()

Registra pré-confirmação de presença pelo atleta autenticado.  INV-TRAIN-063: preconfirm NÃO gera is_official=True. Permitido apenas antes do início da sessão (status in [scheduled, draft]).

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost(
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

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Pré-confirmação registrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas atleta) |  -  |
|**404** | Sessão ou atleta não encontrado |  -  |
|**422** | Sessão já iniciada — pré-confirmação não permitida |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost_0**
> any preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost_0()

Registra pré-confirmação de presença pelo atleta autenticado.  INV-TRAIN-063: preconfirm NÃO gera is_official=True. Permitido apenas antes do início da sessão (status in [scheduled, draft]).

### Example

```typescript
import {
    AttendanceApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let sessionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.preconfirmAttendanceApiV1AttendanceSessionsSessionIdPreconfirmPost_0(
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

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Pré-confirmação registrada |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas atleta) |  -  |
|**404** | Sessão ou atleta não encontrado |  -  |
|**422** | Sessão já iniciada — pré-confirmação não permitida |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch**
> any resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch(resolveItemRequest)

Treinador resolve um pending item de divergência de presença.  INV-TRAIN-067: apenas treinador/coach pode resolver — atleta só submete justificativa. INV-TRAIN-066: status muda para \'resolved\' com resolved_at e resolved_by.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    ResolveItemRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let itemId: string; // (default to undefined)
let resolveItemRequest: ResolveItemRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch(
    itemId,
    resolveItemRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **resolveItemRequest** | **ResolveItemRequest**|  | |
| **itemId** | [**string**] |  | defaults to undefined|
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
|**200** | Pending item resolvido com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas treinador/admin) |  -  |
|**404** | Pending item não encontrado |  -  |
|**409** | Item já resolvido ou sessão em readonly |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch_0**
> any resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch_0(resolveItemRequest)

Treinador resolve um pending item de divergência de presença.  INV-TRAIN-067: apenas treinador/coach pode resolver — atleta só submete justificativa. INV-TRAIN-066: status muda para \'resolved\' com resolved_at e resolved_by.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    ResolveItemRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let itemId: string; // (default to undefined)
let resolveItemRequest: ResolveItemRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.resolvePendingItemApiV1AttendancePendingItemsItemIdResolvePatch_0(
    itemId,
    resolveItemRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **resolveItemRequest** | **ResolveItemRequest**|  | |
| **itemId** | [**string**] |  | defaults to undefined|
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
|**200** | Pending item resolvido com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (apenas treinador/admin) |  -  |
|**404** | Pending item não encontrado |  -  |
|**409** | Item já resolvido ou sessão em readonly |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateAttendanceApiV1AttendanceAttendanceIdPatch**
> Attendance updateAttendanceApiV1AttendanceAttendanceIdPatch(attendanceUpdate)

Atualiza status, minutes_effective, comment ou participation_type de um registro de presença.  **Regras**: - R40: Janela de edição (10min/24h). - RF5.2/R37: Temporada bloqueada. - R25/R26: Permissões por papel e escopo.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Presença não encontrada. - 409 edit_window_expired: Janela de edição expirada (R40). - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    AttendanceUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let attendanceId: string; // (default to undefined)
let attendanceUpdate: AttendanceUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateAttendanceApiV1AttendanceAttendanceIdPatch(
    attendanceId,
    attendanceUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceUpdate** | **AttendanceUpdate**|  | |
| **attendanceId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Attendance**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Presença atualizada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Presença não encontrada |  -  |
|**409** | Conflito de estado (R40: janela expirada, RF5.2: temporada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateAttendanceApiV1AttendanceAttendanceIdPatch_0**
> Attendance updateAttendanceApiV1AttendanceAttendanceIdPatch_0(attendanceUpdate)

Atualiza status, minutes_effective, comment ou participation_type de um registro de presença.  **Regras**: - R40: Janela de edição (10min/24h). - RF5.2/R37: Temporada bloqueada. - R25/R26: Permissões por papel e escopo.  **Erros mapeados**: - 403 permission_denied: Permissão insuficiente. - 404 not_found: Presença não encontrada. - 409 edit_window_expired: Janela de edição expirada (R40). - 409 season_locked: Temporada interrompida/encerrada. - 422 validation_error: Payload inválido.

### Example

```typescript
import {
    AttendanceApi,
    Configuration,
    AttendanceUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new AttendanceApi(configuration);

let attendanceId: string; // (default to undefined)
let attendanceUpdate: AttendanceUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateAttendanceApiV1AttendanceAttendanceIdPatch_0(
    attendanceId,
    attendanceUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **attendanceUpdate** | **AttendanceUpdate**|  | |
| **attendanceId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Attendance**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Presença atualizada com sucesso |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Presença não encontrada |  -  |
|**409** | Conflito de estado (R40: janela expirada, RF5.2: temporada) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

