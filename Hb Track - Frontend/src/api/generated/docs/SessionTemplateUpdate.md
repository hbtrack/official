# SessionTemplateUpdate

Schema para atualizar template (campos opcionais)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**icon** | **string** |  | [optional] [default to undefined]
**focus_attack_positional_pct** | **number** |  | [optional] [default to undefined]
**focus_defense_positional_pct** | **number** |  | [optional] [default to undefined]
**focus_transition_offense_pct** | **number** |  | [optional] [default to undefined]
**focus_transition_defense_pct** | **number** |  | [optional] [default to undefined]
**focus_attack_technical_pct** | **number** |  | [optional] [default to undefined]
**focus_defense_technical_pct** | **number** |  | [optional] [default to undefined]
**focus_physical_pct** | **number** |  | [optional] [default to undefined]
**is_favorite** | **boolean** |  | [optional] [default to undefined]
**is_active** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { SessionTemplateUpdate } from './api';

const instance: SessionTemplateUpdate = {
    name,
    description,
    icon,
    focus_attack_positional_pct,
    focus_defense_positional_pct,
    focus_transition_offense_pct,
    focus_transition_defense_pct,
    focus_attack_technical_pct,
    focus_defense_technical_pct,
    focus_physical_pct,
    is_favorite,
    is_active,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
