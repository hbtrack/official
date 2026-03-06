# LgpdApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**exportAthleteDataApiV1AthletesMeExportDataGet**](#exportathletedataapiv1athletesmeexportdataget) | **GET** /api/v1/athletes/me/export-data | Exportar Dados Pessoais (LGPD)|

# **exportAthleteDataApiV1AthletesMeExportDataGet**
> any exportAthleteDataApiV1AthletesMeExportDataGet()

Exporta todos os dados pessoais do atleta conforme LGPD Art. 18.          **Formatos disponíveis:**     - `json`: Retorna JSON direto no response     - `csv`: Retorna ZIP com múltiplos CSVs (download)          **Dados incluídos:**     - Informações pessoais (nome, data nascimento, posição, etc)     - Wellness pré-treino (todas entradas)     - Wellness pós-treino (todas entradas)     - Presenças em treinos     - Histórico médico (casos registrados)     - Badges conquistados          **NÃO inclui:**     - Logs de acesso (data_access_logs)     - Dados de outros atletas     - Informações de equipes/organizações          **Segurança:**     - Apenas o próprio atleta pode exportar seus dados     - Registra exportação em audit_logs     - Rate limiting futuro: 3 exports/dia          **Compliance:**     - LGPD Art. 18, II - Direito à portabilidade     - Dados em formato estruturado (JSON/CSV)     - Gerado em até 5 segundos

### Example

```typescript
import {
    LgpdApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new LgpdApi(configuration);

let format: string; //Formato do export: \'json\' ou \'csv\' (optional) (default to 'json')
let xRequestID: string; // (optional) (default to undefined)
let xOrganizationId: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.exportAthleteDataApiV1AthletesMeExportDataGet(
    format,
    xRequestID,
    xOrganizationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **format** | [**string**] | Formato do export: \&#39;json\&#39; ou \&#39;csv\&#39; | (optional) defaults to 'json'|
| **xRequestID** | [**string**] |  | (optional) defaults to undefined|
| **xOrganizationId** | [**string**] |  | (optional) defaults to undefined|


### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/zip


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dados exportados com sucesso |  -  |
|**400** | Formato inválido ou usuário não é atleta |  -  |
|**401** | Não autenticado |  -  |
|**404** | Atleta não encontrado |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

