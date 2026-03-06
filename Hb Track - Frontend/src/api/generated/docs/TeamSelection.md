# TeamSelection

Seleção de equipe.  mode=\'select\': usar team_id existente mode=\'create\': criar nova equipe

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mode** | **string** |  | [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**category_id** | **number** |  | [optional] [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**organization_id** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamSelection } from './api';

const instance: TeamSelection = {
    mode,
    team_id,
    name,
    category_id,
    gender,
    organization_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
