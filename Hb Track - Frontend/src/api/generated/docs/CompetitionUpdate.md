# CompetitionUpdate

Schema para atualização de competição (PATCH).  Campos editáveis: - name: Nome da competição - kind: Tipo da competição  Campos NÃO editáveis (omitidos): - organization_id (imutável após criação)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**kind** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CompetitionUpdate } from './api';

const instance: CompetitionUpdate = {
    name,
    kind,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
