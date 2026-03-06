# ContentTranslationMacro

Mapeamento de foco de treino → eficiência de jogo para um macroblock.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**training_focus_pct** | **number** | % total de foco no treino para este macroblock | [default to undefined]
**game_efficiency** | **number** |  | [optional] [default to undefined]
**focus_breakdown** | [**FocusBreakdown**](FocusBreakdown.md) |  | [optional] [default to undefined]

## Example

```typescript
import { ContentTranslationMacro } from './api';

const instance: ContentTranslationMacro = {
    training_focus_pct,
    game_efficiency,
    focus_breakdown,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
