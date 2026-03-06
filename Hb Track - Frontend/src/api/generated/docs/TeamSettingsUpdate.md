# TeamSettingsUpdate

Payload para atualização de configurações da equipe (Step 15).  Configura threshold de alertas automáticos para o sistema de wellness.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alert_threshold_multiplier** | **number** | Multiplicador de threshold para alertas (1.0-3.0). Valores sugeridos: 1.5 (juvenis sensíveis), 2.0 (adultos padrão), 2.5 (adultos tolerantes) | [default to undefined]

## Example

```typescript
import { TeamSettingsUpdate } from './api';

const instance: TeamSettingsUpdate = {
    alert_threshold_multiplier,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
