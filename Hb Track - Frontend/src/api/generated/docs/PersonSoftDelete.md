# PersonSoftDelete

Schema para soft delete de Person e entidades relacionadas  Referências RAG: - RDB4: deleted_reason obrigatório quando deleted_at não é null

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted_reason** | **string** | Motivo da exclusão (RDB4 - obrigatório) | [default to undefined]

## Example

```typescript
import { PersonSoftDelete } from './api';

const instance: PersonSoftDelete = {
    deleted_reason,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
