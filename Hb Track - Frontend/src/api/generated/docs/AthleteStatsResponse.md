# AthleteStatsResponse

Estatísticas de atletas para dashboard (FASE 2 - FLUXO_GERENCIAMENTO_ATLETAS.md).  KPIs: - Total de atletas - Em captação (sem team_registration ativo) - Lesionadas (injured=true) - Suspensas (suspended_until >= hoje) - Por estado (ativa, dispensada, arquivada) - Por categoria

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total** | **number** | Total de atletas | [default to undefined]
**em_captacao** | **number** | Atletas sem equipe (fase captação/avaliação) | [default to undefined]
**lesionadas** | **number** | Atletas com flag injured&#x3D;true | [default to undefined]
**suspensas** | **number** | Atletas com suspensão ativa | [default to undefined]
**ativas** | **number** | Atletas no estado ativa | [default to undefined]
**dispensadas** | **number** | Atletas dispensadas | [default to undefined]
**arquivadas** | **number** | Atletas arquivadas | [default to undefined]
**com_restricao_medica** | **number** | Atletas com restrição médica | [default to undefined]
**carga_restrita** | **number** | Atletas com carga restrita | [default to undefined]
**por_categoria** | **{ [key: string]: any; }** | Contagem por categoria (categoria_name: count) | [optional] [default to undefined]

## Example

```typescript
import { AthleteStatsResponse } from './api';

const instance: AthleteStatsResponse = {
    total,
    em_captacao,
    lesionadas,
    suspensas,
    ativas,
    dispensadas,
    arquivadas,
    com_restricao_medica,
    carga_restrita,
    por_categoria,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
