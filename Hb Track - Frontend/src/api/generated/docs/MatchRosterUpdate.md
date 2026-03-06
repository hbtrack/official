# MatchRosterUpdate

Schema para atualizar roster entry (PATCH).  Campos editáveis: - jersey_number: número da camisa - is_starting: se é titular - is_goalkeeper: se é goleira - is_available: se está disponível - notes: observações  Campos NÃO editáveis: - athlete_id (imutável) - match_id (imutável) - team_id (imutável)  Regras: RDB13/RF15 - Bloquear se jogo finalizado

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**jersey_number** | **number** |  | [optional] [default to undefined]
**is_starting** | **boolean** |  | [optional] [default to undefined]
**is_goalkeeper** | **boolean** |  | [optional] [default to undefined]
**is_available** | **boolean** |  | [optional] [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { MatchRosterUpdate } from './api';

const instance: MatchRosterUpdate = {
    jersey_number,
    is_starting,
    is_goalkeeper,
    is_available,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
