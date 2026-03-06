# MatchRoster

Schema de resposta completo para match_roster. Campos conforme banco: id, match_id, team_id, athlete_id, jersey_number,                       is_starting, is_goalkeeper, is_available, notes  Regras relacionadas: - RD4/RD7: Participação oficial exige inscrição na temporada - RD18: Limite máximo de 16 atletas por jogo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID único do match_roster | [default to undefined]
**match_id** | **string** | ID do jogo | [default to undefined]
**team_id** | **string** | ID da equipe | [default to undefined]
**athlete_id** | **string** | ID da atleta | [default to undefined]
**jersey_number** | **number** | Número da camisa | [default to undefined]
**is_starting** | **boolean** |  | [optional] [default to undefined]
**is_goalkeeper** | **boolean** | Indica se é goleira | [default to undefined]
**is_available** | **boolean** | Indica se está disponível | [default to undefined]
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { MatchRoster } from './api';

const instance: MatchRoster = {
    id,
    match_id,
    team_id,
    athlete_id,
    jersey_number,
    is_starting,
    is_goalkeeper,
    is_available,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
