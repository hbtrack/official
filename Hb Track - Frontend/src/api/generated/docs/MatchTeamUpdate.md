# MatchTeamUpdate

Schema para atualizar equipe do jogo (PATCH).  Campos editáveis: - is_home: Lado da equipe (pode trocar mandante/visitante) - is_our_team: Se é nossa equipe  Campos NÃO editáveis: - team_id (imutável) - match_id (imutável)  Regras: RDB13/RF15 - Bloquear se jogo finalizado

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_home** | **boolean** |  | [optional] [default to undefined]
**is_our_team** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { MatchTeamUpdate } from './api';

const instance: MatchTeamUpdate = {
    is_home,
    is_our_team,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
