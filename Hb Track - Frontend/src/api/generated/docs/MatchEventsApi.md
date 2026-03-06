# MatchEventsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addEventToMatch**](#addeventtomatch) | **POST** /api/v1/matches/matches/{match_id}/events | Adicionar evento ao jogo|
|[**addEventToMatch_0**](#addeventtomatch_0) | **POST** /api/v1/matches/matches/{match_id}/events | Adicionar evento ao jogo|
|[**bulkCreateMatchEvents**](#bulkcreatematchevents) | **POST** /api/v1/matches/matches/{match_id}/events/bulk | Criar eventos em lote|
|[**bulkCreateMatchEvents_0**](#bulkcreatematchevents_0) | **POST** /api/v1/matches/matches/{match_id}/events/bulk | Criar eventos em lote|
|[**correctMatchEvent**](#correctmatchevent) | **POST** /api/v1/matches/match_events/{match_event_id}/correct | Corrigir evento com histórico|
|[**correctMatchEvent_0**](#correctmatchevent_0) | **POST** /api/v1/matches/match_events/{match_event_id}/correct | Corrigir evento com histórico|
|[**deleteMatchEvent**](#deletematchevent) | **DELETE** /api/v1/matches/match_events/{match_event_id} | Excluir evento|
|[**deleteMatchEvent_0**](#deletematchevent_0) | **DELETE** /api/v1/matches/match_events/{match_event_id} | Excluir evento|
|[**getAthleteMatchStats**](#getathletematchstats) | **GET** /api/v1/matches/matches/{match_id}/stats/athlete/{athlete_id} | Estatísticas do atleta na partida|
|[**getAthleteMatchStats_0**](#getathletematchstats_0) | **GET** /api/v1/matches/matches/{match_id}/stats/athlete/{athlete_id} | Estatísticas do atleta na partida|
|[**listMatchEvents**](#listmatchevents) | **GET** /api/v1/matches/matches/{match_id}/events | Listar eventos do jogo|
|[**listMatchEvents_0**](#listmatchevents_0) | **GET** /api/v1/matches/matches/{match_id}/events | Listar eventos do jogo|
|[**scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost**](#scopedaddeventtomatchapiv1teamsteamidmatchesmatchideventspost) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/events | Adicionar evento ao jogo (escopo equipe)|
|[**scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost_0**](#scopedaddeventtomatchapiv1teamsteamidmatchesmatchideventspost_0) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/events | Adicionar evento ao jogo (escopo equipe)|
|[**scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost**](#scopedbulkcreatematcheventsapiv1teamsteamidmatchesmatchideventsbulkpost) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/events/bulk | Criar eventos em lote (escopo equipe)|
|[**scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost_0**](#scopedbulkcreatematcheventsapiv1teamsteamidmatchesmatchideventsbulkpost_0) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/events/bulk | Criar eventos em lote (escopo equipe)|
|[**scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost**](#scopedcorrectmatcheventapiv1teamsteamidmatchesmatchidmatcheventsmatcheventidcorrectpost) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/match_events/{match_event_id}/correct | Corrigir evento (escopo equipe)|
|[**scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost_0**](#scopedcorrectmatcheventapiv1teamsteamidmatchesmatchidmatcheventsmatcheventidcorrectpost_0) | **POST** /api/v1/teams/{team_id}/matches/{match_id}/match_events/{match_event_id}/correct | Corrigir evento (escopo equipe)|
|[**scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete**](#scopeddeletematcheventapiv1teamsteamidmatchesmatchidmatcheventsmatcheventiddelete) | **DELETE** /api/v1/teams/{team_id}/matches/{match_id}/match_events/{match_event_id} | Excluir evento (escopo equipe)|
|[**scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete_0**](#scopeddeletematcheventapiv1teamsteamidmatchesmatchidmatcheventsmatcheventiddelete_0) | **DELETE** /api/v1/teams/{team_id}/matches/{match_id}/match_events/{match_event_id} | Excluir evento (escopo equipe)|
|[**scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet**](#scopedgetathletematchstatsapiv1teamsteamidmatchesmatchidstatsathleteathleteidget) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/stats/athlete/{athlete_id} | Estatísticas do atleta na partida (escopo equipe)|
|[**scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet_0**](#scopedgetathletematchstatsapiv1teamsteamidmatchesmatchidstatsathleteathleteidget_0) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/stats/athlete/{athlete_id} | Estatísticas do atleta na partida (escopo equipe)|
|[**scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet**](#scopedlistmatcheventsapiv1teamsteamidmatchesmatchideventsget) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/events | Listar eventos do jogo (escopo equipe)|
|[**scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet_0**](#scopedlistmatcheventsapiv1teamsteamidmatchesmatchideventsget_0) | **GET** /api/v1/teams/{team_id}/matches/{match_id}/events | Listar eventos do jogo (escopo equipe)|
|[**scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch**](#scopedupdatematcheventapiv1teamsteamidmatchesmatchidmatcheventsmatcheventidpatch) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id}/match_events/{match_event_id} | Atualizar evento (escopo equipe)|
|[**scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch_0**](#scopedupdatematcheventapiv1teamsteamidmatchesmatchidmatcheventsmatcheventidpatch_0) | **PATCH** /api/v1/teams/{team_id}/matches/{match_id}/match_events/{match_event_id} | Atualizar evento (escopo equipe)|
|[**updateMatchEvent**](#updatematchevent) | **PATCH** /api/v1/matches/match_events/{match_event_id} | Atualizar evento do jogo|
|[**updateMatchEvent_0**](#updatematchevent_0) | **PATCH** /api/v1/matches/match_events/{match_event_id} | Atualizar evento do jogo|

# **addEventToMatch**
> ScoutEventRead addEventToMatch(scoutEventCreate)

Adiciona um novo evento ao jogo (gol, falta, etc.).  **Regras aplicáveis:** - RDB13: Bloquear se jogo finalizado → 409 edit_finalized_game - RD4: Atleta deve estar no roster do time - RF15: Partida não pode estar finalizada - R25/R26: Permissões por papel e escopo  **event_type canônicos (11):** goal, shot, seven_meter, goalkeeper_save, turnover, foul, exclusion_2min, yellow_card, red_card, substitution, timeout — ref: event_types table

### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    ScoutEventCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let scoutEventCreate: ScoutEventCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addEventToMatch(
    matchId,
    scoutEventCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **ScoutEventCreate**|  | |
| **matchId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Evento criado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo, equipe ou atleta não encontrado |  -  |
|**409** | Conflito (jogo finalizado ou temporada bloqueada) |  -  |
|**422** | Erro de validação ou regra de goleira (RD13/RD22) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **addEventToMatch_0**
> ScoutEventRead addEventToMatch_0(scoutEventCreate)

Adiciona um novo evento ao jogo (gol, falta, etc.).  **Regras aplicáveis:** - RDB13: Bloquear se jogo finalizado → 409 edit_finalized_game - RD4: Atleta deve estar no roster do time - RF15: Partida não pode estar finalizada - R25/R26: Permissões por papel e escopo  **event_type canônicos (11):** goal, shot, seven_meter, goalkeeper_save, turnover, foul, exclusion_2min, yellow_card, red_card, substitution, timeout — ref: event_types table

### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    ScoutEventCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let scoutEventCreate: ScoutEventCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.addEventToMatch_0(
    matchId,
    scoutEventCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **ScoutEventCreate**|  | |
| **matchId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Evento criado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo, equipe ou atleta não encontrado |  -  |
|**409** | Conflito (jogo finalizado ou temporada bloqueada) |  -  |
|**422** | Erro de validação ou regra de goleira (RD13/RD22) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulkCreateMatchEvents**
> Array<ScoutEventRead> bulkCreateMatchEvents(scoutEventCreate)

Cria múltiplos eventos em lote. Útil para importação de súmula.

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let scoutEventCreate: Array<ScoutEventCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkCreateMatchEvents(
    matchId,
    scoutEventCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **Array<ScoutEventCreate>**|  | |
| **matchId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ScoutEventRead>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Eventos criados |  -  |
|**403** | Partida finalizada |  -  |
|**422** | Dados inválidos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulkCreateMatchEvents_0**
> Array<ScoutEventRead> bulkCreateMatchEvents_0(scoutEventCreate)

Cria múltiplos eventos em lote. Útil para importação de súmula.

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let scoutEventCreate: Array<ScoutEventCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkCreateMatchEvents_0(
    matchId,
    scoutEventCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **Array<ScoutEventCreate>**|  | |
| **matchId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ScoutEventRead>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Eventos criados |  -  |
|**403** | Partida finalizada |  -  |
|**422** | Dados inválidos |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **correctMatchEvent**
> ScoutEventRead correctMatchEvent(matchEventCorrection)

Corrige evento com histórico obrigatório.  **Regras aplicáveis:** - R23/R24: Correção com justificativa e registro de valor anterior  Salva os valores anteriores em previous_value (JSON) e registra a justificativa em correction_note.

### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventCorrection
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchEventId: string; // (default to undefined)
let matchEventCorrection: MatchEventCorrection; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.correctMatchEvent(
    matchEventId,
    matchEventCorrection,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventCorrection** | **MatchEventCorrection**|  | |
| **matchEventId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Evento corrigido com histórico |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Match event não encontrado |  -  |
|**422** | Justificativa obrigatória |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **correctMatchEvent_0**
> ScoutEventRead correctMatchEvent_0(matchEventCorrection)

Corrige evento com histórico obrigatório.  **Regras aplicáveis:** - R23/R24: Correção com justificativa e registro de valor anterior  Salva os valores anteriores em previous_value (JSON) e registra a justificativa em correction_note.

### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventCorrection
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchEventId: string; // (default to undefined)
let matchEventCorrection: MatchEventCorrection; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.correctMatchEvent_0(
    matchEventId,
    matchEventCorrection,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventCorrection** | **MatchEventCorrection**|  | |
| **matchEventId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Evento corrigido com histórico |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente |  -  |
|**404** | Match event não encontrado |  -  |
|**422** | Justificativa obrigatória |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteMatchEvent**
> ScoutEventRead deleteMatchEvent()

Soft delete de evento.  **Regras aplicáveis:** - RDB3: Soft delete com deleted_at e deleted_reason - RF15: Partida não pode estar finalizada

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchEventId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteMatchEvent(
    matchEventId,
    reason,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Evento excluído (soft delete) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Partida finalizada |  -  |
|**404** | Match event não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteMatchEvent_0**
> ScoutEventRead deleteMatchEvent_0()

Soft delete de evento.  **Regras aplicáveis:** - RDB3: Soft delete com deleted_at e deleted_reason - RF15: Partida não pode estar finalizada

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchEventId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteMatchEvent_0(
    matchEventId,
    reason,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Evento excluído (soft delete) |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Partida finalizada |  -  |
|**404** | Match event não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAthleteMatchStats**
> AthleteMatchStats getAthleteMatchStats()

Retorna estatísticas agregadas de um atleta em uma partida.  **Regras aplicáveis:** - RD1-RD91: Agregação de eventos estatísticos  Retorna gols, assistências, cartões, defesas, etc.

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteMatchStats(
    matchId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteMatchStats**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Estatísticas agregadas do atleta |  -  |
|**404** | Partida ou atleta não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAthleteMatchStats_0**
> AthleteMatchStats getAthleteMatchStats_0()

Retorna estatísticas agregadas de um atleta em uma partida.  **Regras aplicáveis:** - RD1-RD91: Agregação de eventos estatísticos  Retorna gols, assistências, cartões, defesas, etc.

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getAthleteMatchStats_0(
    matchId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteMatchStats**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Estatísticas agregadas do atleta |  -  |
|**404** | Partida ou atleta não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listMatchEvents**
> MatchEventList listMatchEvents()

Lista eventos do jogo (gols, faltas, etc.) de forma paginada.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - RD1-RD91: Eventos estatísticos do handball  **Paginação:** - page: Número da página (1-indexed) - limit: Itens por página (1-100, padrão 50)  **Envelope de resposta:** {items, page, size, total, pages}

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let athleteId: string; //Filtrar por atleta (optional) (default to undefined)
let eventType: EventType; //Filtrar por tipo de evento (optional) (default to undefined)
let period: number; //Filtrar por período (optional) (default to undefined)
let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listMatchEvents(
    matchId,
    athleteId,
    eventType,
    period,
    page,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] | Filtrar por atleta | (optional) defaults to undefined|
| **eventType** | **EventType** | Filtrar por tipo de evento | (optional) defaults to undefined|
| **period** | [**number**] | Filtrar por período | (optional) defaults to undefined|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchEventList**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de eventos do jogo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listMatchEvents_0**
> MatchEventList listMatchEvents_0()

Lista eventos do jogo (gols, faltas, etc.) de forma paginada.  **Regras aplicáveis:** - R25/R26: Permissões por papel e escopo - RD1-RD91: Eventos estatísticos do handball  **Paginação:** - page: Número da página (1-indexed) - limit: Itens por página (1-100, padrão 50)  **Envelope de resposta:** {items, page, size, total, pages}

### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchId: string; // (default to undefined)
let athleteId: string; //Filtrar por atleta (optional) (default to undefined)
let eventType: EventType; //Filtrar por tipo de evento (optional) (default to undefined)
let period: number; //Filtrar por período (optional) (default to undefined)
let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listMatchEvents_0(
    matchId,
    athleteId,
    eventType,
    period,
    page,
    limit,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] | Filtrar por atleta | (optional) defaults to undefined|
| **eventType** | **EventType** | Filtrar por tipo de evento | (optional) defaults to undefined|
| **period** | [**number**] | Filtrar por período | (optional) defaults to undefined|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchEventList**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Lista paginada de eventos do jogo |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Jogo não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost**
> ScoutEventRead scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost(scoutEventCreate)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    ScoutEventCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let scoutEventCreate: ScoutEventCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost(
    teamId,
    matchId,
    scoutEventCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **ScoutEventCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost_0**
> ScoutEventRead scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost_0(scoutEventCreate)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    ScoutEventCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let scoutEventCreate: ScoutEventCreate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedAddEventToMatchApiV1TeamsTeamIdMatchesMatchIdEventsPost_0(
    teamId,
    matchId,
    scoutEventCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **ScoutEventCreate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost**
> Array<ScoutEventRead> scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost(scoutEventCreate)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let scoutEventCreate: Array<ScoutEventCreate>; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost(
    teamId,
    matchId,
    scoutEventCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **Array<ScoutEventCreate>**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ScoutEventRead>**

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

# **scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost_0**
> Array<ScoutEventRead> scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost_0(scoutEventCreate)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let scoutEventCreate: Array<ScoutEventCreate>; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedBulkCreateMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsBulkPost_0(
    teamId,
    matchId,
    scoutEventCreate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **scoutEventCreate** | **Array<ScoutEventCreate>**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<ScoutEventRead>**

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

# **scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost**
> ScoutEventRead scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost(matchEventCorrection)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventCorrection
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchEventId: string; // (default to undefined)
let matchEventCorrection: MatchEventCorrection; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost(
    teamId,
    matchId,
    matchEventId,
    matchEventCorrection,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventCorrection** | **MatchEventCorrection**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost_0**
> ScoutEventRead scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost_0(matchEventCorrection)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventCorrection
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchEventId: string; // (default to undefined)
let matchEventCorrection: MatchEventCorrection; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedCorrectMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdCorrectPost_0(
    teamId,
    matchId,
    matchEventId,
    matchEventCorrection,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventCorrection** | **MatchEventCorrection**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete**
> ScoutEventRead scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete()


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchEventId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete(
    teamId,
    matchId,
    matchEventId,
    reason,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete_0**
> ScoutEventRead scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete_0()


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchEventId: string; // (default to undefined)
let reason: string; //Motivo da exclusão (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedDeleteMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdDelete_0(
    teamId,
    matchId,
    matchEventId,
    reason,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **reason** | [**string**] | Motivo da exclusão | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet**
> AthleteMatchStats scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet()


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet(
    teamId,
    matchId,
    athleteId,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteMatchStats**

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

# **scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet_0**
> AthleteMatchStats scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet_0()


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let athleteId: string; // (default to undefined)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedGetAthleteMatchStatsApiV1TeamsTeamIdMatchesMatchIdStatsAthleteAthleteIdGet_0(
    teamId,
    matchId,
    athleteId,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AthleteMatchStats**

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

# **scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet**
> MatchEventList scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet()


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let eventType: EventType; //Filtrar por tipo de evento (optional) (default to undefined)
let period: number; //Filtrar por período (optional) (default to undefined)
let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet(
    teamId,
    matchId,
    athleteId,
    eventType,
    period,
    page,
    limit,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **eventType** | **EventType** | Filtrar por tipo de evento | (optional) defaults to undefined|
| **period** | [**number**] | Filtrar por período | (optional) defaults to undefined|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchEventList**

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

# **scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet_0**
> MatchEventList scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet_0()


### Example

```typescript
import {
    MatchEventsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let eventType: EventType; //Filtrar por tipo de evento (optional) (default to undefined)
let period: number; //Filtrar por período (optional) (default to undefined)
let page: number; //Número da página (1-indexed) (optional) (default to 1)
let limit: number; //Itens por página (máximo 100) (optional) (default to 50)
let organizationId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedListMatchEventsApiV1TeamsTeamIdMatchesMatchIdEventsGet_0(
    teamId,
    matchId,
    athleteId,
    eventType,
    period,
    page,
    limit,
    organizationId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **eventType** | **EventType** | Filtrar por tipo de evento | (optional) defaults to undefined|
| **period** | [**number**] | Filtrar por período | (optional) defaults to undefined|
| **page** | [**number**] | Número da página (1-indexed) | (optional) defaults to 1|
| **limit** | [**number**] | Itens por página (máximo 100) | (optional) defaults to 50|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MatchEventList**

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

# **scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch**
> ScoutEventRead scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch(matchEventUpdate)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchEventId: string; // (default to undefined)
let matchEventUpdate: MatchEventUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch(
    teamId,
    matchId,
    matchEventId,
    matchEventUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventUpdate** | **MatchEventUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch_0**
> ScoutEventRead scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch_0(matchEventUpdate)


### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let teamId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let matchEventId: string; // (default to undefined)
let matchEventUpdate: MatchEventUpdate; //
let organizationId: string; // (optional) (default to undefined)
let athleteId: string; // (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.scopedUpdateMatchEventApiV1TeamsTeamIdMatchesMatchIdMatchEventsMatchEventIdPatch_0(
    teamId,
    matchId,
    matchEventId,
    matchEventUpdate,
    organizationId,
    athleteId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventUpdate** | **MatchEventUpdate**|  | |
| **teamId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **matchEventId** | [**string**] |  | defaults to undefined|
| **organizationId** | [**string**] |  | (optional) defaults to undefined|
| **athleteId** | [**string**] |  | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

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

# **updateMatchEvent**
> ScoutEventRead updateMatchEvent(matchEventUpdate)

Atualiza atributos de um evento do jogo.  **Campos editáveis:** event_type, period_number, game_time_seconds, x_coord, y_coord, notes **Campos NÃO editáveis:** match_id, athlete_id  **Regras aplicáveis:** - RDB13/RF15: Bloquear se jogo finalizado → 409 edit_finalized_game - R25/R26: Permissões por papel e escopo  Para correções com histórico, use POST /match_events/{id}/correct

### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchEventId: string; // (default to undefined)
let matchEventUpdate: MatchEventUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateMatchEvent(
    matchEventId,
    matchEventUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventUpdate** | **MatchEventUpdate**|  | |
| **matchEventId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Evento atualizado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Match event não encontrado |  -  |
|**409** | Jogo finalizado (RDB13) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateMatchEvent_0**
> ScoutEventRead updateMatchEvent_0(matchEventUpdate)

Atualiza atributos de um evento do jogo.  **Campos editáveis:** event_type, period_number, game_time_seconds, x_coord, y_coord, notes **Campos NÃO editáveis:** match_id, athlete_id  **Regras aplicáveis:** - RDB13/RF15: Bloquear se jogo finalizado → 409 edit_finalized_game - R25/R26: Permissões por papel e escopo  Para correções com histórico, use POST /match_events/{id}/correct

### Example

```typescript
import {
    MatchEventsApi,
    Configuration,
    MatchEventUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MatchEventsApi(configuration);

let matchEventId: string; // (default to undefined)
let matchEventUpdate: MatchEventUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateMatchEvent_0(
    matchEventId,
    matchEventUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **matchEventUpdate** | **MatchEventUpdate**|  | |
| **matchEventId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ScoutEventRead**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Evento atualizado |  -  |
|**401** | Token inválido ou ausente |  -  |
|**403** | Permissão insuficiente (R25/R26) |  -  |
|**404** | Match event não encontrado |  -  |
|**409** | Jogo finalizado (RDB13) |  -  |
|**422** | Erro de validação |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

