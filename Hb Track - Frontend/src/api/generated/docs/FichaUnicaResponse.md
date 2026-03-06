# FichaUnicaResponse

Resposta da criação via Ficha Única

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** |  | [default to undefined]
**message** | **string** |  | [default to undefined]
**person_id** | **string** |  | [optional] [default to undefined]
**user_id** | **string** |  | [optional] [default to undefined]
**season_id** | **string** |  | [optional] [default to undefined]
**organization_id** | **string** |  | [optional] [default to undefined]
**team_id** | **string** |  | [optional] [default to undefined]
**athlete_id** | **string** |  | [optional] [default to undefined]
**team_registration_id** | **string** |  | [optional] [default to undefined]
**org_membership_id** | **string** |  | [optional] [default to undefined]
**user_created** | **boolean** |  | [optional] [default to false]
**season_created** | **boolean** |  | [optional] [default to false]
**organization_created** | **boolean** |  | [optional] [default to false]
**team_created** | **boolean** |  | [optional] [default to false]
**athlete_created** | **boolean** |  | [optional] [default to false]
**email_sent** | **boolean** |  | [optional] [default to false]
**validation_only** | **boolean** |  | [optional] [default to false]
**validation_errors** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { FichaUnicaResponse } from './api';

const instance: FichaUnicaResponse = {
    success,
    message,
    person_id,
    user_id,
    season_id,
    organization_id,
    team_id,
    athlete_id,
    team_registration_id,
    org_membership_id,
    user_created,
    season_created,
    organization_created,
    team_created,
    athlete_created,
    email_sent,
    validation_only,
    validation_errors,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
