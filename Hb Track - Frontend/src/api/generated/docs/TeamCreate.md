# TeamCreate

Payload para criação de equipe (RF6).  Regras: - RF6: Equipe pertence a uma organização - UNIQUE(organization_id, category_id, name)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Nome da equipe | [default to undefined]
**category_id** | **number** | ID da categoria (obrigatório) | [default to undefined]
**gender** | **string** | Gênero: \&#39;masculino\&#39; ou \&#39;feminino\&#39; | [default to undefined]
**is_our_team** | **boolean** | Se é nossa equipe ou adversário | [optional] [default to true]
**season_id** | **string** |  | [optional] [default to undefined]
**coach_membership_id** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamCreate } from './api';

const instance: TeamCreate = {
    name,
    category_id,
    gender,
    is_our_team,
    season_id,
    coach_membership_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
