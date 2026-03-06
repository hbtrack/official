# CoachHistoryItem

Item de histórico de coaches (Step 19).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID do team_membership | [default to undefined]
**person_id** | **string** | ID da pessoa | [default to undefined]
**person_name** | **string** | Nome completo do coach | [default to undefined]
**start_at** | **string** | Data de início | [default to undefined]
**end_at** | **string** |  | [optional] [default to undefined]
**is_current** | **boolean** | Se é o coach atual | [default to undefined]

## Example

```typescript
import { CoachHistoryItem } from './api';

const instance: CoachHistoryItem = {
    id,
    person_id,
    person_name,
    start_at,
    end_at,
    is_current,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
