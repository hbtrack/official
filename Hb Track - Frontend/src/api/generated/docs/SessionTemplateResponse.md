# SessionTemplateResponse

Schema de resposta com todos os campos

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**focus_attack_positional_pct** | **number** | Ataque Posicional (%) | [optional] [default to 0]
**focus_defense_positional_pct** | **number** | Defesa Posicional (%) | [optional] [default to 0]
**focus_transition_offense_pct** | **number** | Transição Ofensiva (%) | [optional] [default to 0]
**focus_transition_defense_pct** | **number** | Transição Defensiva (%) | [optional] [default to 0]
**focus_attack_technical_pct** | **number** | Técnica Ofensiva (%) | [optional] [default to 0]
**focus_defense_technical_pct** | **number** | Técnica Defensiva (%) | [optional] [default to 0]
**focus_physical_pct** | **number** | Físico (%) | [optional] [default to 0]
**created_at** | **string** | Data de criação (UTC) | [default to undefined]
**updated_at** | **string** | Data da última atualização (UTC) | [default to undefined]
**id** | **string** |  | [default to undefined]
**org_id** | **string** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**description** | **string** |  | [default to undefined]
**icon** | **string** |  | [default to undefined]
**is_favorite** | **boolean** |  | [default to undefined]
**is_active** | **boolean** |  | [default to undefined]
**created_by_membership_id** | **string** |  | [default to undefined]

## Example

```typescript
import { SessionTemplateResponse } from './api';

const instance: SessionTemplateResponse = {
    focus_attack_positional_pct,
    focus_defense_positional_pct,
    focus_transition_offense_pct,
    focus_transition_defense_pct,
    focus_attack_technical_pct,
    focus_defense_technical_pct,
    focus_physical_pct,
    created_at,
    updated_at,
    id,
    org_id,
    name,
    description,
    icon,
    is_favorite,
    is_active,
    created_by_membership_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
