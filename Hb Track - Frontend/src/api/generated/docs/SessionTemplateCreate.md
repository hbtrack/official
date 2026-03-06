# SessionTemplateCreate

Schema para criar template

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
**name** | **string** | Nome do template | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**icon** | **string** | Ícone do template | [optional] [default to 'target']
**is_favorite** | **boolean** | Marcar como favorito | [optional] [default to false]

## Example

```typescript
import { SessionTemplateCreate } from './api';

const instance: SessionTemplateCreate = {
    focus_attack_positional_pct,
    focus_defense_positional_pct,
    focus_transition_offense_pct,
    focus_transition_defense_pct,
    focus_attack_technical_pct,
    focus_defense_technical_pct,
    focus_physical_pct,
    name,
    description,
    icon,
    is_favorite,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
