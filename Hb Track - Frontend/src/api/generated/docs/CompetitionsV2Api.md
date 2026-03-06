# CompetitionsV2Api

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bulkCreateMatches**](#bulkcreatematches) | **POST** /api/v1/competitions/{competition_id}/matches/bulk | Criar vários jogos de uma vez (com upsert)|
|[**bulkCreateMatches_0**](#bulkcreatematches_0) | **POST** /api/v1/competitions/{competition_id}/matches/bulk | Criar vários jogos de uma vez (com upsert)|
|[**bulkCreateOpponentTeams**](#bulkcreateopponentteams) | **POST** /api/v1/competitions/{competition_id}/opponent-teams/bulk | Criar várias equipes adversárias de uma vez|
|[**bulkCreateOpponentTeams_0**](#bulkcreateopponentteams_0) | **POST** /api/v1/competitions/{competition_id}/opponent-teams/bulk | Criar várias equipes adversárias de uma vez|
|[**createCompetitionMatch**](#createcompetitionmatch) | **POST** /api/v1/competitions/{competition_id}/matches | Criar jogo na competição|
|[**createCompetitionMatch_0**](#createcompetitionmatch_0) | **POST** /api/v1/competitions/{competition_id}/matches | Criar jogo na competição|
|[**createCompetitionPhase**](#createcompetitionphase) | **POST** /api/v1/competitions/{competition_id}/phases | Criar fase na competição|
|[**createCompetitionPhase_0**](#createcompetitionphase_0) | **POST** /api/v1/competitions/{competition_id}/phases | Criar fase na competição|
|[**createCompetitionV2**](#createcompetitionv2) | **POST** /api/v1/competitions/v2 | Criar competição V2 (com novos campos)|
|[**createCompetitionV2_0**](#createcompetitionv2_0) | **POST** /api/v1/competitions/v2 | Criar competição V2 (com novos campos)|
|[**createOpponentTeam**](#createopponentteam) | **POST** /api/v1/competitions/{competition_id}/opponent-teams | Criar equipe adversária|
|[**createOpponentTeam_0**](#createopponentteam_0) | **POST** /api/v1/competitions/{competition_id}/opponent-teams | Criar equipe adversária|
|[**deleteCompetitionPhase**](#deletecompetitionphase) | **DELETE** /api/v1/competitions/{competition_id}/phases/{phase_id} | Remover fase|
|[**deleteCompetitionPhase_0**](#deletecompetitionphase_0) | **DELETE** /api/v1/competitions/{competition_id}/phases/{phase_id} | Remover fase|
|[**getCompetitionFull**](#getcompetitionfull) | **GET** /api/v1/competitions/v2/{competition_id}/full | Obter competição com todos os relacionamentos|
|[**getCompetitionFull_0**](#getcompetitionfull_0) | **GET** /api/v1/competitions/v2/{competition_id}/full | Obter competição com todos os relacionamentos|
|[**getCompetitionStandings**](#getcompetitionstandings) | **GET** /api/v1/competitions/{competition_id}/standings | Obter classificação da competição|
|[**getCompetitionStandings_0**](#getcompetitionstandings_0) | **GET** /api/v1/competitions/{competition_id}/standings | Obter classificação da competição|
|[**importFromAI**](#importfromai) | **POST** /api/v1/competitions/v2/{competition_id}/import-from-ai | Importar dados extraídos pela IA para uma competição|
|[**importFromAI_0**](#importfromai_0) | **POST** /api/v1/competitions/v2/{competition_id}/import-from-ai | Importar dados extraídos pela IA para uma competição|
|[**listCompetitionMatches**](#listcompetitionmatches) | **GET** /api/v1/competitions/{competition_id}/matches | Listar jogos da competição|
|[**listCompetitionMatches_0**](#listcompetitionmatches_0) | **GET** /api/v1/competitions/{competition_id}/matches | Listar jogos da competição|
|[**listCompetitionPhases**](#listcompetitionphases) | **GET** /api/v1/competitions/{competition_id}/phases | Listar fases da competição|
|[**listCompetitionPhases_0**](#listcompetitionphases_0) | **GET** /api/v1/competitions/{competition_id}/phases | Listar fases da competição|
|[**listOpponentTeams**](#listopponentteams) | **GET** /api/v1/competitions/{competition_id}/opponent-teams | Listar equipes adversárias|
|[**listOpponentTeams_0**](#listopponentteams_0) | **GET** /api/v1/competitions/{competition_id}/opponent-teams | Listar equipes adversárias|
|[**parsePdfWithAI**](#parsepdfwithai) | **POST** /api/v1/competitions/v2/parse-pdf | Extrair dados de PDF via IA (Gemini)|
|[**parsePdfWithAI_0**](#parsepdfwithai_0) | **POST** /api/v1/competitions/v2/parse-pdf | Extrair dados de PDF via IA (Gemini)|
|[**updateCompetitionPhase**](#updatecompetitionphase) | **PATCH** /api/v1/competitions/{competition_id}/phases/{phase_id} | Atualizar fase|
|[**updateCompetitionPhase_0**](#updatecompetitionphase_0) | **PATCH** /api/v1/competitions/{competition_id}/phases/{phase_id} | Atualizar fase|
|[**updateMatchResult**](#updatematchresult) | **PATCH** /api/v1/competitions/{competition_id}/matches/{match_id}/result | Atualizar resultado do jogo|
|[**updateMatchResult_0**](#updatematchresult_0) | **PATCH** /api/v1/competitions/{competition_id}/matches/{match_id}/result | Atualizar resultado do jogo|
|[**updateOpponentTeam**](#updateopponentteam) | **PATCH** /api/v1/competitions/{competition_id}/opponent-teams/{team_id} | Atualizar equipe adversária|
|[**updateOpponentTeam_0**](#updateopponentteam_0) | **PATCH** /api/v1/competitions/{competition_id}/opponent-teams/{team_id} | Atualizar equipe adversária|

# **bulkCreateMatches**
> { [key: string]: any; } bulkCreateMatches(competitionMatchCreate)

Cria vários jogos de uma vez. Se external_reference_id já existir, atualiza o jogo existente (upsert).

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionMatchCreate: Array<CompetitionMatchCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkCreateMatches(
    competitionId,
    competitionMatchCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionMatchCreate** | **Array<CompetitionMatchCreate>**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **bulkCreateMatches_0**
> { [key: string]: any; } bulkCreateMatches_0(competitionMatchCreate)

Cria vários jogos de uma vez. Se external_reference_id já existir, atualiza o jogo existente (upsert).

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionMatchCreate: Array<CompetitionMatchCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkCreateMatches_0(
    competitionId,
    competitionMatchCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionMatchCreate** | **Array<CompetitionMatchCreate>**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **bulkCreateOpponentTeams**
> Array<CompetitionOpponentTeamResponse> bulkCreateOpponentTeams(competitionOpponentTeamCreate)

Cria várias equipes adversárias de uma vez.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionOpponentTeamCreate: Array<CompetitionOpponentTeamCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkCreateOpponentTeams(
    competitionId,
    competitionOpponentTeamCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionOpponentTeamCreate** | **Array<CompetitionOpponentTeamCreate>**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionOpponentTeamResponse>**

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

# **bulkCreateOpponentTeams_0**
> Array<CompetitionOpponentTeamResponse> bulkCreateOpponentTeams_0(competitionOpponentTeamCreate)

Cria várias equipes adversárias de uma vez.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionOpponentTeamCreate: Array<CompetitionOpponentTeamCreate>; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.bulkCreateOpponentTeams_0(
    competitionId,
    competitionOpponentTeamCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionOpponentTeamCreate** | **Array<CompetitionOpponentTeamCreate>**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionOpponentTeamResponse>**

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

# **createCompetitionMatch**
> CompetitionMatchResponse createCompetitionMatch(competitionMatchCreate)

Cria um novo jogo na competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionMatchCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionMatchCreate: CompetitionMatchCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionMatch(
    competitionId,
    competitionMatchCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionMatchCreate** | **CompetitionMatchCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionMatchResponse**

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

# **createCompetitionMatch_0**
> CompetitionMatchResponse createCompetitionMatch_0(competitionMatchCreate)

Cria um novo jogo na competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionMatchCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionMatchCreate: CompetitionMatchCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionMatch_0(
    competitionId,
    competitionMatchCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionMatchCreate** | **CompetitionMatchCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionMatchResponse**

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

# **createCompetitionPhase**
> CompetitionPhaseResponse createCompetitionPhase(competitionPhaseCreate)

Cria uma nova fase na competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionPhaseCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionPhaseCreate: CompetitionPhaseCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionPhase(
    competitionId,
    competitionPhaseCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionPhaseCreate** | **CompetitionPhaseCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionPhaseResponse**

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

# **createCompetitionPhase_0**
> CompetitionPhaseResponse createCompetitionPhase_0(competitionPhaseCreate)

Cria uma nova fase na competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionPhaseCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionPhaseCreate: CompetitionPhaseCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionPhase_0(
    competitionId,
    competitionPhaseCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionPhaseCreate** | **CompetitionPhaseCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionPhaseResponse**

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

# **createCompetitionV2**
> CompetitionV2Response createCompetitionV2(competitionV2Create)

Cria uma nova competição com todos os campos V2.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionV2Create
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionV2Create: CompetitionV2Create; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionV2(
    competitionV2Create,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionV2Create** | **CompetitionV2Create**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionV2Response**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Competição criada com sucesso |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createCompetitionV2_0**
> CompetitionV2Response createCompetitionV2_0(competitionV2Create)

Cria uma nova competição com todos os campos V2.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionV2Create
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionV2Create: CompetitionV2Create; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createCompetitionV2_0(
    competitionV2Create,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionV2Create** | **CompetitionV2Create**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionV2Response**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Competição criada com sucesso |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createOpponentTeam**
> CompetitionOpponentTeamResponse createOpponentTeam(competitionOpponentTeamCreate)

Cria uma nova equipe adversária na competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionOpponentTeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionOpponentTeamCreate: CompetitionOpponentTeamCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createOpponentTeam(
    competitionId,
    competitionOpponentTeamCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionOpponentTeamCreate** | **CompetitionOpponentTeamCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionOpponentTeamResponse**

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

# **createOpponentTeam_0**
> CompetitionOpponentTeamResponse createOpponentTeam_0(competitionOpponentTeamCreate)

Cria uma nova equipe adversária na competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionOpponentTeamCreate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let competitionOpponentTeamCreate: CompetitionOpponentTeamCreate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.createOpponentTeam_0(
    competitionId,
    competitionOpponentTeamCreate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionOpponentTeamCreate** | **CompetitionOpponentTeamCreate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionOpponentTeamResponse**

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

# **deleteCompetitionPhase**
> deleteCompetitionPhase()

Remove uma fase da competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteCompetitionPhase(
    competitionId,
    phaseId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteCompetitionPhase_0**
> deleteCompetitionPhase_0()

Remove uma fase da competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.deleteCompetitionPhase_0(
    competitionId,
    phaseId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCompetitionFull**
> CompetitionV2WithRelations getCompetitionFull()

Retorna competição com fases, equipes e contagem de jogos.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionFull(
    competitionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionV2WithRelations**

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

# **getCompetitionFull_0**
> CompetitionV2WithRelations getCompetitionFull_0()

Retorna competição com fases, equipes e contagem de jogos.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionFull_0(
    competitionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionV2WithRelations**

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

# **getCompetitionStandings**
> Array<CompetitionStandingResponse> getCompetitionStandings()

Retorna a classificação da competição. Se não houver dados em competition_standings, calcula a partir dos jogos.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; //Filtrar por fase (optional) (default to undefined)
let groupName: string; //Filtrar por grupo (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionStandings(
    competitionId,
    phaseId,
    groupName,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] | Filtrar por fase | (optional) defaults to undefined|
| **groupName** | [**string**] | Filtrar por grupo | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionStandingResponse>**

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

# **getCompetitionStandings_0**
> Array<CompetitionStandingResponse> getCompetitionStandings_0()

Retorna a classificação da competição. Se não houver dados em competition_standings, calcula a partir dos jogos.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; //Filtrar por fase (optional) (default to undefined)
let groupName: string; //Filtrar por grupo (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getCompetitionStandings_0(
    competitionId,
    phaseId,
    groupName,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] | Filtrar por fase | (optional) defaults to undefined|
| **groupName** | [**string**] | Filtrar por grupo | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionStandingResponse>**

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

# **importFromAI**
> CompetitionV2WithRelations importFromAI(aIValidateAndSaveRequest)

Importa os dados extraídos pela IA para uma competição existente.  Este endpoint: 1. Atualiza os campos da competição 2. Cria as fases 3. Cria as equipes adversárias 4. Cria os jogos (com external_reference_id para upsert)

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    AIValidateAndSaveRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let aIValidateAndSaveRequest: AIValidateAndSaveRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.importFromAI(
    competitionId,
    aIValidateAndSaveRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIValidateAndSaveRequest** | **AIValidateAndSaveRequest**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionV2WithRelations**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dados importados com sucesso |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **importFromAI_0**
> CompetitionV2WithRelations importFromAI_0(aIValidateAndSaveRequest)

Importa os dados extraídos pela IA para uma competição existente.  Este endpoint: 1. Atualiza os campos da competição 2. Cria as fases 3. Cria as equipes adversárias 4. Cria os jogos (com external_reference_id para upsert)

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    AIValidateAndSaveRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let aIValidateAndSaveRequest: AIValidateAndSaveRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.importFromAI_0(
    competitionId,
    aIValidateAndSaveRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIValidateAndSaveRequest** | **AIValidateAndSaveRequest**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionV2WithRelations**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dados importados com sucesso |  -  |
|**404** | Competição não encontrada |  -  |
|**422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCompetitionMatches**
> Array<CompetitionMatchResponse> listCompetitionMatches()

Lista todos os jogos de uma competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; //Filtrar por fase (optional) (default to undefined)
let onlyOurMatches: boolean; //Apenas nossos jogos (optional) (default to false)
let statusFilter: string; //Filtrar por status (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionMatches(
    competitionId,
    phaseId,
    onlyOurMatches,
    statusFilter,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] | Filtrar por fase | (optional) defaults to undefined|
| **onlyOurMatches** | [**boolean**] | Apenas nossos jogos | (optional) defaults to false|
| **statusFilter** | [**string**] | Filtrar por status | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionMatchResponse>**

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

# **listCompetitionMatches_0**
> Array<CompetitionMatchResponse> listCompetitionMatches_0()

Lista todos os jogos de uma competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; //Filtrar por fase (optional) (default to undefined)
let onlyOurMatches: boolean; //Apenas nossos jogos (optional) (default to false)
let statusFilter: string; //Filtrar por status (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionMatches_0(
    competitionId,
    phaseId,
    onlyOurMatches,
    statusFilter,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] | Filtrar por fase | (optional) defaults to undefined|
| **onlyOurMatches** | [**boolean**] | Apenas nossos jogos | (optional) defaults to false|
| **statusFilter** | [**string**] | Filtrar por status | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionMatchResponse>**

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

# **listCompetitionPhases**
> Array<CompetitionPhaseResponse> listCompetitionPhases()

Lista todas as fases de uma competição ordenadas por order_index.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionPhases(
    competitionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionPhaseResponse>**

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

# **listCompetitionPhases_0**
> Array<CompetitionPhaseResponse> listCompetitionPhases_0()

Lista todas as fases de uma competição ordenadas por order_index.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listCompetitionPhases_0(
    competitionId,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionPhaseResponse>**

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

# **listOpponentTeams**
> Array<CompetitionOpponentTeamResponse> listOpponentTeams()

Lista todas as equipes adversárias de uma competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let groupName: string; //Filtrar por grupo (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listOpponentTeams(
    competitionId,
    groupName,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **groupName** | [**string**] | Filtrar por grupo | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionOpponentTeamResponse>**

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

# **listOpponentTeams_0**
> Array<CompetitionOpponentTeamResponse> listOpponentTeams_0()

Lista todas as equipes adversárias de uma competição.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let groupName: string; //Filtrar por grupo (optional) (default to undefined)
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.listOpponentTeams_0(
    competitionId,
    groupName,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionId** | [**string**] |  | defaults to undefined|
| **groupName** | [**string**] | Filtrar por grupo | (optional) defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<CompetitionOpponentTeamResponse>**

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

# **parsePdfWithAI**
> AIParseResponse parsePdfWithAI(aIParseRequest)

Envia um PDF para o Gemini e extrai dados estruturados da competição.  O usuário deve validar os dados antes de salvar.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    AIParseRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let aIParseRequest: AIParseRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.parsePdfWithAI(
    aIParseRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIParseRequest** | **AIParseRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIParseResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dados extraídos com sucesso |  -  |
|**400** | PDF inválido ou erro de parsing |  -  |
|**401** | Unauthorized |  -  |
|**503** | Serviço Gemini indisponível |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **parsePdfWithAI_0**
> AIParseResponse parsePdfWithAI_0(aIParseRequest)

Envia um PDF para o Gemini e extrai dados estruturados da competição.  O usuário deve validar os dados antes de salvar.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    AIParseRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let aIParseRequest: AIParseRequest; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.parsePdfWithAI_0(
    aIParseRequest,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIParseRequest** | **AIParseRequest**|  | |
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AIParseResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dados extraídos com sucesso |  -  |
|**400** | PDF inválido ou erro de parsing |  -  |
|**401** | Unauthorized |  -  |
|**503** | Serviço Gemini indisponível |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateCompetitionPhase**
> CompetitionPhaseResponse updateCompetitionPhase(competitionPhaseUpdate)

Atualiza uma fase existente.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionPhaseUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; // (default to undefined)
let competitionPhaseUpdate: CompetitionPhaseUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCompetitionPhase(
    competitionId,
    phaseId,
    competitionPhaseUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionPhaseUpdate** | **CompetitionPhaseUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionPhaseResponse**

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

# **updateCompetitionPhase_0**
> CompetitionPhaseResponse updateCompetitionPhase_0(competitionPhaseUpdate)

Atualiza uma fase existente.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionPhaseUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let phaseId: string; // (default to undefined)
let competitionPhaseUpdate: CompetitionPhaseUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateCompetitionPhase_0(
    competitionId,
    phaseId,
    competitionPhaseUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionPhaseUpdate** | **CompetitionPhaseUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **phaseId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionPhaseResponse**

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

# **updateMatchResult**
> CompetitionMatchResponse updateMatchResult(competitionMatchResultUpdate)

Atualiza apenas o resultado do jogo. O trigger do banco atualiza automaticamente as estatísticas das equipes.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionMatchResultUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let competitionMatchResultUpdate: CompetitionMatchResultUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateMatchResult(
    competitionId,
    matchId,
    competitionMatchResultUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionMatchResultUpdate** | **CompetitionMatchResultUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionMatchResponse**

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

# **updateMatchResult_0**
> CompetitionMatchResponse updateMatchResult_0(competitionMatchResultUpdate)

Atualiza apenas o resultado do jogo. O trigger do banco atualiza automaticamente as estatísticas das equipes.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionMatchResultUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let matchId: string; // (default to undefined)
let competitionMatchResultUpdate: CompetitionMatchResultUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateMatchResult_0(
    competitionId,
    matchId,
    competitionMatchResultUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionMatchResultUpdate** | **CompetitionMatchResultUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **matchId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionMatchResponse**

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

# **updateOpponentTeam**
> CompetitionOpponentTeamResponse updateOpponentTeam(competitionOpponentTeamUpdate)

Atualiza uma equipe adversária.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionOpponentTeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let teamId: string; // (default to undefined)
let competitionOpponentTeamUpdate: CompetitionOpponentTeamUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateOpponentTeam(
    competitionId,
    teamId,
    competitionOpponentTeamUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionOpponentTeamUpdate** | **CompetitionOpponentTeamUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **teamId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionOpponentTeamResponse**

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

# **updateOpponentTeam_0**
> CompetitionOpponentTeamResponse updateOpponentTeam_0(competitionOpponentTeamUpdate)

Atualiza uma equipe adversária.

### Example

```typescript
import {
    CompetitionsV2Api,
    Configuration,
    CompetitionOpponentTeamUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new CompetitionsV2Api(configuration);

let competitionId: string; // (default to undefined)
let teamId: string; // (default to undefined)
let competitionOpponentTeamUpdate: CompetitionOpponentTeamUpdate; //
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.updateOpponentTeam_0(
    competitionId,
    teamId,
    competitionOpponentTeamUpdate,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **competitionOpponentTeamUpdate** | **CompetitionOpponentTeamUpdate**|  | |
| **competitionId** | [**string**] |  | defaults to undefined|
| **teamId** | [**string**] |  | defaults to undefined|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**CompetitionOpponentTeamResponse**

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

