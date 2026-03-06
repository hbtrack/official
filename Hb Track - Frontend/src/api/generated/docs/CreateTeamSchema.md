# CreateTeamSchema

Dados para criar nova equipe

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**category_id** | **number** |  | [default to undefined]
**gender** | [**Gender**](Gender.md) |  | [default to undefined]

## Example

```typescript
import { CreateTeamSchema } from './api';

const instance: CreateTeamSchema = {
    name,
    category_id,
    gender,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
