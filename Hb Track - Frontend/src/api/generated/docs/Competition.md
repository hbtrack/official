# Competition

Schema de resposta completo para competição.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID único da competição | [default to undefined]
**organization_id** | **string** | ID da organização | [default to undefined]
**name** | **string** | Nome da competição | [default to undefined]
**kind** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Data/hora de criação | [default to undefined]
**updated_at** | **string** | Data/hora da última atualização | [default to undefined]

## Example

```typescript
import { Competition } from './api';

const instance: Competition = {
    id,
    organization_id,
    name,
    kind,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
