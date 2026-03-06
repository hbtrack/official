# AppSchemasAttendanceAthleteNested

Dados básicos do atleta para response nested.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | ID do atleta | [default to undefined]
**athlete_name** | **string** | Nome do atleta | [default to undefined]
**athlete_nickname** | **string** |  | [optional] [default to undefined]
**shirt_number** | **number** |  | [optional] [default to undefined]
**state** | **string** | Estado do atleta | [optional] [default to 'ativa']

## Example

```typescript
import { AppSchemasAttendanceAthleteNested } from './api';

const instance: AppSchemasAttendanceAthleteNested = {
    id,
    athlete_name,
    athlete_nickname,
    shirt_number,
    state,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
