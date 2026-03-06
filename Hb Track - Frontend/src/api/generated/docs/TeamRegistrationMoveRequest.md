# TeamRegistrationMoveRequest

Payload para mover atleta para outra equipe.  - Encerra inscricoes ativas na temporada (RDB10) - Cria nova inscricao na equipe alvo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**athlete_id** | **string** | ID do atleta | [default to undefined]
**start_at** | **string** |  | [optional] [default to undefined]
**end_previous_at** | **string** |  | [optional] [default to undefined]
**role** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamRegistrationMoveRequest } from './api';

const instance: TeamRegistrationMoveRequest = {
    athlete_id,
    start_at,
    end_previous_at,
    role,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
