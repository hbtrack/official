# RegistrationCreate

Vínculo atleta-equipe (team_registrations).  Só processado se athlete.create=True e team selecionada/criada.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **string** |  | [optional] [default to undefined]
**start_at** | **string** |  | [optional] [default to undefined]
**end_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { RegistrationCreate } from './api';

const instance: RegistrationCreate = {
    team_id,
    start_at,
    end_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
