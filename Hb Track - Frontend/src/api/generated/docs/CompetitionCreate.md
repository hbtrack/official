# CompetitionCreate

Schema para criação de competição (POST).  Campos obrigatórios: - name: Nome da competição  Campo kind: Texto livre. Exemplos: \"official\", \"friendly\", \"training-game\"  NOTA: organization_id é obtido automaticamente do contexto de autenticação (R34)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Nome da competição (obrigatório) | [default to undefined]
**kind** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionCreate } from './api';

const instance: CompetitionCreate = {
    name,
    kind,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
