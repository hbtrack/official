# TeamStaffMember

Membro do staff de uma equipe.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID do org_membership | [default to undefined]
**person_id** | **string** | ID da pessoa | [default to undefined]
**full_name** | **string** | Nome completo | [default to undefined]
**role** | **string** | Papel: treinador, etc | [default to undefined]
**start_at** | **string** |  | [optional] [default to undefined]
**end_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { TeamStaffMember } from './api';

const instance: TeamStaffMember = {
    id,
    person_id,
    full_name,
    role,
    start_at,
    end_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
