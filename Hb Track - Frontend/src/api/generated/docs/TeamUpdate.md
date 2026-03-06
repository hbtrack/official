# TeamUpdate

Payload para atualização de equipe.  Regras: - RF7: Pode alterar coach_membership_id

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**category_id** | **number** |  | [optional] [default to undefined]
**coach_membership_id** | **string** |  | [optional] [default to undefined]
**is_active** | **boolean** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamUpdate } from './api';

const instance: TeamUpdate = {
    name,
    category_id,
    coach_membership_id,
    is_active,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
