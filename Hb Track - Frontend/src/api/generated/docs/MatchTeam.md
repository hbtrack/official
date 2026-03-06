# MatchTeam

Schema de resposta completo para match_team. Campos conforme banco: id, match_id, team_id, is_home, is_our_team

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID único do match_team | [default to undefined]
**match_id** | **string** | ID do jogo | [default to undefined]
**team_id** | **string** | ID da equipe | [default to undefined]
**is_home** | **boolean** | True &#x3D; mandante, False &#x3D; visitante | [default to undefined]
**is_our_team** | **boolean** | True &#x3D; nossa equipe | [default to undefined]

## Example

```typescript
import { MatchTeam } from './api';

const instance: MatchTeam = {
    id,
    match_id,
    team_id,
    is_home,
    is_our_team,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
