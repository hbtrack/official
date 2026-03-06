# MatchTeamCreate

Schema para adicionar equipe ao jogo (POST).  Campos obrigatórios: - team_id: UUID da equipe - is_home: boolean (true = mandante, false = visitante) - is_our_team: boolean (true = nossa equipe)  Constraints (banco): - UNIQUE (match_id, team_id)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** | ID da equipe (obrigatório) | [default to undefined]
**is_home** | **boolean** | True &#x3D; mandante, False &#x3D; visitante (obrigatório) | [default to undefined]
**is_our_team** | **boolean** | True &#x3D; nossa equipe (obrigatório) | [default to undefined]

## Example

```typescript
import { MatchTeamCreate } from './api';

const instance: MatchTeamCreate = {
    team_id,
    is_home,
    is_our_team,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
