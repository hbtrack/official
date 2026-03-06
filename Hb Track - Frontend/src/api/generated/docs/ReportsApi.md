# ReportsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet**](#getathleteindividualreportapiv1reportsathletesathleteidget) | **GET** /api/v1/reports/athletes/{athlete_id} | Relatório Individual de Atleta|
|[**getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet_0**](#getathleteindividualreportapiv1reportsathletesathleteidget_0) | **GET** /api/v1/reports/athletes/{athlete_id} | Relatório Individual de Atleta|
|[**getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet**](#getathletemedicalhistoryapiv1reportsathletesathleteidmedicalhistoryget) | **GET** /api/v1/reports/athletes/{athlete_id}/medical-history | Histórico Médico de Atleta|
|[**getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet_0**](#getathletemedicalhistoryapiv1reportsathletesathleteidmedicalhistoryget_0) | **GET** /api/v1/reports/athletes/{athlete_id}/medical-history | Histórico Médico de Atleta|
|[**getAthleteSelfApiV1ReportsAthleteSelfGet**](#getathleteselfapiv1reportsathleteselfget) | **GET** /api/v1/reports/athlete-self | Visão individual do atleta (autoconhecimento)|
|[**getAttendanceReportApiV1ReportsAttendanceGet**](#getattendancereportapiv1reportsattendanceget) | **GET** /api/v1/reports/attendance | Relatório de Assiduidade|
|[**getAttendanceReportApiV1ReportsAttendanceGet_0**](#getattendancereportapiv1reportsattendanceget_0) | **GET** /api/v1/reports/attendance | Relatório de Assiduidade|
|[**getLoadReportApiV1ReportsLoadGet**](#getloadreportapiv1reportsloadget) | **GET** /api/v1/reports/load | Relatório de Carga|
|[**getLoadReportApiV1ReportsLoadGet_0**](#getloadreportapiv1reportsloadget_0) | **GET** /api/v1/reports/load | Relatório de Carga|
|[**getMedicalSummaryReportApiV1ReportsMedicalSummaryGet**](#getmedicalsummaryreportapiv1reportsmedicalsummaryget) | **GET** /api/v1/reports/medical-summary | Relatório de Gerenciamento de Lesões|
|[**getMedicalSummaryReportApiV1ReportsMedicalSummaryGet_0**](#getmedicalsummaryreportapiv1reportsmedicalsummaryget_0) | **GET** /api/v1/reports/medical-summary | Relatório de Gerenciamento de Lesões|
|[**getMinutesReportApiV1ReportsMinutesGet**](#getminutesreportapiv1reportsminutesget) | **GET** /api/v1/reports/minutes | Relatório de Minutos Jogados|
|[**getMinutesReportApiV1ReportsMinutesGet_0**](#getminutesreportapiv1reportsminutesget_0) | **GET** /api/v1/reports/minutes | Relatório de Minutos Jogados|
|[**getOperationalSessionApiV1ReportsOperationalSessionGet**](#getoperationalsessionapiv1reportsoperationalsessionget) | **GET** /api/v1/reports/operational-session | Snapshot operacional da sessão (treino/jogo)|
|[**getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet**](#getteamtraininggamecorrelationapiv1reportsteamtraininggamecorrelationget) | **GET** /api/v1/reports/team-training-game-correlation | Correlação Treino → Jogo por Equipe|
|[**getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet_0**](#getteamtraininggamecorrelationapiv1reportsteamtraininggamecorrelationget_0) | **GET** /api/v1/reports/team-training-game-correlation | Correlação Treino → Jogo por Equipe|
|[**getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet**](#gettrainingperformancereportapiv1reportstrainingperformanceget) | **GET** /api/v1/reports/training-performance | Relatório de Performance em Treinos|
|[**getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet_0**](#gettrainingperformancereportapiv1reportstrainingperformanceget_0) | **GET** /api/v1/reports/training-performance | Relatório de Performance em Treinos|
|[**getTrainingTrendsApiV1ReportsTrainingTrendsGet**](#gettrainingtrendsapiv1reportstrainingtrendsget) | **GET** /api/v1/reports/training-trends | Tendências de Performance em Treinos|
|[**getTrainingTrendsApiV1ReportsTrainingTrendsGet_0**](#gettrainingtrendsapiv1reportstrainingtrendsget_0) | **GET** /api/v1/reports/training-trends | Tendências de Performance em Treinos|
|[**getViewsStatsApiV1ReportsStatsGet**](#getviewsstatsapiv1reportsstatsget) | **GET** /api/v1/reports/stats | Estatísticas das Materialized Views|
|[**getViewsStatsApiV1ReportsStatsGet_0**](#getviewsstatsapiv1reportsstatsget_0) | **GET** /api/v1/reports/stats | Estatísticas das Materialized Views|
|[**getWellnessSummaryReportApiV1ReportsWellnessSummaryGet**](#getwellnesssummaryreportapiv1reportswellnesssummaryget) | **GET** /api/v1/reports/wellness-summary | Relatório de Prontidão e Bem-Estar|
|[**getWellnessSummaryReportApiV1ReportsWellnessSummaryGet_0**](#getwellnesssummaryreportapiv1reportswellnesssummaryget_0) | **GET** /api/v1/reports/wellness-summary | Relatório de Prontidão e Bem-Estar|
|[**getWellnessTrendsApiV1ReportsWellnessTrendsGet**](#getwellnesstrendsapiv1reportswellnesstrendsget) | **GET** /api/v1/reports/wellness-trends | Tendências de Bem-Estar|
|[**getWellnessTrendsApiV1ReportsWellnessTrendsGet_0**](#getwellnesstrendsapiv1reportswellnesstrendsget_0) | **GET** /api/v1/reports/wellness-trends | Tendências de Bem-Estar|
|[**listAthleteReportsApiV1ReportsAthletesGet**](#listathletereportsapiv1reportsathletesget) | **GET** /api/v1/reports/athletes | Lista Relatórios de Atletas|
|[**listAthleteReportsApiV1ReportsAthletesGet_0**](#listathletereportsapiv1reportsathletesget_0) | **GET** /api/v1/reports/athletes | Lista Relatórios de Atletas|
|[**refreshAllViewsApiV1ReportsRefreshAllPost**](#refreshallviewsapiv1reportsrefreshallpost) | **POST** /api/v1/reports/refresh-all | Refresh de Todas as Materialized Views|
|[**refreshAllViewsApiV1ReportsRefreshAllPost_0**](#refreshallviewsapiv1reportsrefreshallpost_0) | **POST** /api/v1/reports/refresh-all | Refresh de Todas as Materialized Views|
|[**refreshSpecificViewApiV1ReportsRefreshViewNamePost**](#refreshspecificviewapiv1reportsrefreshviewnamepost) | **POST** /api/v1/reports/refresh/{view_name} | Refresh Materialized View Específica|
|[**refreshSpecificViewApiV1ReportsRefreshViewNamePost_0**](#refreshspecificviewapiv1reportsrefreshviewnamepost_0) | **POST** /api/v1/reports/refresh/{view_name} | Refresh Materialized View Específica|
|[**refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost**](#refreshtrainingperformanceapiv1reportsrefreshtrainingperformancepost) | **POST** /api/v1/reports/refresh-training-performance | Atualizar Materialized View de Treinos|
|[**refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost_0**](#refreshtrainingperformanceapiv1reportsrefreshtrainingperformancepost_0) | **POST** /api/v1/reports/refresh-training-performance | Atualizar Materialized View de Treinos|

# **getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet**
> AthleteIndividualReport getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet()

Retorna relatório completo de uma atleta (treinos, wellness, carga).      **Referências RAG:**     - R12: Atleta permanente no histórico     - R13/R14: Estados e impactos     - RP4: Escopo de participação     - RP5: Ausência = carga 0     - RP6: Participação = métricas obrigatórias      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas atletas (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let athleteId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet(
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

**AthleteIndividualReport**

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

# **getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet_0**
> AthleteIndividualReport getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet_0()

Retorna relatório completo de uma atleta (treinos, wellness, carga).      **Referências RAG:**     - R12: Atleta permanente no histórico     - R13/R14: Estados e impactos     - RP4: Escopo de participação     - RP5: Ausência = carga 0     - RP6: Participação = métricas obrigatórias      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas atletas (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let athleteId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteIndividualReportApiV1ReportsAthletesAthleteIdGet_0(
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

**AthleteIndividualReport**

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

# **getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet**
> Array<{ [key: string]: any; }> getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet()

Retorna histórico completo de casos médicos de uma atleta.      **Referências RAG:**     - R13: Estados de atleta     - RP7: Rastreamento médico      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas atletas (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let athleteId: string; // (default to undefined)
let limit: number; //Limite de registros (optional) (default to 10)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet(
    athleteId,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] | Limite de registros | (optional) defaults to 10|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<{ [key: string]: any; }>**

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

# **getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet_0**
> Array<{ [key: string]: any; }> getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet_0()

Retorna histórico completo de casos médicos de uma atleta.      **Referências RAG:**     - R13: Estados de atleta     - RP7: Rastreamento médico      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas atletas (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let athleteId: string; // (default to undefined)
let limit: number; //Limite de registros (optional) (default to 10)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteMedicalHistoryApiV1ReportsAthletesAthleteIdMedicalHistoryGet_0(
    athleteId,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **athleteId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] | Limite de registros | (optional) defaults to 10|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<{ [key: string]: any; }>**

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

# **getAthleteSelfApiV1ReportsAthleteSelfGet**
> any getAthleteSelfApiV1ReportsAthleteSelfGet()

Retorna presença, wellness, carga, status e insights do próprio atleta.

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteSelfApiV1ReportsAthleteSelfGet(
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

# **getAttendanceReportApiV1ReportsAttendanceGet**
> AttendanceReportResponse getAttendanceReportApiV1ReportsAttendanceGet()

Retorna taxa de assiduidade por atleta em treinos e jogos.      **Métricas incluídas:**     - Total de treinos e jogos     - Presenças em treinos e jogos     - Taxa de presença (%) individual     - Médias da equipe      **Referências RAG:**     - R17: Treinos como eventos operacionais     - R19: Estatísticas vinculadas a jogo + equipe     - R21: Métricas de treino (assiduidade)     - RP5: Ausência = carga 0     - RP6: Participação = métricas obrigatórias      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (obrigatório) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Página (1-indexed) (optional) (default to 1)
let pageSize: number; //Itens por página (optional) (default to 25)
let orderBy: string; //Campo de ordenação: athlete_name, training_attendance_rate, match_participation_rate, combined_attendance_rate (optional) (default to undefined)
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAttendanceReportApiV1ReportsAttendanceGet(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    pageSize,
    orderBy,
    orderDir,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe (obrigatório) | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Página (1-indexed) | (optional) defaults to 1|
| **pageSize** | [**number**] | Itens por página | (optional) defaults to 25|
| **orderBy** | [**string**] | Campo de ordenação: athlete_name, training_attendance_rate, match_participation_rate, combined_attendance_rate | (optional) defaults to undefined|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AttendanceReportResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Taxa de assiduidade por atleta |  -  |
|**403** | Equipe fora do escopo do usuário |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAttendanceReportApiV1ReportsAttendanceGet_0**
> AttendanceReportResponse getAttendanceReportApiV1ReportsAttendanceGet_0()

Retorna taxa de assiduidade por atleta em treinos e jogos.      **Métricas incluídas:**     - Total de treinos e jogos     - Presenças em treinos e jogos     - Taxa de presença (%) individual     - Médias da equipe      **Referências RAG:**     - R17: Treinos como eventos operacionais     - R19: Estatísticas vinculadas a jogo + equipe     - R21: Métricas de treino (assiduidade)     - RP5: Ausência = carga 0     - RP6: Participação = métricas obrigatórias      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (obrigatório) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Página (1-indexed) (optional) (default to 1)
let pageSize: number; //Itens por página (optional) (default to 25)
let orderBy: string; //Campo de ordenação: athlete_name, training_attendance_rate, match_participation_rate, combined_attendance_rate (optional) (default to undefined)
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAttendanceReportApiV1ReportsAttendanceGet_0(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    pageSize,
    orderBy,
    orderDir,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe (obrigatório) | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Página (1-indexed) | (optional) defaults to 1|
| **pageSize** | [**number**] | Itens por página | (optional) defaults to 25|
| **orderBy** | [**string**] | Campo de ordenação: athlete_name, training_attendance_rate, match_participation_rate, combined_attendance_rate | (optional) defaults to undefined|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AttendanceReportResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Taxa de assiduidade por atleta |  -  |
|**403** | Equipe fora do escopo do usuário |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getLoadReportApiV1ReportsLoadGet**
> LoadReportResponse getLoadReportApiV1ReportsLoadGet()

Retorna carga acumulada por atleta (treinos + jogos).      **Cálculo de carga:**     - Treino: RPE × minutes_effective (wellness_post.session_rpe)     - Jogo: minutes_played (carga estimada)     - RPE padrão: 5 quando não informado      **Métricas incluídas:**     - Carga total de treinos     - Carga total de jogos     - Número de sessões/jogos     - Média por sessão/jogo      **Referências RAG:**     - R21: Métricas de treino (carga)     - RP5: Ausência = carga 0     - RP8: Monitoramento de sobrecarga      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (obrigatório) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Página (1-indexed) (optional) (default to 1)
let pageSize: number; //Itens por página (optional) (default to 25)
let orderBy: string; //Campo de ordenação: athlete_name, training_load_total, match_load_total, total_load, avg_daily_load (optional) (default to undefined)
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getLoadReportApiV1ReportsLoadGet(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    pageSize,
    orderBy,
    orderDir,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe (obrigatório) | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Página (1-indexed) | (optional) defaults to 1|
| **pageSize** | [**number**] | Itens por página | (optional) defaults to 25|
| **orderBy** | [**string**] | Campo de ordenação: athlete_name, training_load_total, match_load_total, total_load, avg_daily_load | (optional) defaults to undefined|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LoadReportResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Carga acumulada por atleta |  -  |
|**403** | Equipe fora do escopo do usuário |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getLoadReportApiV1ReportsLoadGet_0**
> LoadReportResponse getLoadReportApiV1ReportsLoadGet_0()

Retorna carga acumulada por atleta (treinos + jogos).      **Cálculo de carga:**     - Treino: RPE × minutes_effective (wellness_post.session_rpe)     - Jogo: minutes_played (carga estimada)     - RPE padrão: 5 quando não informado      **Métricas incluídas:**     - Carga total de treinos     - Carga total de jogos     - Número de sessões/jogos     - Média por sessão/jogo      **Referências RAG:**     - R21: Métricas de treino (carga)     - RP5: Ausência = carga 0     - RP8: Monitoramento de sobrecarga      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (obrigatório) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Página (1-indexed) (optional) (default to 1)
let pageSize: number; //Itens por página (optional) (default to 25)
let orderBy: string; //Campo de ordenação: athlete_name, training_load_total, match_load_total, total_load, avg_daily_load (optional) (default to undefined)
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getLoadReportApiV1ReportsLoadGet_0(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    pageSize,
    orderBy,
    orderDir,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe (obrigatório) | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Página (1-indexed) | (optional) defaults to 1|
| **pageSize** | [**number**] | Itens por página | (optional) defaults to 25|
| **orderBy** | [**string**] | Campo de ordenação: athlete_name, training_load_total, match_load_total, total_load, avg_daily_load | (optional) defaults to undefined|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**LoadReportResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Carga acumulada por atleta |  -  |
|**403** | Equipe fora do escopo do usuário |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMedicalSummaryReportApiV1ReportsMedicalSummaryGet**
> MedicalCasesReport getMedicalSummaryReportApiV1ReportsMedicalSummaryGet()

Retorna resumo de casos médicos e lesões.      **Referências RAG:**     - R13: Estados de atleta (lesionada)     - R14: Impacto de estados em participação     - RP7: Rastreamento de casos médicos      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let status: string; //Status do caso (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMedicalSummaryReportApiV1ReportsMedicalSummaryGet(
    seasonId,
    teamId,
    startDate,
    endDate,
    status,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **status** | [**string**] | Status do caso | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MedicalCasesReport**

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

# **getMedicalSummaryReportApiV1ReportsMedicalSummaryGet_0**
> MedicalCasesReport getMedicalSummaryReportApiV1ReportsMedicalSummaryGet_0()

Retorna resumo de casos médicos e lesões.      **Referências RAG:**     - R13: Estados de atleta (lesionada)     - R14: Impacto de estados em participação     - RP7: Rastreamento de casos médicos      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let status: string; //Status do caso (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMedicalSummaryReportApiV1ReportsMedicalSummaryGet_0(
    seasonId,
    teamId,
    startDate,
    endDate,
    status,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **status** | [**string**] | Status do caso | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MedicalCasesReport**

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

# **getMinutesReportApiV1ReportsMinutesGet**
> MinutesReportResponse getMinutesReportApiV1ReportsMinutesGet()

Retorna minutos jogados por atleta em partidas e treinos.      **Métricas incluídas:**     - Minutos em jogos (minutes_played)     - Minutos em treinos (minutes_effective)     - Jogos com participação (played=true)     - Titularidades (started=true)      **Referências RAG:**     - R19: minutes_played como estatística primária     - R20: Estatísticas agregadas derivadas     - R21: minutes_effective em treinos      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (obrigatório) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Página (1-indexed) (optional) (default to 1)
let pageSize: number; //Itens por página (optional) (default to 25)
let orderBy: string; //Campo de ordenação: athlete_name, total_minutes_played, total_training_minutes, total_activity_minutes (optional) (default to undefined)
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMinutesReportApiV1ReportsMinutesGet(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    pageSize,
    orderBy,
    orderDir,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe (obrigatório) | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Página (1-indexed) | (optional) defaults to 1|
| **pageSize** | [**number**] | Itens por página | (optional) defaults to 25|
| **orderBy** | [**string**] | Campo de ordenação: athlete_name, total_minutes_played, total_training_minutes, total_activity_minutes | (optional) defaults to undefined|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MinutesReportResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Minutos por atleta |  -  |
|**403** | Equipe fora do escopo do usuário |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getMinutesReportApiV1ReportsMinutesGet_0**
> MinutesReportResponse getMinutesReportApiV1ReportsMinutesGet_0()

Retorna minutos jogados por atleta em partidas e treinos.      **Métricas incluídas:**     - Minutos em jogos (minutes_played)     - Minutos em treinos (minutes_effective)     - Jogos com participação (played=true)     - Titularidades (started=true)      **Referências RAG:**     - R19: minutes_played como estatística primária     - R20: Estatísticas agregadas derivadas     - R21: minutes_effective em treinos      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (obrigatório) (default to undefined)
let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let page: number; //Página (1-indexed) (optional) (default to 1)
let pageSize: number; //Itens por página (optional) (default to 25)
let orderBy: string; //Campo de ordenação: athlete_name, total_minutes_played, total_training_minutes, total_activity_minutes (optional) (default to undefined)
let orderDir: string; //Direção: asc ou desc (optional) (default to 'desc')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMinutesReportApiV1ReportsMinutesGet_0(
    teamId,
    seasonId,
    startDate,
    endDate,
    page,
    pageSize,
    orderBy,
    orderDir,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe (obrigatório) | defaults to undefined|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **page** | [**number**] | Página (1-indexed) | (optional) defaults to 1|
| **pageSize** | [**number**] | Itens por página | (optional) defaults to 25|
| **orderBy** | [**string**] | Campo de ordenação: athlete_name, total_minutes_played, total_training_minutes, total_activity_minutes | (optional) defaults to undefined|
| **orderDir** | [**string**] | Direção: asc ou desc | (optional) defaults to 'desc'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MinutesReportResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Minutos por atleta |  -  |
|**403** | Equipe fora do escopo do usuário |  -  |
|**404** | Equipe não encontrada |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getOperationalSessionApiV1ReportsOperationalSessionGet**
> any getOperationalSessionApiV1ReportsOperationalSessionGet()

Retorna contexto, pendências, carga, lista operacional e alertas consolidados.

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let sessionId: string; //ID da sessão (treino ou jogo) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getOperationalSessionApiV1ReportsOperationalSessionGet(
    sessionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **sessionId** | [**string**] | ID da sessão (treino ou jogo) | defaults to undefined|
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

# **getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet**
> TeamTrainingGameCorrelationResponse getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet()

Análise estratégica de correlação entre focos de treino e performance em jogos.          **Pergunta estratégica respondida:**     \"O que do treino está (ou não) se traduzindo em performance de jogo?\"          **Estrutura da resposta:**     - `context`: Contexto da análise (equipe, temporada, competição, período)     - `summary`: Resumo executivo (total de jogos/treinos, médias, força de correlação)     - `training_focus_distribution`: Distribuição dos 7 focos de treino (%)     - `content_translation`: Mapeamento treino → jogo por macroblock (attack/defense/physical)     - `load_vs_performance`: Scatter plot carga × eficiência     - `consistency`: Métricas de variabilidade treino/jogo     - `insights`: Arrays interpretativos (works/adjust/avoid)          **Referências RAG:**     - Especificação: eststisticas_equipes (2,199 linhas)     - RAG/IMPLEMENTACAO_FOCOS_TREINO.md     - R26: Permissões por papel (coordenador, treinador)     - Domínio: /statistics/teams (análise estratégica, não operacional)          **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes     - Dirigente: acesso às equipes da organização

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (default to undefined)
let seasonId: string; //ID da temporada (default to undefined)
let competitionId: string; //ID da competição (opcional) (optional) (default to undefined)
let periodGames: number; //Número de jogos recentes a analisar (optional) (default to 5)
let trainingWindowDays: number; //Janela de treino pré-jogo (dias) (optional) (default to 7)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet(
    teamId,
    seasonId,
    competitionId,
    periodGames,
    trainingWindowDays,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe | defaults to undefined|
| **seasonId** | [**string**] | ID da temporada | defaults to undefined|
| **competitionId** | [**string**] | ID da competição (opcional) | (optional) defaults to undefined|
| **periodGames** | [**number**] | Número de jogos recentes a analisar | (optional) defaults to 5|
| **trainingWindowDays** | [**number**] | Janela de treino pré-jogo (dias) | (optional) defaults to 7|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamTrainingGameCorrelationResponse**

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

# **getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet_0**
> TeamTrainingGameCorrelationResponse getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet_0()

Análise estratégica de correlação entre focos de treino e performance em jogos.          **Pergunta estratégica respondida:**     \"O que do treino está (ou não) se traduzindo em performance de jogo?\"          **Estrutura da resposta:**     - `context`: Contexto da análise (equipe, temporada, competição, período)     - `summary`: Resumo executivo (total de jogos/treinos, médias, força de correlação)     - `training_focus_distribution`: Distribuição dos 7 focos de treino (%)     - `content_translation`: Mapeamento treino → jogo por macroblock (attack/defense/physical)     - `load_vs_performance`: Scatter plot carga × eficiência     - `consistency`: Métricas de variabilidade treino/jogo     - `insights`: Arrays interpretativos (works/adjust/avoid)          **Referências RAG:**     - Especificação: eststisticas_equipes (2,199 linhas)     - RAG/IMPLEMENTACAO_FOCOS_TREINO.md     - R26: Permissões por papel (coordenador, treinador)     - Domínio: /statistics/teams (análise estratégica, não operacional)          **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes     - Dirigente: acesso às equipes da organização

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let teamId: string; //ID da equipe (default to undefined)
let seasonId: string; //ID da temporada (default to undefined)
let competitionId: string; //ID da competição (opcional) (optional) (default to undefined)
let periodGames: number; //Número de jogos recentes a analisar (optional) (default to 5)
let trainingWindowDays: number; //Janela de treino pré-jogo (dias) (optional) (default to 7)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTeamTrainingGameCorrelationApiV1ReportsTeamTrainingGameCorrelationGet_0(
    teamId,
    seasonId,
    competitionId,
    periodGames,
    trainingWindowDays,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] | ID da equipe | defaults to undefined|
| **seasonId** | [**string**] | ID da temporada | defaults to undefined|
| **competitionId** | [**string**] | ID da competição (opcional) | (optional) defaults to undefined|
| **periodGames** | [**number**] | Número de jogos recentes a analisar | (optional) defaults to 5|
| **trainingWindowDays** | [**number**] | Janela de treino pré-jogo (dias) | (optional) defaults to 7|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TeamTrainingGameCorrelationResponse**

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

# **getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet**
> Array<TrainingPerformanceReport> getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet()

Retorna métricas agregadas de performance de treinos.      **Referências RAG:**     - R18: Treinos como eventos operacionais     - R22: Métricas de carga, PSE, assiduidade     - RP5: Ausência gera carga = 0     - RP6: Participação gera métricas obrigatórias      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let minAttendanceRate: number; //Taxa mínima de presença (%) (optional) (default to undefined)
let skip: number; // (optional) (default to 0)
let limit: number; // (optional) (default to 100)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet(
    seasonId,
    teamId,
    startDate,
    endDate,
    minAttendanceRate,
    skip,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **minAttendanceRate** | [**number**] | Taxa mínima de presença (%) | (optional) defaults to undefined|
| **skip** | [**number**] |  | (optional) defaults to 0|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingPerformanceReport>**

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

# **getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet_0**
> Array<TrainingPerformanceReport> getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet_0()

Retorna métricas agregadas de performance de treinos.      **Referências RAG:**     - R18: Treinos como eventos operacionais     - R22: Métricas de carga, PSE, assiduidade     - RP5: Ausência gera carga = 0     - RP6: Participação gera métricas obrigatórias      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let minAttendanceRate: number; //Taxa mínima de presença (%) (optional) (default to undefined)
let skip: number; // (optional) (default to 0)
let limit: number; // (optional) (default to 100)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingPerformanceReportApiV1ReportsTrainingPerformanceGet_0(
    seasonId,
    teamId,
    startDate,
    endDate,
    minAttendanceRate,
    skip,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **minAttendanceRate** | [**number**] | Taxa mínima de presença (%) | (optional) defaults to undefined|
| **skip** | [**number**] |  | (optional) defaults to 0|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingPerformanceReport>**

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

# **getTrainingTrendsApiV1ReportsTrainingTrendsGet**
> Array<TrainingPerformanceTrend> getTrainingTrendsApiV1ReportsTrainingTrendsGet()

Retorna tendências agregadas por período (semana ou mês).      **Referências RAG:**     - R21: Estatísticas agregadas derivadas     - R22: Métricas de treino

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let period: string; // (optional) (default to 'week')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingTrendsApiV1ReportsTrainingTrendsGet(
    seasonId,
    teamId,
    period,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **period** | [**string**] |  | (optional) defaults to 'week'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingPerformanceTrend>**

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

# **getTrainingTrendsApiV1ReportsTrainingTrendsGet_0**
> Array<TrainingPerformanceTrend> getTrainingTrendsApiV1ReportsTrainingTrendsGet_0()

Retorna tendências agregadas por período (semana ou mês).      **Referências RAG:**     - R21: Estatísticas agregadas derivadas     - R22: Métricas de treino

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let period: string; // (optional) (default to 'week')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getTrainingTrendsApiV1ReportsTrainingTrendsGet_0(
    seasonId,
    teamId,
    period,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **period** | [**string**] |  | (optional) defaults to 'week'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<TrainingPerformanceTrend>**

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

# **getViewsStatsApiV1ReportsStatsGet**
> any getViewsStatsApiV1ReportsStatsGet()

Retorna estatísticas sobre todas as materialized views.      **Informações retornadas:**     - Número de registros em cada view     - Schema e metadados     - Último vacuum/refresh      **Referências RAG:**     - RF29: Monitoramento de performance     - RD85: Otimizações      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getViewsStatsApiV1ReportsStatsGet(
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

# **getViewsStatsApiV1ReportsStatsGet_0**
> any getViewsStatsApiV1ReportsStatsGet_0()

Retorna estatísticas sobre todas as materialized views.      **Informações retornadas:**     - Número de registros em cada view     - Schema e metadados     - Último vacuum/refresh      **Referências RAG:**     - RF29: Monitoramento de performance     - RD85: Otimizações      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getViewsStatsApiV1ReportsStatsGet_0(
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

# **getWellnessSummaryReportApiV1ReportsWellnessSummaryGet**
> WellnessSummaryReport getWellnessSummaryReportApiV1ReportsWellnessSummaryGet()

Retorna resumo de bem-estar (wellness pré e pós-treino).      **Referências RAG:**     - RP6: Wellness obrigatório     - RP7: Escalas padronizadas     - RP8: Alertas de sobrecarga e fadiga      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessSummaryReportApiV1ReportsWellnessSummaryGet(
    seasonId,
    teamId,
    startDate,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessSummaryReport**

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

# **getWellnessSummaryReportApiV1ReportsWellnessSummaryGet_0**
> WellnessSummaryReport getWellnessSummaryReportApiV1ReportsWellnessSummaryGet_0()

Retorna resumo de bem-estar (wellness pré e pós-treino).      **Referências RAG:**     - RP6: Wellness obrigatório     - RP7: Escalas padronizadas     - RP8: Alertas de sobrecarga e fadiga      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let startDate: string; //Data inicial (optional) (default to undefined)
let endDate: string; //Data final (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessSummaryReportApiV1ReportsWellnessSummaryGet_0(
    seasonId,
    teamId,
    startDate,
    endDate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **startDate** | [**string**] | Data inicial | (optional) defaults to undefined|
| **endDate** | [**string**] | Data final | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**WellnessSummaryReport**

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

# **getWellnessTrendsApiV1ReportsWellnessTrendsGet**
> Array<{ [key: string]: any; }> getWellnessTrendsApiV1ReportsWellnessTrendsGet()

Retorna tendências de wellness ao longo do tempo.      **Referências RAG:**     - RP8: Monitoramento de sobrecarga      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let period: string; // (optional) (default to 'week')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessTrendsApiV1ReportsWellnessTrendsGet(
    seasonId,
    teamId,
    period,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **period** | [**string**] |  | (optional) defaults to 'week'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<{ [key: string]: any; }>**

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

# **getWellnessTrendsApiV1ReportsWellnessTrendsGet_0**
> Array<{ [key: string]: any; }> getWellnessTrendsApiV1ReportsWellnessTrendsGet_0()

Retorna tendências de wellness ao longo do tempo.      **Referências RAG:**     - RP8: Monitoramento de sobrecarga      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas equipes (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; // (optional) (default to undefined)
let teamId: string; // (optional) (default to undefined)
let period: string; // (optional) (default to 'week')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getWellnessTrendsApiV1ReportsWellnessTrendsGet_0(
    seasonId,
    teamId,
    period,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] |  | (optional) defaults to undefined|
| **teamId** | [**string**] |  | (optional) defaults to undefined|
| **period** | [**string**] |  | (optional) defaults to 'week'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<{ [key: string]: any; }>**

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

# **listAthleteReportsApiV1ReportsAthletesGet**
> Array<AthleteIndividualReport> listAthleteReportsApiV1ReportsAthletesGet()

Lista relatórios individuais de atletas com filtros.      **Referências RAG:**     - R12: Atleta permanente     - R13/R14: Estados e impactos     - RP4: Escopo de participação      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas atletas (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let state: string; //Estado da atleta (optional) (default to undefined)
let minAttendanceRate: number; //Taxa mínima de assiduidade (%) (optional) (default to undefined)
let skip: number; // (optional) (default to 0)
let limit: number; // (optional) (default to 100)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAthleteReportsApiV1ReportsAthletesGet(
    seasonId,
    teamId,
    state,
    minAttendanceRate,
    skip,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **state** | [**string**] | Estado da atleta | (optional) defaults to undefined|
| **minAttendanceRate** | [**number**] | Taxa mínima de assiduidade (%) | (optional) defaults to undefined|
| **skip** | [**number**] |  | (optional) defaults to 0|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<AthleteIndividualReport>**

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

# **listAthleteReportsApiV1ReportsAthletesGet_0**
> Array<AthleteIndividualReport> listAthleteReportsApiV1ReportsAthletesGet_0()

Lista relatórios individuais de atletas com filtros.      **Referências RAG:**     - R12: Atleta permanente     - R13/R14: Estados e impactos     - RP4: Escopo de participação      **Permissões:**     - Coordenador: acesso total     - Treinador: acesso às suas atletas (R26)

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let seasonId: string; //Filtrar por temporada (optional) (default to undefined)
let teamId: string; //Filtrar por equipe (optional) (default to undefined)
let state: string; //Estado da atleta (optional) (default to undefined)
let minAttendanceRate: number; //Taxa mínima de assiduidade (%) (optional) (default to undefined)
let skip: number; // (optional) (default to 0)
let limit: number; // (optional) (default to 100)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listAthleteReportsApiV1ReportsAthletesGet_0(
    seasonId,
    teamId,
    state,
    minAttendanceRate,
    skip,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **seasonId** | [**string**] | Filtrar por temporada | (optional) defaults to undefined|
| **teamId** | [**string**] | Filtrar por equipe | (optional) defaults to undefined|
| **state** | [**string**] | Estado da atleta | (optional) defaults to undefined|
| **minAttendanceRate** | [**number**] | Taxa mínima de assiduidade (%) | (optional) defaults to undefined|
| **skip** | [**number**] |  | (optional) defaults to 0|
| **limit** | [**number**] |  | (optional) defaults to 100|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<AthleteIndividualReport>**

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

# **refreshAllViewsApiV1ReportsRefreshAllPost**
> any refreshAllViewsApiV1ReportsRefreshAllPost()

Atualiza todas as 4 materialized views do sistema de relatórios.      **Operação:**     - Refresha todas as views com CONCURRENTLY (não bloqueia leituras)     - Retorna estatísticas de cada view após refresh      **Referências RAG:**     - RF29: Performance de queries     - RD85: Índices e otimizações     - R21: Atualização de relatórios      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let concurrent: boolean; //Usar CONCURRENTLY (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshAllViewsApiV1ReportsRefreshAllPost(
    concurrent,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **concurrent** | [**boolean**] | Usar CONCURRENTLY | (optional) defaults to true|
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

# **refreshAllViewsApiV1ReportsRefreshAllPost_0**
> any refreshAllViewsApiV1ReportsRefreshAllPost_0()

Atualiza todas as 4 materialized views do sistema de relatórios.      **Operação:**     - Refresha todas as views com CONCURRENTLY (não bloqueia leituras)     - Retorna estatísticas de cada view após refresh      **Referências RAG:**     - RF29: Performance de queries     - RD85: Índices e otimizações     - R21: Atualização de relatórios      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let concurrent: boolean; //Usar CONCURRENTLY (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshAllViewsApiV1ReportsRefreshAllPost_0(
    concurrent,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **concurrent** | [**boolean**] | Usar CONCURRENTLY | (optional) defaults to true|
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

# **refreshSpecificViewApiV1ReportsRefreshViewNamePost**
> any refreshSpecificViewApiV1ReportsRefreshViewNamePost()

Atualiza uma materialized view específica.      **Views disponíveis:**     - training_performance (R1)     - athlete_training_summary (R2)     - wellness_summary (R3)     - medical_cases_summary (R4)      **Referências RAG:**     - RF29: Performance de queries     - RD85: Índices e otimizações     - R21: Atualização de relatórios      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let viewName: 'training_performance' | 'athlete_training_summary' | 'wellness_summary' | 'medical_cases_summary'; // (default to undefined)
let concurrent: boolean; //Usar CONCURRENTLY (recomendado) (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshSpecificViewApiV1ReportsRefreshViewNamePost(
    viewName,
    concurrent,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **viewName** | [**&#39;training_performance&#39; | &#39;athlete_training_summary&#39; | &#39;wellness_summary&#39; | &#39;medical_cases_summary&#39;**]**Array<&#39;training_performance&#39; &#124; &#39;athlete_training_summary&#39; &#124; &#39;wellness_summary&#39; &#124; &#39;medical_cases_summary&#39;>** |  | defaults to undefined|
| **concurrent** | [**boolean**] | Usar CONCURRENTLY (recomendado) | (optional) defaults to true|
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

# **refreshSpecificViewApiV1ReportsRefreshViewNamePost_0**
> any refreshSpecificViewApiV1ReportsRefreshViewNamePost_0()

Atualiza uma materialized view específica.      **Views disponíveis:**     - training_performance (R1)     - athlete_training_summary (R2)     - wellness_summary (R3)     - medical_cases_summary (R4)      **Referências RAG:**     - RF29: Performance de queries     - RD85: Índices e otimizações     - R21: Atualização de relatórios      **Permissões:**     - Coordenador: acesso total

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let viewName: 'training_performance' | 'athlete_training_summary' | 'wellness_summary' | 'medical_cases_summary'; // (default to undefined)
let concurrent: boolean; //Usar CONCURRENTLY (recomendado) (optional) (default to true)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshSpecificViewApiV1ReportsRefreshViewNamePost_0(
    viewName,
    concurrent,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **viewName** | [**&#39;training_performance&#39; | &#39;athlete_training_summary&#39; | &#39;wellness_summary&#39; | &#39;medical_cases_summary&#39;**]**Array<&#39;training_performance&#39; &#124; &#39;athlete_training_summary&#39; &#124; &#39;wellness_summary&#39; &#124; &#39;medical_cases_summary&#39;>** |  | defaults to undefined|
| **concurrent** | [**boolean**] | Usar CONCURRENTLY (recomendado) | (optional) defaults to true|
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

# **refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost**
> any refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost()

Atualiza a materialized view de performance de treinos.      **Referências RAG:**     - R21: Estatísticas agregadas recalculáveis      **Permissões:**     - Apenas Coordenador

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost(
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

# **refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost_0**
> any refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost_0()

Atualiza a materialized view de performance de treinos.      **Referências RAG:**     - R21: Estatísticas agregadas recalculáveis      **Permissões:**     - Apenas Coordenador

### Example

```typescript
import {
    ReportsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new ReportsApi(configuration);

let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.refreshTrainingPerformanceApiV1ReportsRefreshTrainingPerformancePost_0(
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

